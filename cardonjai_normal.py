import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Create directory if it doesn't exist
os.makedirs('cardonjai', exist_ok=True)

brands = [
    {
        "brand": "Audi",
        "imgUrl": "https://media.roddonjai.com/Brands/Logo-Audi-600x338.png"
    },
    {
        "brand": "BMW",
        "imgUrl": "https://media.roddonjai.com/Brands/BMW.png"
    },
    {
        "brand": "BYD",
        "imgUrl": "https://media.roddonjai.com/Brands/BYD_Auto_Logo.png"
    },
    {
        "brand": "Chevrolet",
        "imgUrl": "https://media.roddonjai.com/Brands/logo-chevrolet.png"
    },
    {
        "brand": "Ford",
        "imgUrl": "https://media.roddonjai.com/Brands/Ford-Logo.png"
    },
    {
        "brand": "Haval",
        "imgUrl": "https://media.roddonjai.com/Brands/HAVAL-LOGO.png"
    },
    {
        "brand": "Honda",
        "imgUrl": "https://media.roddonjai.com/Brands/honda-logo-1700x1150.png"
    },
    {
        "brand": "Hyundai",
        "imgUrl": "https://media.roddonjai.com/Brands/Hyundai2.png"
    },
    {
        "brand": "Isuzu",
        "imgUrl": "https://media.roddonjai.com/Brands/Isuzu-Logo.png"
    },
    {
        "brand": "Jaguar",
        "imgUrl": "https://media.roddonjai.com/Brands/Jaguar_logo_transparent_png.png"
    },
    {
        "brand": "Kia",
        "imgUrl": "https://media.roddonjai.com/Brands/Kia_Logo_2021.png"
    },
    {
        "brand": "Land Rover",
        "imgUrl": "https://media.roddonjai.com/Brands/Land-Rover-Logo-600x338.png"
    },
    {
        "brand": "Lexus",
        "imgUrl": "https://media.roddonjai.com/Brands/Lexus-logo.png"
    },
    {
        "brand": "Mazda",
        "imgUrl": "https://media.roddonjai.com/Brands/Brand_Mark_Vertical_Primary_ver1.1.png"
    },
    {
        "brand": "Mercedes-Benz",
        "imgUrl": "https://media.roddonjai.com/Brands/Mercedes-Benz-Logo-600x338.png"
    },
    {
        "brand": "MG",
        "imgUrl": "https://media.roddonjai.com/Brands/MG-logo_UpdateJuly22.png"
    },
    {
        "brand": "Mini",
        "imgUrl": "https://media.roddonjai.com/Brands/Logo-Mini-1-600x338.png"
    },
    {
        "brand": "Mitsubishi",
        "imgUrl": "https://media.roddonjai.com/brand/20240925xjwxVybAwbiyrGmyGtOITtBpfNz.jpeg"
    },
    {
        "brand": "Neta",
        "imgUrl": "https://media.roddonjai.com/Brands/Neta.png"
    },
    {
        "brand": "Nissan",
        "imgUrl": "https://media.roddonjai.com/Brands/Logo-Nissan-1-600x338.png"
    },
    {
        "brand": "Ora",
        "imgUrl": "https://media.roddonjai.com/Brands/Ora.png"
    },
    {
        "brand": "Peugeot",
        "imgUrl": "https://media.roddonjai.com/Brands/Peugeot-Logo-600x450.png"
    },
    {
        "brand": "Porsche",
        "imgUrl": "https://media.roddonjai.com/Brands/Logo-Porsche-1-600x338.png"
    },
    {
        "brand": "Ssangyong",
        "imgUrl": "https://media.roddonjai.com/Brands/SsangYong-Logo-600x338.png"
    },
    {
        "brand": "Subaru",
        "imgUrl": "https://media.roddonjai.com/Brands/Logo-Subaru-1-600x338.png"
    },
    {
        "brand": "Suzuki",
        "imgUrl": "https://media.roddonjai.com/Brands/Suzuki.png"
    },
    {
        "brand": "Tank",
        "imgUrl": "https://media.roddonjai.com/brand/20231208bgNAhsCKfTkSXCuNAmsLElavlOx.jpeg"
    },
    {
        "brand": "Thairung",
        "imgUrl": "https://media.roddonjai.com/Brands/Thairung.png"
    },
    {
        "brand": "Toyota",
        "imgUrl": "https://media.roddonjai.com/Brands/ToyotaLogo_UpdateJul22.png"
    },
    {
        "brand": "Volkswagen",
        "imgUrl": "https://media.roddonjai.com/Brands/Logo-Volkswagen-600x338.png"
    },
    {
        "brand": "Volvo",
        "imgUrl": "https://media.roddonjai.com/Brands/Fullversion-VolvoSpreadWordMarkBlack.jpg"
    }
]


