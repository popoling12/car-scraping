import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import json
import os
import threading
import sys
from datetime import datetime


# ==============================================================================
#  ส่วนตรรกะหลักในการประมวลผลข้อมูล (Logic Core)
#  (ส่วนนี้ไม่มีการเปลี่ยนแปลง)
# ==============================================================================

def build_taladrod_database_from_json(input_filepath):
    """
    อ่านข้อมูลรถยนต์จากไฟล์ JSON ของ Talad Rod,
    ประมวลผลข้อมูล และแปลงเป็น Pandas DataFrame ตาม template
    """
    source_name = "talad_rod"
    processed_data = []

    if not os.path.exists(input_filepath):
        print(f"(!) ผิดพลาด: ไม่พบไฟล์ '{input_filepath}'")
        return pd.DataFrame()

    print(f"[*] กำลังอ่านข้อมูลจากไฟล์: '{os.path.basename(input_filepath)}'...")

    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            car_list = json.load(f)

        print(f"[*] พบข้อมูลรถยนต์ {len(car_list)} รายการ กำลังประมวลผล...")

        for car in car_list:
            name_mmt = car.get('namemmt', '').strip()
            brand = name_mmt.split(' ')[0] if name_mmt else 'N/A'
            model = car.get('model', 'N/A')
            sub_model = name_mmt.replace(brand, '', 1).replace(model, '', 1).strip()
            if not sub_model:
                sub_model = 'N/A'
            price_str = str(car.get('prc', '0')).replace(',', '')
            price = float(price_str) if price_str.isdigit() else 'N/A'
            province = car.get('jvnm', '').strip()
            page_view_num = car.get('ipgvw', '').strip()
            plate_no = f"{province}{page_view_num}" if province or page_view_num else "N/A"
            car_id = car.get('cid')
            page_url = f"https://www.taladrod.com/w/card/{car_id}" if car_id else "N/A"

            car_info = {
                "Sources": source_name, "Brand": brand, "Model": model,
                "Sub Model": sub_model, "Year": car.get('yr', 'N/A'),
                "Price": price, "Mileage": car.get('mileage', 'N/A'),
                "Plate No.": plate_no, "Seller Name": car.get('sell_name', 'N/A'),
                "Phone Number": car.get('phone', 'N/A'), "URL": page_url
            }
            processed_data.append(car_info)

    except json.JSONDecodeError:
        print(f"(!) คำเตือน: ไม่สามารถอ่านข้อมูล JSON จากไฟล์ {input_filepath} ได้ รูปแบบไฟล์อาจไม่ถูกต้อง")
        return pd.DataFrame()
    except Exception as e:
        print(f"(!) เกิดข้อผิดพลาดร้ายแรงขณะอ่านหรือประมวลผลไฟล์ JSON: {e}")
        return pd.DataFrame()

    if not processed_data:
        print("(!) ไม่พบข้อมูลที่สามารถประมวลผลได้ในไฟล์")
        return pd.DataFrame()

    final_df = pd.DataFrame(processed_data)
    column_order = [
        "Sources", "Brand", "Model", "Sub Model", "Year",
        "Price", "Mileage", "Plate No.", "Seller Name", "Phone Number", "URL"
    ]
    final_df = final_df[column_order]
    return final_df


