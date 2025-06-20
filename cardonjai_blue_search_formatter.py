import json
import os
import pandas as pd


def build_bluebook_database_from_json(directory_path):
    """
    สแกนไฟล์ JSON ของข้อมูล Blue Book ทั้งหมดในไดเรกทอรีที่ระบุ,
    ดึงข้อมูลราคากลางรถยนต์, และแปลงเป็น Pandas DataFrame ตาม template

    Args:
        directory_path (str): เส้นทางไปยังโฟลเดอร์ที่มีไฟล์ JSON

    Returns:
        pandas.DataFrame: ตารางข้อมูลรถยนต์ทั้งหมดที่รวบรวมได้
                          หรือ DataFrame ว่างถ้าไม่พบข้อมูล
    """
    all_cars_data = []
    source_name = "blue_search"  # กำหนดแหล่งข้อมูลสำหรับไฟล์ชุดนี้

    # ตรวจสอบว่าไดเรกทอรีมีอยู่จริงหรือไม่
    if not os.path.isdir(directory_path):
        print(f"ผิดพลาด: ไม่พบโฟลเดอร์ '{directory_path}' กรุณาตรวจสอบตำแหน่ง")
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
                # โครงสร้างไฟล์นี้เป็น list of objects
                data_list = json.load(f)

            # วนลูปใน list หลัก (แต่ละ object คือ 1 model)
            for model_group in data_list:
                # เข้าถึง list ของรถรุ่นย่อย/ปี ใน key 'data'
                for car_details in model_group.get('data', []):
                    car_info = {
                        "Sources": source_name,
                        "Brand": car_details.get('carBrand'),
                        "Model": car_details.get('carModel'),
                        "Sub Model": car_details.get('carSubModel'),
                        "Year": car_details.get('year'),
                        "Price": car_details.get('marketPriceSecondhand'),
                        "Mileage": "N/A",  # ไม่มีข้อมูลนี้ใน Source
                        "Plate No.": "N/A", # ไม่มีข้อมูลนี้ใน Source
                        "Seller Name": "N/A",# ไม่มีข้อมูลนี้ใน Source
                        "Phone Number":"N/A",
                        "URL": "N/A" # ไม่มีข้อมูลนี้ใน Source
                    }
                    all_cars_data.append(car_info)

        except json.JSONDecodeError:
            print(f"    คำเตือน: ไม่สามารถอ่านข้อมูล JSON จากไฟล์ {filename} ได้")
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
        "Price", "Mileage", "Plate No.", "Seller Name","Phone Number", "URL"
    ]
    df = df[column_order]

    return df


# --- ส่วนหลักของโปรแกรม ---
if __name__ == "__main__":
    # กำหนดชื่อโฟลเดอร์ที่เก็บข้อมูลและโฟลเดอร์/ไฟล์ผลลัพธ์
    DATA_DIRECTORY = 'blue_search'
    OUTPUT_DIRECTORY = 'combined'
    OUTPUT_FILENAME = 'blue_search_combined_data.csv'

    # เรียกใช้ฟังก์ชันหลักเพื่อประมวลผล
    combined_dataframe = build_bluebook_database_from_json(DATA_DIRECTORY)

    # ตรวจสอบว่ามีข้อมูลที่ถูกประมวลผลหรือไม่ ก่อนทำการบันทึก
    if not combined_dataframe.empty:
        try:
            # สร้างโฟลเดอร์สำหรับเก็บไฟล์ผลลัพธ์ (ถ้ายังไม่มี)
            print(f"\nกำลังเตรียมบันทึกไฟล์... ตรวจสอบโฟลเดอร์ '{OUTPUT_DIRECTORY}'")
            os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

            # กำหนดเส้นทางเต็มของไฟล์ผลลัพธ์
            output_path = os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILENAME)

            # บันทึก DataFrame เป็นไฟล์ CSV
            combined_dataframe.to_csv(output_path, index=False, encoding='utf-8-sig')

            print("\n----------------------------------------------------")
            print("การประมวลผลเสร็จสมบูรณ์!")
            print(f"รวบรวมข้อมูลรถยนต์ทั้งหมด {len(combined_dataframe)} รายการ")
            print(f"ไฟล์ผลลัพธ์ถูกบันทึกเรียบร้อยที่: '{output_path}'")
            print("----------------------------------------------------")

        except Exception as e:
            print(f"\nเกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")
    else:
        print("\nไม่สามารถสร้างไฟล์ผลลัพธ์ได้ เนื่องจากไม่พบข้อมูลที่สามารถประมวลผลได้")