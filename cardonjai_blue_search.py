import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ensure output folder exists
os.makedirs('blue_search', exist_ok=True)

PAGE_SIZE = 4

def setup_driver():
    opts = Options()
    # comment out headless so you can see errors
    # opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=opts)
    driver.set_script_timeout(30)
    # mask webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get:()=>undefined});")
    return driver

def fetch_page_sync(driver, page_no):
    js = f"""
    try {{
      var xhr = new XMLHttpRequest();
      xhr.open("POST",
        "https://api-buyer.roddonjai.com/api-gateway/buyer/service-page/search-bluebook-card?pageNo={page_no}&pageSize={PAGE_SIZE}",
        false
      );
      xhr.setRequestHeader("Accept", "application/json");
      xhr.setRequestHeader("Content-Type", "application/json");
      xhr.setRequestHeader("Origin", "https://www.roddonjai.com");
      xhr.setRequestHeader("Referer", "https://www.roddonjai.com/");
      xhr.withCredentials = true;

      // build the payload in JS and stringify it
      var payload = {{
        keyword: "",
        bluebookCode: "",
        carType: "",
        carSubSegment: "",
        brand: "",
        carModel: "",
        yearStart: "",
        yearEnd: "",
        carSubModel: "",
        carGear: [{{code:"M"}}, {{code:"A"}}],
        carPrice: null,
        carPriceFrom: 0,
        carPriceTo: 20000000,
        termPaymentPrice: "",
        sortType: ""
      }};
      xhr.send(JSON.stringify(payload));

      if (xhr.status === 200) {{
        var resp = JSON.parse(xhr.responseText);
        return resp.searchBluebookCard; 
      }} else {{
        return {{ error: "HTTP " + xhr.status }};
      }}
    }} catch(e) {{
      return {{ error: e.message }};
    }}
    """
    return driver.execute_script(js)

def main():
    driver = setup_driver()
    try:
        # 1) Establish session/cookies
        driver.get("https://www.roddonjai.com")
        time.sleep(2)

        # 2) Bootstrap to find totalPages
        first = fetch_page_sync(driver, 1)
        if not first or "error" in first:
            raise RuntimeError("Bootstrap failed: " + (first or {}).get("error", "no response"))
        total_pages = first["result"]["totalPages"]
        print(f"Total pages = {total_pages}")

        # 3) Loop and save only the content array
        for p in range(1, total_pages + 1):
            print(f"Fetching page {p}/{total_pages}…")
            resp = fetch_page_sync(driver, p)
            if not resp or "error" in resp:
                print(f"  ❌ Page {p} error: {resp.get('error')}")
                continue

            content = resp["result"]["content"]
            path = f"blue_search/{p}.json"
            with open(path, "w", encoding="utf-8-sig") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            print(f"  ✅ Saved {len(content)} items to {path}")

            time.sleep(1)

    finally:
        driver.quit()
        print("Done.")

if __name__ == "__main__":
    main()
    import os
    import json

    # Folder containing the individual page files
    folder = 'blue_search'
    combined = []

    # Check if folder exists
    if not os.path.isdir(folder):
        print(f"Folder '{folder}' does not exist. Please run the scraper first.")
    else:
        # Read each JSON file and extend the combined list
        for filename in sorted(os.listdir(folder),
                               key=lambda x: int(os.path.splitext(x)[0]) if x.endswith('.json') else -1):
            if filename.endswith('.json') and filename != 'combined.json':
                path = os.path.join(folder, filename)
                with open(path, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    combined.extend(data)
        # Write out the merged data
        output_path = os.path.join(folder, 'combined.json')
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)

        print(f"✅ Combined {len(combined)} records into '{output_path}'")

