from pydantic import BaseModel, Field, field_validator
import pandas as pd


class TrackingNumber(BaseModel):

    value: str = Field(..., min_length=1, json_schema_extra={'strip_whitespace': True})

    @field_validator('value')
    def check_length(cls, v):
        if len(v) < 5:
            raise ValueError('Tracking Number สั้นเกินไป')
        return v.strip()
    

class Money(BaseModel):

    amount: float = Field(..., ge=0)
    currency: str = Field(..., min_length=3, max_length=3)

    @field_validator('currency')
    def currency_must_be_uppercase(cls, v):
        return v.upper()
    
    def __str__(self):
        return f'{self.amount:,.2f} {self.currency}'
    

class TicketId(BaseModel):
    value: str = Field(..., min_length=1)

class ClaimTicket(BaseModel):
    """
    Entity: ใบเคลมสินค้า
    ทำหน้าที่รวบรวมข้อมูลการเคลมและควบคุมกฎธุรกิจ
    """
    ticket_id: TicketId
    tracking_number: TrackingNumber
    compensation_amount: Money

    version: int = Field(default=1)

    # Logic ธุรกิจ: การอัปเดตยอดเงินเคลม
    def update_compensation(self, new_money: Money):
        """
        กฎ: การอัปเดตยอดเงิน ต้องเพิ่มเลขเวอร์ชันเสมอ
        """
        self.compensation_amount = new_money
        self.version += 1
        print(f'อัพเดทยอดเงินเป็น {new_money} (version: {self.version})')


class ClaimCase(BaseModel):
    """
    Aggregate Root: ตระกร้าคุมใบเคลมของสินค้า 1 ชิ้น
    """
    tracking_number: TrackingNumber
    # รายการใบเคลมที่อยู่ในตระกร้านี้ (เริ่มต้นเป็น List ว่าง)
    tickets: list[ClaimTicket] = Field(default_factory=list)
    
    # สถานะเงินรวม (Value Object ที่ป๋าทำไว้)
    # เริ่มต้นที่ 0 THB
    total_compensation: Money = Field(
        default_factory=lambda: Money(amount=0, currency="THB")
    )

    def add_ticket(self, ticket: ClaimTicket):
        """
        กฎธุรกิจ: 
        1. ตรวจสอบว่า Tracking ตรงกันไหม
        2. เพิ่มลง List
        3. อัปเดตยอดเงินรวม
        """
        # เช็กกฎ Invariant: ห้ามเอาใบเคลมคนละสินค้ามาปนกัน
        if ticket.tracking_number.value != self.tracking_number.value:
            raise ValueError("ป๋าครับ! ใบเคลมนี้มันคนละเลข Tracking กันนะ")

        self.tickets.append(ticket)
        
        # อัปเดตยอดรวม (ป๋าเห็นไหมครับ เราเอา Value Object มาคำนวณกันในนี้เลย)
        new_amount = self.total_compensation.amount + ticket.compensation_amount.amount
        self.total_compensation = Money(amount=new_amount, currency="THB")
        
        print(f"✅ เพิ่ม {ticket.ticket_id.value} สำเร็จ! ยอดรวมเคสนี้: {self.total_compensation}")


from typing import Optional

# นี่คือ "หน้าตา" ของลิ้นชักที่ระบบเราต้องการ (Interface)
class ClaimRepository:
    def save(self, claim_case: ClaimCase):
        raise NotImplementedError
        
    def get_by_tracking(self, tracking: TrackingNumber) -> Optional[ClaimCase]:
        raise NotImplementedError

# นี่คือ "ลิ้นชักของปลอม" ที่เอาไว้ใช้รันเทสให้ไวปรู๊ดปร๊าด (In-Memory)
class InMemoryClaimRepository(ClaimRepository):
    def __init__(self):
        # ใช้ Dictionary ของ Python เป็นฐานข้อมูลจำลองไปก่อน
        self._db = {} 

    def save(self, claim_case: ClaimCase):
        # เอาเลข Tracking เป็น Key และเอา Aggregate ทั้งก้อนเป็น Value
        self._db[claim_case.tracking_number.value] = claim_case
        print(f"💾 [DB จำลอง] บันทึกเคสของพัสดุ {claim_case.tracking_number.value} ลงลิ้นชักเรียบร้อย!")

    def get_by_tracking(self, tracking: TrackingNumber) -> Optional[ClaimCase]:
        # ค้นหาใน Dictionary
        found_case = self._db.get(tracking.value)
        if found_case:
            print(f"🔍 [DB จำลอง] ค้นพบเคสของพัสดุ {tracking.value}")
        else:
            print(f"❌ [DB จำลอง] ไม่พบพัสดุ {tracking.value} ในระบบ")
        return found_case


