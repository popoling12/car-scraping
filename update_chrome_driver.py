from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

DRIVER_FOLDER = os.path.join(os.getcwd(), "drivers")

driver_path = ChromeDriverManager(path=DRIVER_FOLDER).install()
driver = webdriver.Chrome(service=Service(driver_path))
driver.get("https://www.google.com")
