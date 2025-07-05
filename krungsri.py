from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import pandas as pd

# Optional: configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--window-size=1200,800")
# chrome_options.add_argument("--headless")  # Uncomment to run headless

# Set up Chrome driver using WebDriver Manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# --- Navigate to the initial page first ---
print("Navigating to the Krungsri Market Used Car Warehouse page...")
driver.get('https://krungsrimarket.cjdataservice.com/usedcar/warehouse')

# Ask user for the number of pages to scrape
while True:
    try:
        total_page_number = int(input("Enter the number of pages you want to scrape (e.g., if there are 100 pages, you can enter 100): "))
        if total_page_number > 0:
            break
        else:
            print("Please enter a positive number.")
    except ValueError:
        print("Invalid input. Please enter a whole number.")

all_data = []

print(f"\nStarting to scrape {total_page_number} pages...")
for index in range(1, total_page_number + 1):
    print(f"Scraping page {index}...")
    driver.get(f'https://krungsrimarket.cjdataservice.com/usedcar/warehouse?page={index}')

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'clickable-row'))
        )
    except Exception as e:
        print(f"Could not find elements on page {index}. Skipping to next page. Error: {e}")
        continue

    rows = driver.find_elements(By.CLASS_NAME, 'clickable-row')
    if not rows:
        print(f"No data rows found on page {index}. It might be the end or an empty page.")
        if index > 1:
            print("Stopping scraping as no more data rows were found.")
            break

    for row in rows:
        data = {}
        tds = row.find_elements(By.TAG_NAME, "td")

        if len(tds) >= 5:
            data['index'] = tds[0].text.strip()
            data['brand'] = tds[1].text.strip()
            data['model'] = tds[2].text.strip()
            data['mileage'] = tds[3].text.strip()
            data['price_range'] = tds[4].text.strip()
            data['link'] = row.get_attribute('data-href')

            all_data.append(data)

driver.quit()

print("\n--- Scraped Data Summary ---")
if all_data:
    print(f"Successfully scraped {len(all_data)} records.")
else:
    print("No data was scraped.")

# Save to CSV
if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv('krungsrimarket_demo.csv', encoding='utf-8-sig', index=False)
    print(f"Data successfully saved to krungsrimarket_demo.csv. Total {len(all_data)} records.")
else:
    print("No data to save to CSV.")
