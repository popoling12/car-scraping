import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import time
import re
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# --- คลาสสำหรับสร้างแอปพลิเคชัน GUI ---
class CarScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("TaladRod Scraper GUI")
        master.geometry("800x600")

        self.data = []
        self.filepath = None
        self.driver = None
        self.is_running = False

        # --- 1. ส่วนเลือกไฟล์ ---
        self.file_frame = tk.Frame(master, padx=10, pady=10)
        self.file_frame.pack(fill=tk.X)

        self.label_file = tk.Label(self.file_frame, text="JSON File:")
        self.label_file.pack(side=tk.LEFT, padx=(0, 5))

        self.entry_path = tk.Entry(self.file_frame, state='readonly', width=70)
        self.entry_path.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.btn_browse = tk.Button(self.file_frame, text="Browse...", command=self.load_file)
        self.btn_browse.pack(side=tk.LEFT, padx=(5, 0))

        # --- 2. ส่วนแสดงรายการรถและปุ่มเลือกทั้งหมด ---
        self.list_frame = tk.Frame(master, padx=10, pady=5)
        self.list_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox_label = tk.Label(self.list_frame, text="Select cars to scrape:")
        self.listbox_label.pack(anchor=tk.W)

        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(self.list_frame, selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.listbox.yview)

        self.btn_select_all = tk.Button(self.list_frame, text="Select/Deselect All", command=self.toggle_select_all)
        self.btn_select_all.pack(pady=5)

        # --- 3. ส่วนปุ่มเริ่มทำงาน ---
        self.action_frame = tk.Frame(master, padx=10, pady=5)
        self.action_frame.pack(fill=tk.X)

        self.btn_start = tk.Button(self.action_frame, text="Start Scraping Selected Cars", bg="#4CAF50", fg="white",
                                   font=('Helvetica', 10, 'bold'), command=self.start_scraping_thread)
        self.btn_start.pack(fill=tk.X, ipady=5)

        # --- 4. ส่วนแสดงผล Log ---
        self.log_frame = tk.Frame(master, padx=10, pady=10)
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_label = tk.Label(self.log_frame, text="Log:")
        self.log_label.pack(anchor=tk.W)

        self.log_widget = scrolledtext.ScrolledText(self.log_frame, state='disabled', height=10, wrap=tk.WORD)
        self.log_widget.pack(fill=tk.BOTH, expand=True)

        # --- จัดการการปิดโปรแกรม ---
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        """เพิ่มข้อความลงใน Log widget อย่างปลอดภัยจาก Thread อื่น"""
        self.log_widget.config(state='normal')
        self.log_widget.insert(tk.END, message + '\n')
        self.log_widget.config(state='disabled')
        self.log_widget.see(tk.END)  # Auto-scroll

    def load_file(self):
        """เปิดหน้าต่างเพื่อเลือกไฟล์ JSON"""
        filepath = filedialog.askopenfilename(
            title="Select a JSON file",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if not filepath:
            return

        self.filepath = filepath
        self.entry_path.config(state='normal')
        self.entry_path.delete(0, tk.END)
        self.entry_path.insert(0, self.filepath)
        self.entry_path.config(state='readonly')

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.log(f"✅ Loaded {self.filepath} with {len(self.data)} entries.")
            self.populate_listbox()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load or parse JSON file:\n{e}")
            self.log(f"❌ Error loading JSON: {e}")

    def populate_listbox(self):
        """แสดงรายการรถใน Listbox"""
        self.listbox.delete(0, tk.END)
        for i, item in enumerate(self.data):
            # ตรวจสอบว่ามีข้อมูลครบแล้วหรือยัง
            status = "✅" if 'phone' in item and item.get(
                'phone') != 'N/A' and 'mileage' in item and 'sell_name' in item else "⏳"

            # สร้างข้อความที่สื่อความหมายมากขึ้น
            display_text = f"[{i + 1}] {status} CID: {item.get('cid', 'N/A')} - {item.get('brand_name', '')} {item.get('model_name', '')}"
            self.listbox.insert(tk.END, display_text)

    def toggle_select_all(self):
        """เลือก หรือ ยกเลิกการเลือกทั้งหมด"""
        if len(self.listbox.curselection()) == self.listbox.size():
            self.listbox.selection_clear(0, tk.END)
        else:
            self.listbox.selection_set(0, tk.END)

    def start_scraping_thread(self):
        """เริ่มการทำงาน Scraping ใน Thread ใหม่"""
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select at least one car to scrape.")
            return

        if self.is_running:
            messagebox.showwarning("In Progress", "Scraping is already in progress.")
            return

        self.is_running = True
        self.btn_start.config(state='disabled', text="Scraping in progress...")

        # สร้างและเริ่ม Thread
        scrape_thread = threading.Thread(target=self.run_scraping, args=(selected_indices,), daemon=True)
        scrape_thread.start()

    def run_scraping(self, selected_indices):
        """กระบวนการ Scraping ที่จะรันใน Background Thread"""
        self.log("\n--- Starting Scraping Process ---")
        try:
            # --- Setup Chrome Driver ---
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            self.log(
                f"❌ Critical Error: Could not start WebDriver. Please check your Chrome/ChromeDriver installation. Error: {e}")
            self.master.after(0, self.scraping_finished)  # เรียกฟังก์ชันจบการทำงานใน Main thread
            return

        total_selected = len(selected_indices)
        for i, list_idx in enumerate(selected_indices):
            item_index = list_idx  # Index ใน self.data ตรงกับใน listbox
            item = self.data[item_index]
            cid = item.get('cid')

            self.log(f"--- ({i + 1}/{total_selected}) Processing CID: {cid} ---")

            if not cid:
                self.log(f"[{item_index + 1}] ❌ Missing CID — skipped.")
                continue

            # ใช้ `get` เพื่อป้องกัน lỗi ถ้า key ไม่มีอยู่
            if item.get('phone') and item.get('mileage') and item.get('sell_name'):
                if item['phone'] != 'N/A' and item['mileage'] != 'N/A' and item['sell_name'] != 'N/A':
                    self.log(f"[{item_index + 1}] ⏩ CID {cid} already has full data — skipping.")
                    continue

            url = f"https://www.taladrod.com/w40/icar/cardet.aspx?cid={cid}"
            self.log(f"[{item_index + 1}] 🌐 Visiting: {url}")

            try:
                driver.get(url)
                time.sleep(2)  # รอให้หน้าเว็บโหลดสมบูรณ์

                # --- Extract phone ---
                try:
                    tel_element = driver.find_element(By.ID, "xTelNo")
                    tel_raw = tel_element.get_attribute("innerText")
                    phone_list = [num.strip() for num in tel_raw.split("\n") if num.strip()]
                    joined_phones = ", ".join(phone_list)
                except Exception:
                    joined_phones = "N/A"

                # --- Extract mileage and seller ---
                try:
                    sell_raw = driver.find_element(By.ID, 'xSeller')
                    sell_name = sell_raw.text
                    page_text = driver.page_source
                    match = re.search(r'เลขไมล์\s*([\d,\.]+)\s*กม\.', page_text)
                    mileage = match.group(1).replace(',', '') if match else "N/A"
                except Exception:
                    mileage = "N/A"
                    sell_name = "N/A"

                # --- Update item ---
                item["phone"] = joined_phones
                item["mileage"] = mileage
                item["sell_name"] = sell_name
                self.log(f"[{item_index + 1}] ✅ 📞 {joined_phones} | 🛞 {mileage} km | 👤 {sell_name}")

                # --- อัปเดต Listbox ใน Main Thread ---
                self.master.after(0, self.update_listbox_item, item_index, item)

            except Exception as e:
                item["phone"] = "N/A"
                item["mileage"] = "N/A"
                item["sell_name"] = "N/A"
                self.log(f"[{item_index + 1}] ❌ Error for CID {cid}: {e}")

            # --- Save after each item ---
            try:
                with open(self.filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
                self.log(f"💾 Saved progress to {self.filepath}")
            except Exception as e:
                self.log(f"❌ Error saving file: {e}")

        # --- Cleanup ---
        driver.quit()
        self.log("\n✅ All selected cars processed! Updated file saved.")
        self.master.after(0, self.scraping_finished)  # เรียกฟังก์ชันจบการทำงานใน Main thread

    def update_listbox_item(self, index, item):
        """อัปเดตข้อความใน Listbox หนึ่งบรรทัด"""
        status = "✅" if item.get('phone') != 'N/A' else "⏳"
        display_text = f"[{index + 1}] {status} CID: {item.get('cid', 'N/A')} - {item.get('brand_name', '')} {item.get('model_name', '')}"
        self.listbox.delete(index)
        self.listbox.insert(index, display_text)

    def scraping_finished(self):
        """คืนค่าปุ่มและสถานะเมื่อการทำงานเสร็จสิ้น"""
        self.is_running = False
        self.btn_start.config(state='normal', text="Start Scraping Selected Cars")

    def on_closing(self):
        """จัดการเมื่อผู้ใช้กดปิดหน้าต่าง"""
        if self.is_running:
            if messagebox.askokcancel("Quit?", "Scraping is in progress. Are you sure you want to quit?"):
                self.master.destroy()
        else:
            self.master.destroy()


# --- ส่วนหลักในการรันโปรแกรม ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CarScraperApp(root)
    root.mainloop()