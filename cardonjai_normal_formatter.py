import json
import os
import pandas as pd


def build_car_database_from_json(directory_path):
    """
    สแกนไฟล์ JSON ทั้งหมดในไดเรกทอรีที่ระบุ, ดึงข้อมูลรถยนต์ทั้งหมด,
    และแปลงเป็น Pandas DataFrame ตาม template ที่กำหนด

    Args:
        directory_path (str): เส้นทางไปยังโฟลเดอร์ที่มีไฟล์ JSON

    Returns:
        pandas.DataFrame: ตารางข้อมูลรถยนต์ทั้งหมดที่รวบรวมได้
                          หรือ DataFrame ว่างถ้าไม่พบข้อมูล
    """
    all_cars_data = []
    source_name = "roddonjai_used_car_list"

    # ตรวจสอบว่าไดเรกทอรีมีอยู่จริงหรือไม่
    if not os.path.isdir(directory_path):
        print(f"ผิดพลาด: ไม่พบโฟลเดอร์ '{directory_path}' กรุณาตรวจสอบว่าวางสคริปต์ถูกที่")
        return pd.DataFrame()

    print(f"เริ่มต้นสแกนไฟล์ในโฟลเดอร์ '{directory_path}'...")

    # วนลูปอ่านทุกไฟล์ในโฟลเดอร์
    files_in_directory = os.listdir(directory_path)
    json_files = [f for f in files_in_directory if f.endswith('.json')]

    if not json_files:
        print("ไม่พบไฟล์ .json ในโฟลเดอร์")
        return pd.DataFrame()

    print(f"พบ {len(json_files)} ไฟล์ JSON จะเริ่มทำการประมวลผล...")

    for filename in json_files:
        file_path = os.path.join(directory_path, filename)
        print(f"  - กำลังอ่านไฟล์: {filename}")
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)

            # ดึงข้อมูลจาก list ของ 'cars' ในแต่ละไฟล์
            for car in data.get('cars', []):
                # ใช้ .get() เพื่อเข้าถึงข้อมูลอย่างปลอดภัย ป้องกัน error หาก key ไม่มีอยู่
                seller_name = car.get('dealerProfileDocument', {}).get('dealerName', 'N/A')

                car_info = {
                    "Sources": source_name,
                    "Brand": car.get('carBrand'),
                    "Model": car.get('carModel'),
                    "Sub Model": car.get('carSubModel'),
                    "Year": car.get('carYear'),
                    "Price": car.get('carPrice'),
                    "Mileage": car.get('mileage'),
                    "Plate No.": car.get('licensePlateNumber'),
                    "Seller Name": seller_name,
                    "URL": car.get('carUrl') if car.get('carUrl') else "N/A"
                }
                all_cars_data.append(car_info)

        except json.JSONDecodeError:
            print(f"    คำเตือน: ไม่สามารถอ่านข้อมูล JSON จากไฟล์ {filename} ได้ (อาจมีโครงสร้างผิด)")
        except Exception as e:
            print(f"    เกิดข้อผิดพลาดขณะประมวลผลไฟล์ {filename}: {e}")

    if not all_cars_data:
        print("ไม่พบข้อมูลรถยนต์ในไฟล์ JSON ทั้งหมด")
        return pd.DataFrame()

    # สร้าง DataFrame จาก list ของข้อมูลทั้งหมด
    df = pd.DataFrame(all_cars_data)

    # จัดลำดับคอลัมน์ให้ตรงกับ Template ที่ต้องการ
    column_order = [
        "Sources", "Brand", "Model", "Sub Model", "Year",
        "Price", "Mileage", "Plate No.", "Seller Name", "URL"
    ]

    # กรองเอาเฉพาะคอลัมน์ที่ต้องการและจัดลำดับ
    df = df[column_order]

    return df


# --- ส่วนหลักของโปรแกรม ---
if __name__ == "__main__":
    # กำหนดชื่อโฟลเดอร์ที่เก็บข้อมูลและโฟลเดอร์/ไฟล์ผลลัพธ์
    DATA_DIRECTORY = 'cardonjai'
    OUTPUT_DIRECTORY = 'combined' # <--- ชื่อโฟลเดอร์สำหรับเก็บผลลัพธ์
    OUTPUT_FILENAME = 'roddonjai_combined_data.csv'

    # เรียกใช้ฟังก์ชันหลักเพื่อประมวลผล
    combined_dataframe = build_car_database_from_json(DATA_DIRECTORY)

    # ตรวจสอบว่ามีข้อมูลที่ถูกประมวลผลหรือไม่ ก่อนทำการบันทึก
    if not combined_dataframe.empty:
        try:
            # ---- ส่วนที่แก้ไข: สร้างโฟลเดอร์สำหรับเก็บไฟล์ผลลัพธ์ ----
            print(f"\nกำลังเตรียมบันทึกไฟล์... ตรวจสอบโฟลเดอร์ '{OUTPUT_DIRECTORY}'")
            os.makedirs(OUTPUT_DIRECTORY, exist_ok=True) # สร้างโฟลเดอร์ถ้ายังไม่มี

            # ---- ส่วนที่แก้ไข: กำหนดเส้นทางเต็มของไฟล์ผลลัพธ์ ----
            output_path = os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILENAME)

            # บันทึก DataFrame เป็นไฟล์ CSV ไปยังเส้นทางใหม่
            # ใช้ encoding 'utf-8-sig' เพื่อให้โปรแกรม Excel เปิดไฟล์ภาษาไทยได้ถูกต้อง
            combined_dataframe.to_csv(output_path, index=False, encoding='utf-8-sig')

            print("\n----------------------------------------------------")
            print("การประมวลผลเสร็จสมบูรณ์!")
            print(f"รวบรวมข้อมูลรถยนต์ทั้งหมด {len(combined_dataframe)} คัน")
            print(f"ไฟล์ผลลัพธ์ถูกบันทึกเรียบร้อยที่: '{output_path}'") # <--- แสดง path ที่ถูกต้อง
            print("----------------------------------------------------")

        except Exception as e:
            print(f"\nเกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")
    else:
        print("\nไม่สามารถสร้างไฟล์ผลลัพธ์ได้ เนื่องจากไม่พบข้อมูลที่สามารถประมวลผลได้")