import os
import pandas as pd


def build_krungsri_database_from_csv(input_filepath):
    """
    อ่านข้อมูลรถยนต์จากไฟล์ CSV ของ Krungsri Market,
    ประมวลผลข้อมูล และแปลงเป็น Pandas DataFrame ตาม template

    Args:
        input_filepath (str): เส้นทางไปยังไฟล์ CSV ที่ต้องการอ่าน

    Returns:
        pandas.DataFrame: ตารางข้อมูลรถยนต์ทั้งหมดที่ประมวลผลแล้ว
                          หรือ DataFrame ว่างถ้าไม่พบข้อมูล/ไฟล์
    """
    source_name = "krungsri_market"
    processed_data = []

    # ตรวจสอบว่าไฟล์มีอยู่จริงหรือไม่
    if not os.path.exists(input_filepath):
        print(f"ผิดพลาด: ไม่พบไฟล์ '{input_filepath}' กรุณาตรวจสอบว่ามีไฟล์นี้อยู่จริง")
        return pd.DataFrame()

    print(f"กำลังอ่านข้อมูลจากไฟล์ '{input_filepath}'...")

    try:
        # อ่านไฟล์ CSV ด้วย Pandas
        df = pd.read_csv(input_filepath)

        # วนลูปเพื่อประมวลผลข้อมูลทีละแถว
        for index, row in df.iterrows():

            # --- แยก Model และ Sub Model ---
            model_full = str(row.get('model', '')).strip()
            parts = model_full.split(' ', 1)
            model = parts[0]
            sub_model = parts[1] if len(parts) > 1 else 'N/A'

            # --- คำนวณราคาเฉลี่ยจาก Price Range ---
            avg_price = 'N/A'
            try:
                price_range_str = str(row.get('price_range', '')).strip()
                if ' - ' in price_range_str:
                    low_str, high_str = price_range_str.split(' - ')
                    low_price = float(low_str.replace(',', ''))
                    high_price = float(high_str.replace(',', ''))
                    avg_price = (low_price + high_price) / 2
            except (ValueError, AttributeError):
                print(f"  - คำเตือน: ไม่สามารถประมวลผล price_range '{row.get('price_range')}' ที่แถว {index + 1}")

            # --- ทำความสะอาดข้อมูล Mileage ---
            mileage = 'N/A'
            try:
                mileage = int(str(row.get('mileage', '')).replace(',', ''))
            except (ValueError, AttributeError):
                print(f"  - คำเตือน: ไม่สามารถประมวลผล mileage '{row.get('mileage')}' ที่แถว {index + 1}")

            car_info = {
                "Sources": source_name,
                "Brand": row.get('brand'),
                "Model": model,
                "Sub Model": sub_model,
                "Year": "N/A",  # ไม่มีข้อมูลนี้ใน Source
                "Price": avg_price,
                "Mileage": mileage,
                "Plate No.": "N/A",
                "Seller Name": "N/A",
                "Phone Number": "N/A",
                "URL": row.get('link')
            }
            processed_data.append(car_info)

    except Exception as e:
        print(f"เกิดข้อผิดพลาดร้ายแรงขณะอ่านหรือประมวลผลไฟล์ CSV: {e}")
        return pd.DataFrame()

    if not processed_data:
        print("ไม่พบข้อมูลที่สามารถประมวลผลได้ในไฟล์")
        return pd.DataFrame()

    # สร้าง DataFrame จาก list ของข้อมูลที่ประมวลผลแล้ว
    final_df = pd.DataFrame(processed_data)

    # จัดลำดับคอลัมน์ให้ตรงตาม Template
    column_order = [
        "Sources", "Brand", "Model", "Sub Model", "Year",
        "Price", "Mileage", "Plate No.", "Seller Name","Phone Number", "URL"
    ]
    final_df = final_df[column_order]

    return final_df


# --- ส่วนหลักของโปรแกรม ---
if __name__ == "__main__":
    # กำหนดชื่อไฟล์ข้อมูลและไฟล์ผลลัพธ์
    DATA_FILE = 'krungsrimarket_demo.csv'
    OUTPUT_DIRECTORY = 'combined'
    OUTPUT_FILENAME = 'krungsri_market_combined_data.csv'

    # เรียกใช้ฟังก์ชันหลักเพื่อประมวลผล
    combined_dataframe = build_krungsri_database_from_csv(DATA_FILE)

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