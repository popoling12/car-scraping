import json
import time

# --- CONFIG ---
INPUT_FILE = 'taladrod_links.json'
OUTPUT_FILE = 'taladrod_complete_links.json'

# --- SETUP CHROME WITH WEBDRIVER MANAGER ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome Options
options = Options()
options.add_argument('--headless')  # Remove this line if you want to see the browser
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Use Service wrapper for ChromeDriverManager
service = Service(ChromeDriverManager().install())

# Create WebDriver with service and options
driver = webdriver.Chrome(service=service, options=options)


# --- READ JSON URL LIST ---
with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
    url_list = json.load(f)

results = []

# --- FETCH TITLE FOR EACH URL ---
for url in url_list:
    try:
        driver.get(url)
        time.sleep(2)  # wait for page to load
        title = driver.title
        results.append({'link': url, 'title': title})
        print(f"✅ {url} --> {title}")
    except Exception as e:
        print(f"❌ Error with {url}: {e}")
        results.append({'link': url, 'title': None})

# --- SAVE RESULTS TO OUTPUT FILE ---
with open(OUTPUT_FILE, 'w', encoding='utf-8-sig') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

driver.quit()
print(f"\n📁 Saved titles to {OUTPUT_FILE}")
