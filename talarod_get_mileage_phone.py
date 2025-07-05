import json
import time
import re
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# --- Load JSON File ---
filename = 'talarod.json'

try:
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Loaded {filename} with {len(data)} entries.")
except Exception as e:
    print(f"❌ Error loading JSON: {e}")
    exit(1)

# --- Setup Chrome Driver ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=chrome_options)

# --- Loop with tqdm progress bar ---
for idx, item in enumerate(tqdm(data, desc="🚗 Processing", unit="car"), start=1):
    cid = item.get('cid')

    if not cid:
        tqdm.write(f"[{idx}] ❌ Missing CID — skipped.")
        continue

    if 'phone' in item and 'mileage' in item and 'sell_name' in item:
        tqdm.write(f"[{idx}] ⏩ CID {cid} already processed — skipping.")
        continue

    url = f"https://www.taladrod.com/w40/icar/cardet.aspx?cid={cid}"
    tqdm.write(f"[{idx}] 🌐 Visiting: {url}")

    try:
        driver.get(url)
        time.sleep(2)

        # --- Extract phone ---
        try:
            tel_element = driver.find_element(By.ID, "xTelNo")
            tel_raw = tel_element.get_attribute("innerText")
            sell_raw = driver.find_element(By.ID,'xSeller')
            phone_list = [num.strip() for num in tel_raw.split("\n") if num.strip()]
            joined_phones = ", ".join(phone_list)
        except Exception:
            joined_phones = "N/A"

        # --- Extract mileage ---
        try:
            page_text = driver.page_source
            match = re.search(r'เลขไมล์\s*([\d,\.]+)\s*กม\.', page_text)
            mileage = match.group(1) if match else "N/A"
            sell_name = sell_raw.text
        except Exception:
            mileage = "N/A"

        # --- Update item ---
        item["phone"] = joined_phones
        item["mileage"] = mileage
        item["sell_name"] = sell_name
        tqdm.write(f"[{idx}] ✅ 📞 {joined_phones} | 🛞 {mileage} | {sell_name}")

    except Exception as e:
        item["phone"] = "N/A"
        item["mileage"] = "N/A"
        item["sell_name"] = "N/A"
        tqdm.write(f"[{idx}] ❌ Error for CID {cid}: {e}")

    # --- Save after each item ---
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- Cleanup ---
driver.quit()
print(f"\n✅ All done! Updated file saved continuously to '{filename}'")
