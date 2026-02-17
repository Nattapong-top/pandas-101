import pandas as pd

# สร้างข้อมูลใหม่ที่มีสถานะหลากหลาย
# สมมติวันนี้คือ 12 กุมภาพันธ์ 2026
data_v2 = {
    'MSISDN': ['0960000001', '0960000002', '0960000003', '0960000004', '0960000005'],
    'CUST_FULL_NAME': [
        'นายหมดอายุ แล้วครับ',     # เคส: Expired
        'บริษัท กำลังจะหมด (15วัน)', # เคส: Warning
        'ร้านค้า ยังเหลือเยอะ',      # เคส: Normal
        'นายพอดีเป๊ะ (วันนี้หมด)',    # เคส: Edge Case
        'บจก. เพิ่งเริ่มสัญญา'       # เคส: Long-term
    ],
    'RC_RATE': [599, 899, 1200, 449, 299],
    'SUBS_STATUS': ['Active', 'Active', 'Active', 'Active', 'Active'],
    'CONTRACT_START_DT': ['2025-01-01', '2025-02-15', '2025-10-20', '2025-02-12', '2026-01-01'],
    'CONTRACT_END_DT': [
        '2025-12-31',  # หมดไปแล้วปีที่แล้ว
        '2026-02-27',  # เหลืออีกประมาณ 15 วัน (Warning!)
        '2026-12-31',  # เหลืออีกนาน
        '2026-02-12',  # หมดวันนี้พอดี (Edge Case)
        '2027-12-31'   # เหลืออีกเป็นปี
    ]
}

df_mock = pd.DataFrame(data_v2)

# บันทึกลง Excel
with pd.ExcelWriter('mock_isp_data.xlsx') as writer:
    df_mock.to_excel(writer, sheet_name='Main_Data', index=False)

print("ป๋าครับ! อัปเดต Mock Data v.2 เรียบร้อย มีครบทุกสถานะแล้วครับ")