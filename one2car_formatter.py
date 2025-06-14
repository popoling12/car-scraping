import json
import os
import pandas as pd


def build_one2car_database_from_json(directory_path):
    """
    สแกนไฟล์ JSON ของข้อมูลจาก one2car ทั้งหมดในไดเรกทอรีที่ระบุ,
    ดึงข้อมูลรถยนต์, และแปลงเป็น Pandas DataFrame ตาม template

    Args:
        directory_path (str): เส้นทางไปยังโฟลเดอร์ที่มีไฟล์ JSON

    Returns:
        pandas.DataFrame: ตารางข้อมูลรถยนต์ทั้งหมดที่รวบรวมได้
                          หรือ DataFrame ว่างถ้าไม่พบข้อมูล
    """
    all_cars_data = []
    source_name = "one2car"

    if not os.path.isdir(directory_path):
        print(f"ผิดพลาด: ไม่พบโฟลเดอร์ '{directory_path}' กรุณาตรวจสอบตำแหน่ง")
        return pd.DataFrame()

    print(f"เริ่มต้นสแกนไฟล์ในโฟลเดอร์ '{directory_path}'...")

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
            # --- อ่านไฟล์ด้วย encoding 'utf-8-sig' ตามที่กำหนด ---
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                car_list = json.load(f)

            for car in car_list:
                # --- การดึงข้อมูลและคำนวณฟิลด์ที่ซับซ้อน ---

                # 1. คำนวณ Sub Model
                full_name = car.get('name', '')
                brand_name = car.get('brand', '')
                model_name = car.get('model', '')
                year_str = str(car.get('year', ''))
                # ลบส่วนที่ไม่ต้องการออกจากชื่อเต็มเพื่อให้ได้รุ่นย่อย
                sub_model = full_name.replace(brand_name, '').replace(model_name, '').replace(year_str, '').strip()

                # 2. ดึงชื่อผู้ขายจาก URL
                dealer_url = car.get('dealer_url', '')
                seller_name = dealer_url.split('/')[-1] if dealer_url else 'N/A'

                car_info = {
                    "Sources": source_name,
                    "Brand": brand_name,
                    "Model": model_name,
                    "Sub Model": sub_model,
                    "Year": car.get('year'),
                    "Price": car.get('price'),
                    "Mileage": car.get('mileage_km'),
                    "Plate No.": "N/A",
                    "Seller Name": seller_name,
                    "URL": car.get('page_url')
                }
                all_cars_data.append(car_info)

        except json.JSONDecodeError:
            print(f"    คำเตือน: ไม่สามารถอ่านข้อมูล JSON จากไฟล์ {filename} ได้")
        except Exception as e:
            print(f"    เกิดข้อผิดพลาดขณะประมวลผลไฟล์ {filename}: {e}")

    if not all_cars_data:
        print("ไม่พบข้อมูลรถยนต์ในไฟล์ JSON ทั้งหมด")
        return pd.DataFrame()

    df = pd.DataFrame(all_cars_data)

    column_order = [
        "Sources", "Brand", "Model", "Sub Model", "Year",
        "Price", "Mileage", "Plate No.", "Seller Name", "URL"
    ]
    df = df[column_order]

    return df


# --- ส่วนหลักของโปรแกรม ---
if __name__ == "__main__":
    DATA_DIRECTORY = 'one2car'
    OUTPUT_DIRECTORY = 'combined'
    OUTPUT_FILENAME = 'one2car_combined_data.csv'

    combined_dataframe = build_one2car_database_from_json(DATA_DIRECTORY)

    if not combined_dataframe.empty:
        try:
            print(f"\nกำลังเตรียมบันทึกไฟล์... ตรวจสอบโฟลเดอร์ '{OUTPUT_DIRECTORY}'")
            os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

            output_path = os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILENAME)

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