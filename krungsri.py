from seleniumwire import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import pandas as pd

# Optional: configure Firefox options
firefox_options = Options()
firefox_options.add_argument("--width=1200")
firefox_options.add_argument("--height=800")
# firefox_options.add_argument("--headless")  # Uncomment to run headless

# Set up Firefox driver using WebDriver Manager
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)

# --- Navigate to the initial page first ---
print("Navigating to the Krungsri Market Used Car Warehouse page...")
driver.get('https://krungsrimarket.cjdataservice.com/usedcar/warehouse')

# Give the user time to view the page and total page number (optional, but helpful)
print("\nPlease observe the total number of pages on the website.")
# You might want to add a short delay here to ensure the user has time to see it,
# or ask them to confirm they've seen it.
# For now, we'll just prompt for input immediately after.

# --- User Input for total_page_number ---
while True:
    try:
        total_page_number = int(input("Enter the number of pages you want to scrape (e.g., if there are 100 pages, you can enter 100): "))
        if total_page_number > 0:
            break
        else:
            print("Please enter a positive number.")
    except ValueError:
        print("Invalid input. Please enter a whole number.")
# --- End of User Input ---

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
    if not rows: # Check if no rows were found on the page
        print(f"No data rows found on page {index}. It might be the end or an empty page.")
        if index > 1: # If it's not the first page and no rows, it's likely the end
            print("Stopping scraping as no more data rows were found.")
            break # Exit the loop if no rows are found on subsequent pages

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

# Close the browser after scraping
driver.quit()

# Display all scraped data (optional, for verification)
print("\n--- Scraped Data Summary ---")
if all_data:
    print(f"Successfully scraped {len(all_data)} records.")
    # You could print a few samples here if the list is very long
    # for item in all_data[:5]: # Print first 5 items
    #     print(item)
else:
    print("No data was scraped.")


# Create DataFrame and save to CSV
if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv('krungsrimarket_demo.csv', encoding='utf-8-sig', index=False)
    print(f"Data successfully saved to krungsrimarket_demo.csv. Total {len(all_data)} records.")
else:
    print("No data to save to CSV.")