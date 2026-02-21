from pydantic import BaseModel, Field, field_validator

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