# ==============================================================================
#  ส่วนของ GUI (Graphical User Interface)
# ==============================================================================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Talad Rod Data Converter")
        self.geometry("700x550")

        self.input_filepath = tk.StringVar()
        self.output_filepath = tk.StringVar()

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="1. เลือกไฟล์ Input")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.input_filepath, state="readonly").pack(side=tk.LEFT, fill=tk.X,
                                                                                        expand=True, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse...", command=self.select_input_file).pack(side=tk.LEFT, padx=5, pady=5)

        output_frame = ttk.LabelFrame(main_frame, text="2. เลือกตำแหน่งและชื่อไฟล์ Output")
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_filepath, state="readonly").pack(side=tk.LEFT, fill=tk.X,
                                                                                          expand=True, padx=5, pady=5)
        ttk.Button(output_frame, text="Save As...", command=self.select_output_file).pack(side=tk.LEFT, padx=5, pady=5)

        self.process_button = ttk.Button(main_frame, text="3. เริ่มการประมวลผล", command=self.start_processing_thread)
        self.process_button.pack(fill=tk.X, padx=5, pady=10)

        # --- ส่วนของการสร้าง Log Display ---
        # นี่คือส่วนที่สร้างกล่องข้อความสำหรับแสดง Log
        log_frame = ttk.LabelFrame(main_frame, text="สถานะการทำงาน (Log)")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=15, state="disabled")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

        # --- กลไกสำคัญ: Redirect stdout และ stderr มาที่ Text Widget ---
        # บรรทัดนี้คือหัวใจของการแสดง Log ทำให้ทุกคำสั่ง print() แสดงผลในกล่องข้อความ
        sys.stdout = self.TextRedirector(self.log_text)
        sys.stderr = self.TextRedirector(self.log_text)

    def select_input_file(self):
        filepath = filedialog.askopenfilename(
            title="เลือกไฟล์ JSON Input",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            self.input_filepath.set(filepath)
            print(f"[*] เลือกไฟล์ Input: {filepath}")

    def select_output_file(self):
        filepath = filedialog.asksaveasfilename(
            title="เลือกตำแหน่งบันทึกไฟล์ CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filepath:
            self.output_filepath.set(filepath)
            print(f"[*] กำหนดไฟล์ Output: {filepath}")

    def start_processing_thread(self):
        processing_thread = threading.Thread(target=self.run_conversion)
        processing_thread.daemon = True
        processing_thread.start()

    def run_conversion(self):
        input_path = self.input_filepath.get()
        output_path = self.output_filepath.get()

        if not input_path or not output_path:
            messagebox.showerror("ผิดพลาด", "กรุณาเลือกทั้งไฟล์ Input และตำแหน่งบันทึกไฟล์ Output")
            return

        self.process_button.config(state="disabled", text="กำลังประมวลผล...")
        print("\n" + "=" * 50)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] เริ่มการทำงาน...")
        print("=" * 50)

        try:
            df = build_taladrod_database_from_json(input_path)

            if not df.empty:
                print(f"\n[*] กำลังเตรียมบันทึกไฟล์ CSV...")
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                df.to_csv(output_path, index=False, encoding='utf-8-sig')

                print("\n" + "-" * 50)
                print("การประมวลผลเสร็จสมบูรณ์!")
                print(f"ประมวลผลข้อมูลทั้งหมด {len(df)} รายการ")
                print(f"ไฟล์ผลลัพธ์ถูกบันทึกเรียบร้อยที่: '{output_path}'")
                print("-" * 50)
                messagebox.showinfo("เสร็จสิ้น",
                                    f"ประมวลผลข้อมูล {len(df)} รายการเรียบร้อย!\nไฟล์ถูกบันทึกที่:\n{output_path}")
            else:
                print("\n(!) ไม่สามารถสร้างไฟล์ผลลัพธ์ได้ เนื่องจากไม่พบข้อมูลหรือเกิดข้อผิดพลาดระหว่างการอ่านไฟล์")
                messagebox.showwarning("คำเตือน",
                                       "ไม่พบข้อมูลที่สามารถประมวลผลได้\nกรุณาตรวจสอบ Log สำหรับรายละเอียดเพิ่มเติม")

        except Exception as e:
            print(f"\n(!) เกิดข้อผิดพลาดร้ายแรงในระหว่างการทำงาน: {e}")
            messagebox.showerror("เกิดข้อผิดพลาด", f"เกิดข้อผิดพลาดร้ายแรง โปรดตรวจสอบ Log\n\nError: {e}")
        finally:
            self.process_button.config(state="normal", text="3. เริ่มการประมวลผล")

    # Class สำหรับ redirect print ไปยัง Text widget
    class TextRedirector(object):
        def __init__(self, widget):
            self.widget = widget

        def write(self, str):
            self.widget.config(state="normal")
            self.widget.insert(tk.END, str)
            self.widget.see(tk.END)  # Auto-scroll
            self.widget.config(state="disabled")

        def flush(self):
            pass


if __name__ == "__main__":
    app = App()
    app.mainloop()