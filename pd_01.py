import pandas as pd

df = pd.read_excel('mock_isp_data.xlsx')
print('ห้าแถวแรก')
print(df.head())

print('ข้อมูล data frame')
print(df.info())

print('รายละเอียดข้อมูล')
print(df.describe())

print('ดูชื่อ column  ทั้งหมด')
print(df.columns)