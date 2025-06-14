from bs4 import BeautifulSoup
import json
import os
import time
from selenium import webdriver  # Assuming you'll import webdriver for actual use
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_one2car_page(driver, page_number):
    """Scrape single page and return extracted data"""
    url = f'https://www.one2car.com/%E0%B8%A3%E0%B8%96-%E0%B8%AA%E0%B8%B3%E0%B8%AB%E0%B8%A3%E0%B8%B1%E0%B8%9A-%E0%B8%82%E0%B8%B2%E0%B8%A2?page_size=50&page_number={page_number}'

    try:
        driver.get(url)
        # รอให้หน้าโหลดเสร็จ
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "script"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        json_ld_scripts = soup.find_all('script', type='application/ld+json')

        extracted_data = []
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                # ตรวจสอบว่ามี itemListElement หรือไม่
                if isinstance(data, list) and len(data) > 1 and 'itemListElement' in data[1]:
                    cars = data[1]['itemListElement']

                    for car in cars:
                        item = car['item']
                        extracted_data.append({
                            'name': item.get('name'),
                            'model': item.get('model'),
                            'year': item.get('vehicleModelDate'),
                            'price': item.get('offers', {}).get('price'),
                            'currency': item.get('offers', {}).get('priceCurrency'),
                            'mileage_km': item.get('mileageFromOdometer', {}).get('value') if item.get(
                                'mileageFromOdometer') else None,
                            'color': item.get('color'),
                            'body_type': item.get('bodyType'),
                            'fuel_type': item.get('fuelType'),
                            'seating_capacity': item.get('seatingCapacity'),
                            'brand': item.get('brand', {}).get('name'),
                            'location': item.get('offers', {}).get('seller', {}).get('homeLocation', {}).get('address',
                                                                                                             {}).get(
                                'addressLocality'),
                            'region': item.get('offers', {}).get('seller', {}).get('homeLocation', {}).get('address',
                                                                                                           {}).get(
                                'addressRegion'),
                            'dealer_url': item.get('offers', {}).get('seller', {}).get('homeLocation', {}).get(
                                'address', {}).get('url'),
                            'page_url': item.get('mainEntityOfPage'),
                            'image_url': item.get('image', [None])[0] if item.get('image') else None,
                            'description': item.get('description')
                        })

            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error on page {page_number}:", e)
                continue

        return extracted_data

    except Exception as e:
        print(f"❌ Error scraping page {page_number}:", e)
        return []


def scrape_all_pages(driver, start_page=1, end_page=None):  # Changed end_page default to None
    """Scrape all pages and save to JSON files"""

    # สร้างโฟลเดอร์ one2car ถ้ายังไม่มี
    os.makedirs('one2car', exist_ok=True)

    # If end_page is not provided, prompt the user for it
    if end_page is None:
        while True:
            try:
                user_input = input("Please enter the end page number for scraping: ")
                end_page = int(user_input)
                if end_page < start_page:
                    print(
                        f"The end page ({end_page}) cannot be less than the start page ({start_page}). Please try again.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a valid integer for the end page.")

    for page_num in range(start_page, end_page + 1):
        print(f"🔄 Scraping page {page_num}/{end_page}")

        # ตรวจสอบว่าไฟล์นี้มีอยู่แล้วหรือไม่
        file_path = f'one2car/{page_num}.json'
        if os.path.exists(file_path):
            print(f"⏭️  Page {page_num} already exists, skipping...")
            continue

        # Scrape หน้านี้
        data = scrape_one2car_page(driver, page_num)

        if data:
            # บันทึกเป็นไฟล์ JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Saved {len(data)} cars from page {page_num}")
        else:
            print(f"⚠️  No data found on page {page_num}")

        # หน่วงเวลาเพื่อไม่ให้ server โดน rate limit
        time.sleep(2)


# เรียกใช้งาน
if __name__ == "__main__":
    # จำเป็นต้องสร้าง driver ก่อนเรียกใช้ฟังก์ชัน scrape_all_pages
    # ตัวอย่างการสร้าง Chrome driver (ต้องติดตั้ง ChromeDriver และระบุ path หรืออยู่ใน PATH)
    try:
        # For headless Browse (no browser window)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        # Or for visible browser:
        # driver = webdriver.Chrome()

        scrape_all_pages(driver, start_page=1)  # Now end_page is prompted from user
        print("🎉 Scraping completed!")

    except Exception as e:
        print(f"An error occurred during WebDriver setup or execution: {e}")
        print(
            "Please ensure you have ChromeDriver installed and it's accessible in your system's PATH, or specify its path.")
    finally:
        if 'driver' in locals() and driver:
            driver.quit()  # Close the browser when done