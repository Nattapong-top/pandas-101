import pytest
from pydantic import ValidationError

# สมมติว่าเราเรียกใช้คลาสจากไฟล์ domain (ที่เรากำลังจะสร้าง)
from domain.TrackingNumber import TrackingNumber, Money, TicketId, ClaimTicket, ClaimCase
from domain.TrackingNumber import InMemoryClaimRepository, PandasClaimRepository
from domain.TrackingNumber import ClaimEnrichmentService

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

    # -----------------------------------------
# Test Cases สำหรับ Repository
# -----------------------------------------

def test_repository_can_save_and_retrieve_case():
    # 1. สร้างลิ้นชักจำลอง (In-Memory) สำหรับเทส
    repo = InMemoryClaimRepository()
    
    # 2. สร้างเคสจำลอง
    tn = TrackingNumber(value="TH1234567890")
    claim_case = ClaimCase(tracking_number=tn)
    
    # ลองใส่ใบเคลมเข้าไป 1 ใบ
    ticket = ClaimTicket(
        ticket_id=TicketId(value="CMP-999"),
        tracking_number=tn,
        compensation_amount=Money(amount=1000, currency="THB")
    )
    claim_case.add_ticket(ticket)

    # 3. สั่งเซฟลงลิ้นชัก!
    repo.save(claim_case)

    # 4. สั่งค้นหาจากลิ้นชักด้วยเลข Tracking
    retrieved_case = repo.get_by_tracking(tn)

    # 5. ตรวจสอบว่าหาเจอไหม และข้อมูลครบหรือเปล่า
    assert retrieved_case is not None # ต้องไม่เป็นค่าว่าง
    assert retrieved_case.tracking_number.value == "TH1234567890"
    assert len(retrieved_case.tickets) == 1
    assert retrieved_case.total_compensation.amount == 1000.0


# -----------------------------------------
# Test Cases สำหรับ Repository
# -----------------------------------------

def test_repository_can_save_and_retrieve_case():
    # 1. สร้างลิ้นชักจำลอง (In-Memory) สำหรับเทส
    repo = InMemoryClaimRepository()
    
    # 2. สร้างเคสจำลอง
    tn = TrackingNumber(value="TH1234567890")
    claim_case = ClaimCase(tracking_number=tn)
    
    # ลองใส่ใบเคลมเข้าไป 1 ใบ
    ticket = ClaimTicket(
        ticket_id=TicketId(value="CMP-999"),
        tracking_number=tn,
        compensation_amount=Money(amount=1000, currency="THB")
    )
    claim_case.add_ticket(ticket)

    # 3. สั่งเซฟลงลิ้นชัก!
    repo.save(claim_case)

    # 4. สั่งค้นหาจากลิ้นชักด้วยเลข Tracking
    retrieved_case = repo.get_by_tracking(tn)

    # 5. ตรวจสอบว่าหาเจอไหม และข้อมูลครบหรือเปล่า
    assert retrieved_case is not None # ต้องไม่เป็นค่าว่าง
    assert retrieved_case.tracking_number.value == "TH1234567890"
    assert len(retrieved_case.tickets) == 1
    assert retrieved_case.total_compensation.amount == 1000.0


import pytest
import pandas as pd
import os

# -----------------------------------------
# Integration Test สำหรับ Pandas Repository
# -----------------------------------------

def test_pandas_repo_can_load_from_real_excel():
    # 1. [Arrange] เตรียมไฟล์ Excel จำลองสำหรับเทส
    test_file = r"test_integration.xlsx"
    mock_df = pd.DataFrame({
        'complaint_ticket_id': ['TKT-001'],
        'tracking_no': ['TH999999'],
        'compensation_final_amt': [500.0]
    })
    mock_df.to_excel(test_file, index=False)

    try:
        # 2. [Act] ลองใช้ Repository อ่านไฟล์นี้
        repo = PandasClaimRepository(test_file)
        results = repo.get_all_cases()

        # 3. [Assert] ตรวจสอบว่าของที่ได้ออกมา "ไม่ใช่แค่ตาราง" แต่เป็น "Object"
        assert len(results) == 1
        assert isinstance(results[0], ClaimCase) # ต้องเป็น Class ClaimCase
        assert results[0].tracking_number.value == "TH999999"
        assert results[0].total_compensation.amount == 500.0

    finally:
        # ลบไฟล์ทิ้งหลังเทสเสร็จ (รักษาความสะอาด)
        if os.path.exists(test_file):
            os.remove(test_file)

# -----------------------------------------
# Test Case: การเติมยอดเงินชดเชยให้สมบูรณ์
# -----------------------------------------

def test_claim_enrichment_logic():
    # 1. [Arrange] เตรียมเคสที่เงินยังเป็น 0 (จากไฟล์ 1)
    tn = TrackingNumber(value="TH777")
    my_case = ClaimCase(tracking_number=tn)
    # ใส่ใบแจ้งที่เงินเป็น 0 บาทลงไป
    my_case.add_ticket(ClaimTicket(
        ticket_id=TicketId(value="TKT-001"),
        tracking_number=tn,
        compensation_amount=Money(amount=0, currency="THB")
    ))

    # 2. [Arrange] เตรียมข้อมูลเงินจริง (จำลองข้อมูลที่โหลดมาจากไฟล์ 2)
    # เราใช้ Dictionary เพราะมันค้นหาไวกว่า List (Big O เป็น 1)
    money_map = {
        "TH777": Money(amount=1500.0, currency="THB")
    }

    # 3. [Act] เรียกใช้ Service (ที่เรากำลังจะเขียน)
    service = ClaimEnrichmentService()
    service.enrich(my_case, money_map)

    # 4. [Assert] ยอดรวมในเคสต้องเปลี่ยนจาก 0 เป็น 1500
    assert my_case.total_compensation.amount == 1500.0