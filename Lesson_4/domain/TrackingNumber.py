from abc import ABC, abstractmethod
from typing import Annotated, Optional, List
from pydantic import BaseModel, Field, StringConstraints, field_validator
import pandas as pd

# ==========================================
# 🎯 1. มาตรฐานข้อมูลกลาง (DRY - Type Aliases)
# ==========================================
StrippedStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
UpperStr = Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=3, max_length=3)]


# ==========================================
# 📦 2. Value Objects
# ==========================================
class TrackingNumber(BaseModel):
    value: StrippedStr
    @field_validator('value')
    @classmethod
    def check_length(cls, v):
        if len(v) < 5: raise ValueError('Tracking Number สั้นเกินไป')
        return v

class TicketId(BaseModel):
    value: StrippedStr

class Money(BaseModel):
    amount: float = Field(..., ge=0)
    currency: UpperStr

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f'Cannot add different currencies: {self.currency} and {other.currency}')
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __str__(self):
        return f'{self.amount:,.2f} {self.currency}'


# ==========================================
# 🏛️ 3. Entities & Aggregates
# ==========================================
class ClaimTicket(BaseModel):
    ticket_id: TicketId
    tracking_number: TrackingNumber
    compensation_amount: Money
    version: int = Field(default=1)

    def update_compensation(self, new_money: Money):
        self.compensation_amount = new_money
        self.version += 1

class ClaimCase(BaseModel):
    tracking_number: TrackingNumber
    tickets: list[ClaimTicket] = Field(default_factory=list)
    total_compensation: Money = Field(default_factory=lambda: Money(amount=0, currency="THB"))

    def add_ticket(self, ticket: ClaimTicket):
        if ticket.tracking_number.value != self.tracking_number.value:
            raise ValueError("ป๋าครับ! ใบเคลมคนละเลข Tracking กันนะ")
        self.tickets.append(ticket)
        new_amount = self.total_compensation.amount + ticket.compensation_amount.amount
        self.total_compensation = Money(amount=new_amount, currency="THB")


# ==========================================
# 🗄️ 4. Repositories (ใช้ ABC เข้มงวด 100%)
# ==========================================
class ClaimRepository(ABC):
    @abstractmethod
    def save(self, claim_case: ClaimCase):
        pass # เป็นแค่พิมพ์เขียว ไม่ต้องมีโค้ดการทำงาน
        
    @abstractmethod
    def get_by_tracking(self, tracking: TrackingNumber) -> Optional[ClaimCase]:
        pass

    @abstractmethod
    def get_all_cases(self) -> List[ClaimCase]:
        pass

# --- ลูกคนที่ 1: InMemory ---
class InMemoryClaimRepository(ClaimRepository):
    def __init__(self):
        self._db = {} 

    def save(self, claim_case: ClaimCase):
        self._db[claim_case.tracking_number.value] = claim_case

    def get_by_tracking(self, tracking: TrackingNumber) -> Optional[ClaimCase]:
        return self._db.get(tracking.value)

    def get_all_cases(self) -> List[ClaimCase]:
        return list(self._db.values())

# --- ลูกคนที่ 2: Pandas ---
class PandasClaimRepository(ClaimRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_all_cases(self) -> List[ClaimCase]:
        df = pd.read_excel(self.file_path)
        all_cases = {}
        
        for _, row in df.iterrows():
            tn = TrackingNumber(value=str(row['tracking_no']))
            tid = TicketId(value=str(row['complaint_ticket_id']))
            amount = row.get('compensation_final_amt', 0)
            if pd.isna(amount): amount = 0
            
            money = Money(amount=float(amount), currency="THB")
            ticket = ClaimTicket(ticket_id=tid, tracking_number=tn, compensation_amount=money)
            
            if tn.value not in all_cases:
                all_cases[tn.value] = ClaimCase(tracking_number=tn)
            all_cases[tn.value].add_ticket(ticket)
            
        return list(all_cases.values())

    def get_by_tracking(self, tracking: TrackingNumber) -> Optional[ClaimCase]:
        # ค้นหาจากเคสทั้งหมด
        all_cases = self.get_all_cases()
        for case in all_cases:
            if case.tracking_number.value == tracking.value:
                return case
        return None

    def save(self, claim_case: ClaimCase):
        # ดักไว้ชัดเจนว่า Pandas ทำงานแบบ Read-Only สำหรับตอนนี้
        raise NotImplementedError("PandasClaimRepository ออกแบบมาให้อ่านอย่างเดียวครับป๋า!")


# ==========================================
# 🧠 5. Domain Services
# ==========================================
class ClaimEnrichmentService:
    def enrich(self, claim_case: ClaimCase, compensation_map: dict[str, Money]):
        tracking_val = claim_case.tracking_number.value
        
        if tracking_val in compensation_map:
            real_money = compensation_map[tracking_val]
            for ticket in claim_case.tickets:
                ticket.compensation_amount = real_money
            
            new_amt = sum(t.compensation_amount.amount for t in claim_case.tickets)
            claim_case.total_compensation = Money(amount=new_amt, currency="THB")
            print(f"✨ เติมเงินให้ {tracking_val} สำเร็จ: {real_money}")


# ==========================================
# 🧪 6. การรันใช้งานจริง (Main Execution)
# ==========================================
if __name__ == "__main__":
    print("=== ทดสอบ Value Objects ===")
    good_track = TrackingNumber(value='  TH1234567890  ') # ลองเว้นวรรค
    print(f'สำเร็จ: ได้รับพัสดุ {good_track.value}') # ผลลัพธ์ต้องไม่มีเว้นวรรค

    try:
        bad_track = TrackingNumber(value='TH12')
    except ValueError as e:
        print(f'โดนดัก error: {e}')

    try:
        claim_money = Money(amount=1477.50, currency=' thb ') # ลองเว้นวรรค + ตัวเล็ก
        print(f'สร้างสำเร็จ: {claim_money}') # ผลลัพธ์ต้องเป็นตัวใหญ่และไม่มีเว้นวรรค
        
        fake_money = Money(amount=-50, currency='usd')
    except Exception as e:
        print(f'ระบบดักจับเงินติดลบได้: {e}')

    print("\n=== ทดสอบ Entity & Aggregate ===")
    tn = TrackingNumber(value="TH1234567890")
    my_case = ClaimCase(tracking_number=tn)

    t1 = ClaimTicket(ticket_id=TicketId(value="CMP-01"), tracking_number=tn, compensation_amount=Money(amount=100, currency="THB"))
    my_case.add_ticket(t1)

    t2 = ClaimTicket(ticket_id=TicketId(value="CMP-02"), tracking_number=tn, compensation_amount=Money(amount=200, currency="THB"))
    my_case.add_ticket(t2)

    print("\n=== ทดสอบ Repository ===")
    repo = InMemoryClaimRepository()
    repo.save(my_case)
    result = repo.get_by_tracking(TrackingNumber(value="TH1234567890"))
    print(f"ยอดรวมในระบบตอนนี้: {result.total_compensation}")

    pd_repo = PandasClaimRepository(r'..\Lesson_4\mock_claim_data.xlsx')
    pd_repo.save(r'..\Lesson_4\mock_claim_data.xlsx')
    