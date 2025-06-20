from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import json
import time
from tqdm import tqdm

# โหลด URL จากไฟล์ JSON
# โหลด URL จากไฟล์ JSON (เอาแค่ 5 ลิงก์แรก)
with open("taladrod_links.json", "r", encoding="utf-8") as f:
    car_urls = json.load(f)  # แก้ตรงนี้ เอาแค่ 5 ลิงก์


# ตั้งค่า Selenium Headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(options=chrome_options)

all_cars = []

for idx, url in enumerate(tqdm(car_urls, desc="🚗 ดึงข้อมูลรถ", unit="url"), start=1):
    try:
        driver.get(url)
        time.sleep(2)  # รอ JavaScript โหลด (ปรับได้)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        script_tag = soup.find('script', text=re.compile(r'SchDataJSON'))

        if not script_tag:
            tqdm.write(f"[{idx}] ⚠️ ไม่พบ script SchDataJSON ใน: {url}")
            continue

        match = re.search(r'var SchDataJSON\s*=\s*(\{.*?\});', script_tag.string, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            car_count = 0
            for car in data.get('cars', []):
                car_info = {
                    "year": car.get('yr4'),
                    "title": car.get('title'),
                    "price": car.get('prc'),
                    "image": car.get('img'),
                    "url": url
                }
                all_cars.append(car)
                car_count += 1

            tqdm.write(f"[{idx}] ✅ {car_count} คันจาก: {url}")
        else:
            tqdm.write(f"[{idx}] ❌ ไม่พบข้อมูล JSON ใน: {url}")
    except Exception as e:
        tqdm.write(f"[{idx}] ❌ Error: {e}")

driver.quit()

# บันทึกผลลงไฟล์
with open("talarod_cars.json", "w", encoding="utf-8") as f:
    json.dump(all_cars, f, ensure_ascii=False, indent=2)

print(f"\n✅ เสร็จสิ้น ดึงข้อมูลรถทั้งหมด {len(all_cars)} คัน → talarod_cars.json")