class PandasClaimRepository(ClaimRepository): # สืบทอดมาจากพิมพ์เขียวลิ้นชัก
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_all_cases(self) -> list[ClaimCase]:
        # 1. ใช้ Pandas อ่านไฟล์ (ทบทวนบทที่ 1)
        df = pd.read_excel(self.file_path)
        
        cases = []
        for index, row in df.iterrows():
            # 2. กระบวนการ "แปลงร่าง" (Transformation)
            # ป๋าดูนะครับ เราเอาข้อมูลดิบจาก row มาห่อด้วย Value Object ทันที!
            tn = TrackingNumber(value=row['tracking_no'])
            tid = TicketId(value=row['complaint_ticket_id'])
            
            # สมมติเราดึงราคามา (ถ้าไม่มีให้เป็น 0)
            amount = row.get('compensation_final_amt', 0)
            money = Money(amount=amount, currency="THB")

            # 3. สร้าง Entity และ Aggregate
            ticket = ClaimTicket(
                ticket_id=tid, 
                tracking_number=tn, 
                compensation_amount=money
            )
            
            # สร้างตระกร้า (Case) แล้วใส่ใบเคลมลงไป
            new_case = ClaimCase(tracking_number=tn)
            new_case.add_ticket(ticket)
            
            cases.append(new_case)
            
        return cases


class ClaimEnrichmentService:
    """
    Service สำหรับเติมข้อมูลยอดเงินชดเชยให้สมบูรณ์
    """
    def enrich(self, claim_case: ClaimCase, compensation_map: dict[str, Money]):
        # ดึงเลข Tracking จากแฟ้มเคสออกมา
        tracking_val = claim_case.tracking_number.value
        
        # ค้นหาในข้อมูลไฟล์ 2 (compensation_map)
        if tracking_val in compensation_map:
            real_money = compensation_map[tracking_val]
            
            # อัปเดตเงินในใบแจ้งทุกใบที่อยู่ในเคสนี้
            for ticket in claim_case.tickets:
                ticket.compensation_amount = real_money
            
            # สั่งให้ Aggregate คำนวณยอดรวมใหม่ (Logic อยู่ใน ClaimCase)
            # หมายเหตุ: ในที่นี้เราต้องเรียกเมธอดเพื่ออัปเดตสถานะเงินรวม
            new_amt = sum(t.compensation_amount.amount for t in claim_case.tickets)
            claim_case.total_compensation = Money(amount=new_amt, currency="THB")
            
            print(f"✨ เติมเงินให้ {tracking_val} สำเร็จ: {real_money}")
        else:
            print(f"⚠️ ไม่พบยอดเงินสำหรับ {tracking_val} ในข้อมูลไฟล์ 2")


if __name__ == "__main__":
    good_track = TrackingNumber(value='TH1234567890')
    print(f'สำเร็จ: ได้รับพัสดุ {good_track.value}')

    try:
        bad_track = TrackingNumber(value='TH12')
    except ValueError as e:
        print(f'โดนดัก error {e}')

    try:
        claim_money = Money(amount=1477.50, currency='thb')
        print(f'สร้างสำเร็จ: {claim_money}')
    
        fake_money = Money(amount=-50, currency='usd')
    except Exception as e:
        print(f'ระบบดักจับเงินติดลบได้ {e}')

    my_ticket = ClaimTicket(
        ticket_id=TicketId(value='CMP-1001'),
        tracking_number=TrackingNumber(value='TH1234567890'),
        compensation_amount=Money(amount=88.26, currency='THB')
    )

    print(f'ใบเคลมถูกสร้าง: {my_ticket.ticket_id.value} {my_ticket.version}')
    print(f'ยอดเดิม: {my_ticket.compensation_amount}')

    new_prict = Money(amount=950.00, currency='THB')
    my_ticket.update_compensation(new_prict)


    tn = TrackingNumber(value="TH1234567890")
    my_case = ClaimCase(tracking_number=tn)



    # ลองเพิ่มใบที่ 1
    t1 = ClaimTicket(ticket_id=TicketId(value="CMP-01"), tracking_number=tn, 
                     compensation_amount=Money(amount=100, currency="THB"))
    my_case.add_ticket(t1)

    # ลองเพิ่มใบที่ 2
    t2 = ClaimTicket(ticket_id=TicketId(value="CMP-02"), tracking_number=tn, 
                     compensation_amount=Money(amount=200, currency="THB"))
    my_case.add_ticket(t2)



    # --- ลองใช้งานจริง ---
    # สร้างลิ้นชัก
    repo = InMemoryClaimRepository()
    
    # สร้างข้อมูลและเซฟ
    tn1 = TrackingNumber(value="TH9999999999")
    case1 = ClaimCase(tracking_number=tn1)
    repo.save(case1)
    
    # ลองค้นหาดู
    result = repo.get_by_tracking(TrackingNumber(value="TH9999999999"))
    print(f"ยอดรวมในระบบตอนนี้: {result.total_compensation}")

    # --- ลองใช้งานกับไฟล์ของป๋า ---
    # repo = PandasClaimRepository(r"../Lesson_4/mock_claim_data.xlsx")
    # all_cases = repo.load_all_cases()