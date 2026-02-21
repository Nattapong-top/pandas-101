import pytest
from pydantic import ValidationError

# สมมติว่าเราเรียกใช้คลาสจากไฟล์ domain (ที่เรากำลังจะสร้าง)
from domain.TrackingNumber import TrackingNumber

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

