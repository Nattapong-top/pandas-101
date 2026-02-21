import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ==========================================
# 📦 ไฟล์ที่ 1: จำลองข้อมูลการแจ้งเคลม (Mock Data 1)
# ==========================================
data_1 = {
    'complaint_ticket_id': ['CMP-1001', 'CMP-1002', 'CMP-1003', 'CMP-1004', 'CMP-1005'],
    'compensation_ticket_id': ['CPN-801', 'CPN-802', 'CPN-803', 'CPN-804', 'CPN-805'],
    'shipment_type_name': ['STANDARD', 'EXPRESS', 'STANDARD', 'STANDARD', 'EXPRESS'],
    'seller_operation_country': ['TH', 'TH', 'TH', 'TH', 'TH'],
    'package_id': ['PKG-5501', 'PKG-5502', 'PKG-5503', 'PKG-5504', 'PKG-5505'],
    # สังเกตว่า TH1234567891 ซ้ำกัน 2 บรรทัด เพื่อให้ป๋าทดสอบเงื่อนไข De-duplicate
    'tracking_no': ['TH1234567890', 'TH1234567891', 'TH1234567891', 'TH1234567893', 'TH1234567894'],
    'complaint_ticket_create_time': [
        '2026-02-01 10:00:00', 
        '2026-02-02 11:30:00', 
        '2026-02-03 09:15:00', # เคลมซ้ำของ TH1234567891
        '2026-02-04 14:20:00', 
        '2026-02-05 16:45:00'
    ]
}
df_mock_1 = pd.DataFrame(data_1)
df_mock_1.to_excel('mock_claim_data.xlsx', index=False)
print("✅ สร้างไฟล์ mock_claim_data.xlsx สำเร็จ!")

# ==========================================
# 💰 ไฟล์ที่ 2: จำลองข้อมูลเงินชดเชย (Mock Data 2 - หัวตาราง 2 ชั้น)
# ==========================================
# สร้างข้อมูลบรรทัดที่ 1 (ชื่อคอลัมน์จริงๆ)
columns_row = [
    'ticket id', 'issue type', 'region', 'package ID', 'tracking number', 
    'TOTAL amount', 'TOTAL currency', 'goods value amount', 'shipping fee amount'
]

# สร้างข้อมูลบรรทัดที่ 0 (กลุ่มของคอลัมน์ - Meta)
meta_row = [
    'Ticket Meta', 'Ticket Meta', 'Ticket Meta', 'Ticket Meta', 'Ticket Meta',
    'Compensation Result', 'Compensation Result', 'Compensation Item Meta', 'Compensation Item Meta'
]

# สร้างข้อมูล (Data Rows)
# สังเกตว่า tracking number ตรงกับไฟล์ที่ 1 เพื่อให้ VLOOKUP หากันเจอ
data_rows = [
    ['1477594532001', 'Delivered But Not Received', 'TH', 'PKG-5501', 'TH1234567890', 886.26, 'THB', 692.01, 23.25],
    ['1477594532002', 'Damaged Item', 'TH', 'PKG-5502', 'TH1234567891', 362.50, 'THB', 171.00, 12.50],
    ['1477594532003', 'Lost Parcel', 'TH', 'PKG-5504', 'TH1234567893', 1500.00, 'THB', 1500.00, 0.00],
    ['1477594532004', 'Damaged Item', 'TH', 'PKG-5505', 'TH1234567894', 450.75, 'THB', 400.00, 50.75]
]

# นำมาประกอบร่างกันให้เป็น DataFrame ที่มีหัวตารางจำลอง
# เราจะใช้เทคนิคสร้าง DataFrame เปล่าๆ แล้วจับยัดใส่ทีละบรรทัดเพื่อจำลองความซับซ้อนของ Excel
df_mock_2 = pd.DataFrame([columns_row] + data_rows, columns=meta_row)

df_mock_2.to_excel('mock_compensation_data.xlsx', index=False)
print("✅ สร้างไฟล์ mock_compensation_data.xlsx สำเร็จ!")