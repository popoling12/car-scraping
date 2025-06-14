import time

from seleniumwire import webdriver  # ใช้ seleniumwire แทน selenium ปกติ
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import json

# Optional: configure Firefox options
firefox_options = Options()
firefox_options.add_argument("--width=1200")
firefox_options.add_argument("--height=800")
# firefox_options.add_argument("--headless")  # Uncomment to run headless

# Set up Firefox driver using WebDriver Manager
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)

driver.get('https://m.taladrod.com/car/carlist.aspx?&redirect=no')
time.sleep(5)
# JavaScript สำหรับ inject fetch API และบันทึก response (stringify)
js_code = """
return fetch(
  '/api/v1.0/cars2/carlist?fno=all&sort=y', {
    method: 'GET',
    headers: {
      'Accept': '*/*',
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    credentials: 'same-origin'
  }
)
.then(response => response.json())
.then(data => JSON.stringify(data['Cars']));
"""

result_json_str = driver.execute_script(js_code)

# บันทึกเป็นไฟล์ taladord/talarod.json
with open('talarod.json', 'w', encoding='utf-8') as f:
    f.write(result_json_str)

print("Save Complete!")