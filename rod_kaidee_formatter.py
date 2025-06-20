import json
import os
import pandas as pd


def build_kaidee_database_from_json(input_filepath):
    """
    อ่านข้อมูลรถยนต์จากไฟล์ JSON ของ Kaidee,
    ดึงข้อมูลจาก nested objects, และแปลงเป็น Pandas DataFrame ตาม template

    Args:
        input_filepath (str): เส้นทางไปยังไฟล์ JSON ที่ต้องการอ่าน

    Returns:
        pandas.DataFrame: ตารางข้อมูลรถยนต์ทั้งหมดที่ประมวลผลแล้ว
                          หรือ DataFrame ว่างถ้าไม่พบข้อมูล/ไฟล์
    """
    source_name = "rod_kaidee"
    processed_data = []

    # ตรวจสอบว่าไฟล์มีอยู่จริงหรือไม่
    if not os.path.exists(input_filepath):
        print(f"ผิดพลาด: ไม่พบไฟล์ '{input_filepath}' กรุณาตรวจสอบว่ามีไฟล์นี้อยู่จริง")
        return pd.DataFrame()

    print(f"กำลังอ่านข้อมูลจากไฟล์ '{input_filepath}'...")

    try:
        # อ่านไฟล์ JSON ด้วย encoding 'utf-8' ซึ่งเป็นมาตรฐาน
        with open(input_filepath, 'r', encoding='utf-8') as f:
            car_list = json.load(f)

        # วนลูปเพื่อประมวลผลข้อมูลทีละรายการ
        for car in car_list:
            # ใช้ .get() ซ้อนกันเพื่อเข้าถึงข้อมูลใน nested object อย่างปลอดภัย
            auto_info = car.get('autoInfo', {})
            member_info = car.get('member', {})

            # สร้าง URL ของประกาศจาก ID
            listing_id = car.get('id')
            page_url = f"https://www.kaidee.com/product/{listing_id}" if listing_id else "N/A"
            phone_number = car.get("contactInfo").get("phone", 'N/A')
            car_info = {
                "Sources": source_name,
                "Brand": auto_info.get('brand'),
                "Model": auto_info.get('model'),
                "Sub Model": auto_info.get('submodel'),
                "Year": auto_info.get('year'),
                "Price": car.get('price'),
                "Mileage": auto_info.get('mileage'),
                "Plate No.": "N/A",
                "Seller Name": member_info.get('name'),
                "Phone Number": phone_number,
                "URL": page_url
            }
            processed_data.append(car_info)

    except json.JSONDecodeError:
        print(f"    คำเตือน: ไม่สามารถอ่านข้อมูล JSON จากไฟล์ {input_filepath} ได้ (อาจมีโครงสร้างผิด)")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดร้ายแรงขณะอ่านหรือประมวลผลไฟล์ JSON: {e}")
        return pd.DataFrame()

    if not processed_data:
        print("ไม่พบข้อมูลที่สามารถประมวลผลได้ในไฟล์")
        return pd.DataFrame()

    # สร้าง DataFrame จาก list ของข้อมูลที่ประมวลผลแล้ว
    final_df = pd.DataFrame(processed_data)

    # จัดลำดับคอลัมน์ให้ตรงตาม Template
    column_order = [
        "Sources", "Brand", "Model", "Sub Model", "Year",
        "Price", "Mileage", "Plate No.", "Seller Name", "Phone Number","URL"
    ]
    final_df = final_df[column_order]

    return final_df


# --- ส่วนหลักของโปรแกรม ---
if __name__ == "__main__":
    # กำหนดชื่อไฟล์ข้อมูลและไฟล์ผลลัพธ์
    DATA_FILE = 'rod_kaidee.json'
    OUTPUT_DIRECTORY = 'combined'
    OUTPUT_FILENAME = 'rod_kaidee_combined_data.csv'

    # เรียกใช้ฟังก์ชันหลักเพื่อประมวลผล
    combined_dataframe = build_kaidee_database_from_json(DATA_FILE)

    # ตรวจสอบว่ามีข้อมูลที่ถูกประมวลผลหรือไม่ ก่อนทำการบันทึก
    if not combined_dataframe.empty:
        try:
            print(f"\nกำลังเตรียมบันทึกไฟล์... ตรวจสอบโฟลเดอร์ '{OUTPUT_DIRECTORY}'")
            os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

            output_path = os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILENAME)

            combined_dataframe.to_csv(output_path, index=False, encoding='utf-8-sig')

            print("\n----------------------------------------------------")
            print("การประมวลผลเสร็จสมบูรณ์!")
            print(f"ประมวลผลข้อมูลทั้งหมด {len(combined_dataframe)} รายการ")
            print(f"ไฟล์ผลลัพธ์ถูกบันทึกเรียบร้อยที่: '{output_path}'")
            print("----------------------------------------------------")

        except Exception as e:
            print(f"\nเกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")
    else:
        print("\nไม่สามารถสร้างไฟล์ผลลัพธ์ได้ เนื่องจากไม่พบข้อมูลหรือเกิดข้อผิดพลาด")