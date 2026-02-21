import pytest
from pydantic import ValidationError

# สมมติว่าเราเรียกใช้คลาสจากไฟล์ domain (ที่เรากำลังจะสร้าง)
from domain.TrackingNumber import TrackingNumber, Money, TicketId, ClaimTicket, ClaimCase

# -----------------------------------------
# Test Cases สำหรับ TrackingNumber
# -----------------------------------------

# เทสที่ 1: ใส่ข้อมูลถูกต้อง ต้องทำงานได้
def test_valid_tracking_number():
    # สมมติเราดึงรหัส TH1234567890 มาจากไฟล์ Excel ของป๋า
    tracking = TrackingNumber(value="TH1234567890")
    assert tracking.value == "TH1234567890"

# เทสที่ 2: ใส่ค่าว่าง ต้องพัง (Error)
def test_empty_tracking_number():
    with pytest.raises(ValidationError):
        TrackingNumber(value="") # ห้ามว่างเด็ดขาด

# เทสที่ 3: ใส่ประเภทผิด (เช่น ใส่ตัวเลข) ต้องพัง
def test_invalid_type_tracking_number():
    with pytest.raises(ValidationError):
        TrackingNumber(value=12345678) # ต้องเป็น String เท่านั้น

# -----------------------------------------
# Test Cases สำหรับ Money
# -----------------------------------------

def test_valid_money_creation():
    # จำลองค่าจากไฟล์ป๋า: 886.26 THB
    m = Money(amount=886.26, currency="THB")
    assert m.amount == 886.26
    assert m.currency == "THB"

def test_money_negative_amount():
    # กฎคือเงินเคลมต้องไม่ติดลบ ถ้าติดลบต้องพัง (Error)
    with pytest.raises(ValidationError):
        Money(amount=-100.0, currency="THB")

def test_money_invalid_currency_format():
    # สกุลเงินต้องมี 3 ตัวอักษรเท่านั้น (มาตรฐาน ISO)
    with pytest.raises(ValidationError):
        Money(amount=100.0, currency="THAI_BAHT")

def test_claim_ticket_creation():
    # 1. เตรียมชิ้นส่วน (Value Objects)
    tid = TicketId(value="CMP-1001")
    tn = TrackingNumber(value="TH1234567890")
    price = Money(amount=886.26, currency="THB")

        # 2. สร้าง Entity
    ticket = ClaimTicket(
        ticket_id=tid,
        tracking_number=tn,
        compensation_amount=price
    )

    assert ticket.ticket_id.value == "CMP-1001"
    assert ticket.version == 1  # เริ่มต้นต้องเป็นเวอร์ชัน 1


    # -----------------------------------------
# Test Cases สำหรับ ClaimCase (Aggregate)
# -----------------------------------------

def test_add_multiple_tickets_to_same_case():
    # 1. เตรียม Tracking เดียวกัน (กุญแจหลัก)
    tn = TrackingNumber(value="TH1234567890")
    
    # 2. สร้าง Aggregate Root (ตระกร้า)
    claim_case = ClaimCase(tracking_number=tn)

    # 3. เตรียมใบเคลม 2 ใบ (จำลองว่าแจ้งซ้ำ 2 ครั้ง)
    ticket1 = ClaimTicket(
        ticket_id=TicketId(value="CMP-1001"),
        tracking_number=tn,
        compensation_amount=Money(amount=500, currency="THB")
    )
    ticket2 = ClaimTicket(
        ticket_id=TicketId(value="CMP-1002"),
        tracking_number=tn,
        compensation_amount=Money(amount=300, currency="THB")
    )

    # 4. ใส่ใบเคลมลงในตระกร้า
    claim_case.add_ticket(ticket1)
    claim_case.add_ticket(ticket2)

    # 5. ตรวจสอบ: ในตระกร้าต้องมี 2 ใบ และยอดรวมต้องเป็น 800 บาท
    assert len(claim_case.tickets) == 2
    assert claim_case.total_compensation.amount == 800.0