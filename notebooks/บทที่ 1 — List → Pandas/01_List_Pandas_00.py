'''บทที่ 1 — List → Pandas

หัวใจ: เข้าใจ “โครงสร้างข้อมูล” ก่อน แล้ว Pandas จะง่ายขึ้นมาก

1) Python List คืออะไร

ตื่นเต้นเลยตรงนี้ เพราะมันคือ “ฐานข้อมูลจิ๋ว” ที่เราคุมได้เอง
ใช้เก็บข้อมูลหลายตัวในตัวแปรเดียว เช่น:
'''

nums = [10, 20, 30]
names = ["A", "B", "C"]
mixed = [10, "A", True]


'''คุณสมบัติ:

ใส่อะไรก็ได้ ตัวเลข ตัวหนังสือ object

แก้ไขได้ (mutable)

มี index เช่น names[0] == "A"

2) Nested List (Matrix)

คือ list ซ้อน list เช่น ตาราง Excel ในแบบดิบๆ'''

m = [
    [1, 2, 3],
    [4, 5, 6]
]


'''ใช้กับโจทย์ matrix:

หาผลรวมแต่ละแถว

ผลรวมแต่ละคอลัมน์

ค่ามากสุดในคอลัมน์

zip คว่ำตาราง
ทั้งหมดนี้คือ “พื้นฐาน Pandas” แต่ยังไม่รู้ตัว!

3) จาก list → Pandas DataFrame มันเกิดขึ้นยังไง

Pandas รับ list หลายแบบ เช่น:

3.1 list ของ list

เหมือน nested list แบบตาราง'''

import pandas as pd
df = pd.DataFrame([
    [1, 2, 3],
    [4, 5, 6]
])

'''3.2 list ของ dict

แบบนี้ใช้เยอะสุด เพราะอ่านง่ายเหมือนข้อมูลจริง
'''

rows = [
    {"name": "A", "age": 20},
    {"name": "B", "age": 25}
]
df = pd.DataFrame(rows)


'''
3.3 dict ของ list

แบบนี้ก็โคตรคลีน'''

data = {
    "name": ["A", "B"],
    "age": [20, 25]
}
df = pd.DataFrame(data)


'''สรุปสั้นชัด ๆ
Pandas คือการเอา list/dict ของ Python มาประกอบกันให้กลายเป็นตาราง (DataFrame)
แค่นั้นเอง!

4) แล้ว Numpy อยู่ตรงไหน

Numpy คือ “หัวใจลึก ๆ” ที่ Pandas เอาไปใช้เก็บข้อมูลแบบ array (เร็วมาก)
แต่ตอนนี้ป๋ายังไม่ต้องเรียน Numpy ก็ได้
เพราะ Pandas = friendly layer ที่ซ่อน Numpy ไว้ข้างใน

ลำดับที่ชัดที่สุด:

list → dict → nested list → matrix → DataFrame → Pandas → Numpy (ลึก)

5) ทำไมป๋ากำลังเรียน list แต่ทำงานจริงดันใช้ Pandas

เพราะงานจริงต้องจัดการตารางเยอะ แต่พื้นฐานการคิดตาราง = list + nested list 100%
เมื่อป๋าเข้าใจ list/nested list ดี
ป๋าจะ “เห็นกลไกของ Pandas แบบโปร”

เช่น:

row = list หนึ่งแถว

column = คีย์ของ dict

DataFrame = list ของ dict

ค่า missing = None

for loop ฟีลเดียวกับ Pandas functions เลย

6) ให้ป๋าดูตัวอย่างภาพใหญ่ (โคตรตอบโจทย์งานจริง)
เริ่มจากข้อมูลแบบ list'''

rows = [
    ["ป๋า", 32, "IT"],
    ["เอ", 29, "HR"]
]

'''กลายเป็น DataFrame'''
df = pd.DataFrame(rows, columns=["name", "age", "dept"])

'''แล้วป๋าจะได้ใช้แบบนี้ในงาน'''
df[df["dept"] == "IT"]
df["age"].mean()
df.to_excel("out.xlsx")


'''ทั้งหมดนี้พื้นฐานมาจาก “list + index + loop” จริง ๆ

7) โครงบทเรียนบทที่ 1 (ให้ป๋าเดินตามแบบไม่หลง)

ความเข้าใจ list พื้นฐาน

การเข้าถึง index

loop list

nested list

โจทย์ matrix 5 แบบ

list → dict → list ของ dict

แปลงไป DataFrame

อ่าน/เขียน CSV

แกะกลไก Pandas จากพื้นฐาน list'''