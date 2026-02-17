import pandas as pd

mock_data = {
    'MSISDN': ['0960673105', '0912345678', '0812345678', '0612345678', '0998887776'],
    'RC_RATE': [599, 899, 1200, 449, 299],
    'SUBS_STATUS': ['Active', 'Active', 'Suspended', 'Active', 'Terminated'],
    'CUST_FULL_NAME': ['ABC Corp', 'XYZ Co.,Ltd', 'Pah Nattapong Service', 'JukThong Tech', 'Sample Client'],
    'PRODUCT_TYPE': ['FTTH', 'Mobile', 'Mobile', 'DATA SERVICE', 'FTTH'],
    'CONTRACT_START_DT': ['2025-03-01', '2025-05-15', '2024-10-20', '2024-01-10', '2024-12-01'],
    'CONTRACT_END_DT': ['2026-03-01', '2026-05-15', '2025-10-20', '2025-01-10', '2025-12-01']
}

# 2. แปลง Dictionary เป็น DataFrame
df = pd.DataFrame(mock_data)

# 3. บันทึกลงไฟล์ Excel (สร้าง 2 ชีทเพื่อฝึกซ้อม)
with pd.ExcelWriter('mock_isp_data.xlsx') as writer:
    df.to_excel(writer, sheet_name='Main_Data', index=False)
    # เพิ่มชีทจิปถะอีกอัน
    pd.DataFrame({'Update_Date': ['2024-05-20'], 'Admin': ['Pah']}).to_excel(writer, sheet_name='Metadata', index=False)

print('สร้างไฟล์ mock_isp_data.xlxs เรียบร้อยแล้ว')