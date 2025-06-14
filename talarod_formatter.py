import json
import os
import pandas as pd


def build_taladrod_database_from_json(input_filepath):
    """
    อ่านข้อมูลรถยนต์จากไฟล์ JSON ของ Talad Rod,
    ประมวลผลข้อมูล และแปลงเป็น Pandas DataFrame ตาม template

    Args:
        input_filepath (str): เส้นทางไปยังไฟล์ JSON ที่ต้องการอ่าน

    Returns:
        pandas.DataFrame: ตารางข้อมูลรถยนต์ทั้งหมดที่ประมวลผลแล้ว
                          หรือ DataFrame ว่างถ้าไม่พบข้อมูล/ไฟล์
    """
    source_name = "talad_rod"
    processed_data = []

    if not os.path.exists(input_filepath):
        print(f"ผิดพลาด: ไม่พบไฟล์ '{input_filepath}' กรุณาตรวจสอบว่ามีไฟล์นี้อยู่จริง")
        return pd.DataFrame()

    print(f"กำลังอ่านข้อมูลจากไฟล์ '{input_filepath}'...")

    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            car_list = json.load(f)

        for car in car_list:
            # --- การคำนวณและทำความสะอาดข้อมูล ---
            name_mmt = car.get('NameMMT', '').strip()

            # 1. ดึง Brand
            brand = name_mmt.split(' ')[0] if name_mmt else 'N/A'

            # 2. ดึง Model
            model = car.get('Model', '')

            # 3. คำนวณ Sub Model
            sub_model = name_mmt.replace(brand, '', 1).replace(model, '', 1).strip()

            # 4. ทำความสะอาด Price
            price_str = car.get('Prc', '0').replace(',', '')
            price = float(price_str) if price_str.isdigit() else 'N/A'

            # --- ส่วนที่แก้ไข: สร้าง Plate No. ตามที่ผู้ใช้กำหนด (JvNm + iPgVw) ---
            province = car.get('JvNm', '').strip()
            page_view_num = car.get('iPgVw', '').strip()
            # นำข้อมูลมาต่อกัน ถ้ามีข้อมูลอย่างน้อยหนึ่งอย่าง
            plate_no = f"{province}{page_view_num}" if province or page_view_num else "N/A"

            # 6. สร้าง URL
            car_id = car.get('Cid')
            page_url = f"https://www.taladrod.com/w/card/{car_id}" if car_id else "N/A"

            car_info = {
                "Sources": source_name,
                "Brand": brand,
                "Model": model,
                "Sub Model": sub_model,
                "Year": car.get('Yr'),
                "Price": price,
                "Mileage": "N/A",
                "Plate No.": plate_no,  # <-- ใช้ค่าที่คำนวณใหม่
                "Seller Name": "N/A",
                "URL": page_url
            }
            processed_data.append(car_info)

    except json.JSONDecodeError:
        print(f"    คำเตือน: ไม่สามารถอ่านข้อมูล JSON จากไฟล์ {input_filepath} ได้")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดร้ายแรงขณะอ่านหรือประมวลผลไฟล์ JSON: {e}")
        return pd.DataFrame()

    if not processed_data:
        print("ไม่พบข้อมูลที่สามารถประมวลผลได้ในไฟล์")
        return pd.DataFrame()

    final_df = pd.DataFrame(processed_data)

    column_order = [
        "Sources", "Brand", "Model", "Sub Model", "Year",
        "Price", "Mileage", "Plate No.", "Seller Name", "URL"
    ]
    final_df = final_df[column_order]

    return final_df


# --- ส่วนหลักของโปรแกรม ---
if __name__ == "__main__":
    # --- ส่วนที่แก้ไข: เปลี่ยนชื่อไฟล์ Input ---
    DATA_FILE = 'talarod.json'
    OUTPUT_DIRECTORY = 'combined'
    OUTPUT_FILENAME = 'talad_rod_combined_data.csv'

    combined_dataframe = build_taladrod_database_from_json(DATA_FILE)

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