def setup_driver():
    """Setup Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Remove this line if you want to see the browser
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def fetch_brand_data(driver, brand_name, page_size=100):
    """Fetch all data for a specific brand"""
    print(f"Fetching data for {brand_name}...")

    # First request to get total pages
    js_code_first = f"""
    return fetch('https://api-buyer.roddonjai.com/api-gateway/buyer/home-page/search-car-profile-advance', {{
        method: 'POST',
        headers: {{
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://www.roddonjai.com',
            'Referer': 'https://www.roddonjai.com/'
        }},
        body: JSON.stringify({{
            "pageNo": 1,
            "pageSize": {page_size},
            "keyword": "",
            "brandList": ["{brand_name}"],
            "modelList": [],
            "subModelList": [],
            "carFuelList": [],
            "carTypeList": null,
            "colorCodeList": null,
            "gearList": null,
            "inspectionScore": null,
            "sellingPointList": null,
            "sellerSubType": null,
            "minMileage": "",
            "maxMileage": "",
            "locationId": "",
            "carInterestList": null,
            "yearFrom": "",
            "yearTo": "",
            "sortedBy": "",
            "isExcellentPrice": false,
            "isGoodPrice": false,
            "isFairPrice": false,
            "provinceList": null,
            "location": null,
            "maxPrice": "20000000",
            "minPrice": "0"
        }}),
        credentials: 'include'
    }})
    .then(response => response.json())
    .then(data => data)
    .catch(error => ({{error: error.message}}));
    """

    try:
        # Navigate to the site first to establish session
        driver.get('https://www.roddonjai.com')
        time.sleep(2)

        response = driver.execute_script(js_code_first)

        if 'error' in response:
            print(f"Error fetching {brand_name}: {response['error']}")
            return []

        if 'getCarProfile' not in response:
            print(f"No car profile data found for {brand_name}")
            return []

        total_pages = response['getCarProfile']['totalPages']
        total_elements = response['getCarProfile']['totalElements']

        print(f"  - Total pages: {total_pages}")
        print(f"  - Total cars: {total_elements}")

        all_cars_data = []

        # Collect data from all pages
        for page_no in range(1, total_pages + 1):
            print(f"  - Fetching page {page_no}/{total_pages}")

            js_code_page = f"""
            return fetch('https://api-buyer.roddonjai.com/api-gateway/buyer/home-page/search-car-profile-advance', {{
                method: 'POST',
                headers: {{
                    'Accept': 'application/json, text/plain, */*',
                    'Content-Type': 'application/json',
                    'Origin': 'https://www.roddonjai.com',
                    'Referer': 'https://www.roddonjai.com/'
                }},
                body: JSON.stringify({{
                    "pageNo": {page_no},
                    "pageSize": {page_size},
                    "keyword": "",
                    "brandList": ["{brand_name}"],
                    "modelList": [],
                    "subModelList": [],
                    "carFuelList": [],
                    "carTypeList": null,
                    "colorCodeList": null,
                    "gearList": null,
                    "inspectionScore": null,
                    "sellingPointList": null,
                    "sellerSubType": null,
                    "minMileage": "",
                    "maxMileage": "",
                    "locationId": "",
                    "carInterestList": null,
                    "yearFrom": "",
                    "yearTo": "",
                    "sortedBy": "",
                    "isExcellentPrice": false,
                    "isGoodPrice": false,
                    "isFairPrice": false,
                    "provinceList": null,
                    "location": null,
                    "maxPrice": "20000000",
                    "minPrice": "0"
                }}),
                credentials: 'include'
            }})
            .then(response => response.json())
            .then(data => data)
            .catch(error => ({{error: error.message}}));
            """

            page_response = driver.execute_script(js_code_page)

            if 'error' in page_response:
                print(f"    Error on page {page_no}: {page_response['error']}")
                continue

            if 'getCarProfile' in page_response and 'content' in page_response['getCarProfile']:
                cars_data = page_response['getCarProfile']['content']
                all_cars_data.extend(cars_data)
                print(f"    Added {len(cars_data)} cars from page {page_no}")

            # Add small delay to avoid rate limiting
            time.sleep(1)

        print(f"  - Total collected: {len(all_cars_data)} cars")
        return all_cars_data

    except Exception as e:
        print(f"Exception while fetching {brand_name}: {str(e)}")
        return []


def main():
    """Main function to process all brands"""
    driver = setup_driver()

    try:
        for brand in brands:
            brand_name = brand["brand"]

            # Fetch all data for this brand
            current_brands_data = fetch_brand_data(driver, brand_name)

            if current_brands_data:
                # Save to JSON file with UTF-8 encoding
                filename = f"cardonjai/{brand_name}.json"

                # Create data structure
                brand_data = {
                    "brand": brand_name,
                    "imgUrl": brand["imgUrl"],
                    "totalCars": len(current_brands_data),
                    "cars": current_brands_data,
                    "fetchedAt": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                with open(filename, 'w', encoding='utf-8-sig') as f:
                    json.dump(brand_data, f, ensure_ascii=False, indent=2)

                print(f"✅ Saved {len(current_brands_data)} cars for {brand_name} to {filename}")
            else:
                print(f"❌ No data collected for {brand_name}")

            # Add delay between brands to be respectful
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nScript interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        driver.quit()
        print("Driver closed")


if __name__ == "__main__":
    main()