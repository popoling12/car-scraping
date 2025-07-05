import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import re
import threading

class KaideeScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Kaidee Auto Car Scraper (Firefox)")
        master.geometry("800x650") # Set initial window size

        self.driver = None
        self.token = None
        self.all_car_data = []
        self.scraping_thread = None

        # --- GUI Elements ---
        self.create_widgets()

        # Initial button states
        self.btn_get_token.config(state=tk.DISABLED)
        self.btn_scrape_data.config(state=tk.DISABLED)
        self.btn_close_browser.config(state=tk.DISABLED)
        self.entry_max_pages.config(state=tk.DISABLED)

    def create_widgets(self):
        # Frame for controls
        control_frame = tk.Frame(self.master, padx=10, pady=10)
        control_frame.pack(fill=tk.X)

        # Launch Browser Button
        self.btn_launch_browser = tk.Button(control_frame, text="1. Launch Browser", command=self.launch_browser_threaded)
        self.btn_launch_browser.pack(side=tk.LEFT, padx=5)

        # Get Token Button
        self.btn_get_token = tk.Button(control_frame, text="2. Get Token", command=self.get_token_threaded)
        self.btn_get_token.pack(side=tk.LEFT, padx=5)

        # Max Pages Entry
        tk.Label(control_frame, text="Max Pages:").pack(side=tk.LEFT, padx=5)
        self.entry_max_pages = tk.Entry(control_frame, width=5)
        self.entry_max_pages.insert(0, "5") # Default value
        self.entry_max_pages.pack(side=tk.LEFT, padx=5)

        # Scrape Data Button
        self.btn_scrape_data = tk.Button(control_frame, text="3. Scrape Data", command=self.scrape_data_threaded)
        self.btn_scrape_data.pack(side=tk.LEFT, padx=5)

        # Close Browser Button
        self.btn_close_browser = tk.Button(control_frame, text="Close Browser", command=self.close_browser)
        self.btn_close_browser.pack(side=tk.RIGHT, padx=5)

        # Separator
        tk.Frame(self.master, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

        # Log Text Area
        self.log_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=90, height=30, font=("Arial", 9))
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.log_area.config(state=tk.DISABLED) # Make it read-only

    def log_message(self, message):
        """Helper to log messages to the text area."""
        self.log_area.config(state=tk.NORMAL) # Enable for writing
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END) # Scroll to the end
        self.log_area.config(state=tk.DISABLED) # Disable after writing
        self.master.update_idletasks() # Update GUI immediately

    def launch_browser_threaded(self):
        """Starts the browser launch in a separate thread."""
        self.btn_launch_browser.config(state=tk.DISABLED) # Disable to prevent multiple clicks
        self.log_message("Launching browser in background...")
        self.scraping_thread = threading.Thread(target=self._launch_browser)
        self.scraping_thread.start()

    def _launch_browser(self):
        """Actual browser launch logic."""
        try:
            self.log_message("Setting up Firefox driver...")
            chrome_options = Options()
            # chrome_options.add_argument("--headless")  # Uncomment to run headless if needed
            chromedriver_path = os.path.join(os.getcwd(), "drivers", "chromedriver.exe")
            chrome_options.add_argument("--window-size=1200,800")
            self.driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
            # You can set window size after launching if not headless
            # self.driver.set_window_size(1200, 800)
            self.log_message("Firefox browser launched successfully.")

            self.log_message("Navigating to https://rod.kaidee.com/c11-auto-car...")
            self.driver.get('https://rod.kaidee.com/c11-auto-car')
            self.log_message(f"Current Page Title: {self.driver.title}")

            self.log_message("Navigating to https://rod.kaidee.com/c11a5-auto-car-toyota...")
            self.driver.get('https://rod.kaidee.com/c11a5-auto-car-toyota')
            self.log_message("Waiting for 5 seconds for page to load and requests to occur...")
            time.sleep(5)
            self.log_message(f"New Page Title: {self.driver.title}")
            self.log_message("Finished waiting.")

            self.master.after(0, self.enable_get_token_button) # Enable button on main thread
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Error", f"Failed to launch browser: {e}"))
            self.log_message(f"Error launching browser: {e}")
            self.master.after(0, lambda: self.btn_launch_browser.config(state=tk.NORMAL)) # Re-enable launch button
            # Added this line in case launching browser fails and you want to retry

    def enable_get_token_button(self):
        """Enables the Get Token button and input."""
        self.btn_get_token.config(state=tk.NORMAL)
        self.btn_close_browser.config(state=tk.NORMAL)
        self.entry_max_pages.config(state=tk.NORMAL)
        self.log_message("Browser is ready. Click 'Get Token' to proceed.")

    def get_token_threaded(self):
        """Starts the token collection in a separate thread."""
        if not self.driver:
            self.log_message("Error: Browser not launched. Please launch browser first.")
            return

        self.btn_get_token.config(state=tk.DISABLED) # Disable while running
        self.log_message("Collecting token from network requests in background...")
        self.scraping_thread = threading.Thread(target=self._get_token)
        self.scraping_thread.start()

    def _get_token(self):
        """Actual token collection logic."""
        self.token = None
        try:
            for request in self.driver.requests:
                if request.method == 'GET' and 'rod.kaidee.com/_next/data/' in request.url:
                    self.log_message(f"Checking URL: {request.url}")
                    match = re.search(r'/_next/data/([^/]+)/th/auto/listing\.json', request.url)
                    if match:
                        self.token = match.group(1)
                        self.log_message(f"Found token: {self.token}")
                        break

            if self.token:
                self.log_message(f"Extracted token: {self.token}")
                self.master.after(0, lambda: self.btn_scrape_data.config(state=tk.NORMAL)) # Enable scrape button
                self.log_message("Token found. You can now enter Max Pages and click 'Scrape Data'.")
            else:
                self.log_message("Token not found. The specific request might not have occurred or the URL pattern needs adjustment.")
                self.log_message("Consider increasing the initial wait time or checking other request URLs.")
                self.master.after(0, lambda: messagebox.showwarning("Token Not Found", "Token could not be extracted. Check logs for details."))

        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Error", f"Error during token collection: {e}"))
            self.log_message(f"Error during token collection: {e}")
        finally:
            # FIX APPLIED HERE: Use lambda to correctly pass state argument to config
            self.master.after(0, lambda: self.btn_get_token.config(state=tk.NORMAL)) # Re-enable get token button

    def scrape_data_threaded(self):
        """Starts the data scraping in a separate thread."""
        if not self.driver:
            self.log_message("Error: Browser not launched. Please launch browser first.")
            return
        if not self.token:
            self.log_message("Error: Token not found. Please click 'Get Token' first.")
            return

        try:
            max_page_str = self.entry_max_pages.get()
            max_page = int(max_page_str)
            if max_page < 1:
                raise ValueError("Maximum pages must be at least 1.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Invalid input for Max Pages: {e}")
            self.log_message(f"Invalid input for Max Pages: {e}")
            return

        self.btn_scrape_data.config(state=tk.DISABLED) # Disable while running
        self.all_car_data = [] # Reset data for new scrape
        self.log_message(f"Starting data scraping for {max_page} pages in background...")
        self.scraping_thread = threading.Thread(target=self._scrape_data, args=(max_page,))
        self.scraping_thread.start()

    def _scrape_data(self, max_page):
        """Actual data scraping logic."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
            'Accept': '*/*',
            'Accept-Language': 'th,en-US;q=0.7,en;q=0.3',
            'Referer': 'https://rod.kaidee.com/',
            'x-nextjs-data': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }

        for page_no in range(1, max_page + 1):
            try:
                js_code = f"""
                return fetch('https://rod.kaidee.com/_next/data/{self.token}/th/auto/listing.json?categoryId=11&attributeId=1&page={page_no}', {{
                    method: 'GET',
                    headers: {json.dumps(headers)},
                    credentials: 'include'
                }})
                .then(response => {{
                    if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
                    return response.json();
                }})
                .catch(error => ({{error: error.message}}));
                """
                response = self.driver.execute_script(js_code)

                if 'error' in response:
                    self.log_message(f"Error on page {page_no}: {response['error']}")
                    continue

                if 'pageProps' in response and 'ads' in response['pageProps']:
                    ads = response['pageProps']['ads']
                    if ads and len(ads) > 0:
                        car_ads = [ad_data for ad_data in ads if 'title' in ad_data]
                        self.all_car_data.extend(car_ads)
                        self.log_message(f"Page {page_no}: Scraped {len(car_ads)} car ads (out of {len(ads)} total items). Total collected: {len(self.all_car_data)}")
                    else:
                        self.log_message(f"Page {page_no}: No car ads found. This might be the last page.")
                        break
                else:
                    self.log_message(f"Page {page_no}: Invalid response structure or missing 'pageProps'/'ads'.")

                time.sleep(1) # Rate limiting

            except Exception as e:
                self.log_message(f"An unexpected exception occurred on page {page_no}: {str(e)}")
                continue

        self.log_message(f"\n--- Scraping Complete ---")
        self.log_message(f"Total unique car listings collected: {len(self.all_car_data)}")
        self.save_data()
        self.master.after(0, lambda: self.btn_scrape_data.config(state=tk.NORMAL)) # Re-enable scrape button
        self.master.after(0, lambda: messagebox.showinfo("Scraping Done", f"Scraping completed! Total {len(self.all_car_data)} listings collected."))

    def save_data(self):
        """Saves collected data to JSON."""
        if self.all_car_data:
            try:
                with open('rod_kaidee.json', 'w', encoding='utf-8') as f:
                    json.dump(self.all_car_data, f, ensure_ascii=False, indent=2)
                self.log_message("Data successfully saved to **rod_kaidee.json**")
            except Exception as e:
                self.log_message(f"Error saving data to file: {e}")
                self.master.after(0, lambda: messagebox.showerror("Save Error", f"Error saving data: {e}"))
        else:
            self.log_message("No data was collected to save.")

    def close_browser(self):
        """Closes the WebDriver and resets state."""
        if self.driver:
            self.log_message("Closing the browser...")
            try:
                self.driver.quit()
                self.log_message("Browser closed successfully.")
            except Exception as e:
                self.log_message(f"Error closing browser: {e}")
                messagebox.showerror("Error", f"Error closing browser: {e}")
            self.driver = None
            self.token = None
            self.all_car_data = []

        self.btn_launch_browser.config(state=tk.NORMAL)
        self.btn_get_token.config(state=tk.DISABLED)
        self.btn_scrape_data.config(state=tk.DISABLED)
        self.btn_close_browser.config(state=tk.DISABLED)
        self.entry_max_pages.config(state=tk.DISABLED)
        self.log_message("Application ready for new session.")


# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = KaideeScraperApp(root)
    root.mainloop()