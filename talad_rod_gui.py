import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import json
import threading
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

class CarScraperGUI:
    def __init__(self, master):
        self.master = master
        master.title("Taladrod Car Scraper")
        master.geometry("1000x700")

        self.car_urls = []
        self.running_scraper = False
        self.stop_event = threading.Event()

        # --- Define checkbox characters ---
        self.CHECK_CHAR = "☑"
        self.UNCHECK_CHAR = "☐"

        # --- Link Selection Frame ---
        self.link_frame = ttk.LabelFrame(master, text="Select URLs")
        self.link_frame.pack(padx=10, pady=10, fill="x", expand=False)

        # --- Treeview for URLs ---
        # Note: We are no longer using the 'image' option in the treeview
        self.tree = ttk.Treeview(self.link_frame, columns=("Checkbox", "URL"), show="headings", selectmode="none")
        self.tree.heading("Checkbox", text="Select", anchor=tk.CENTER)
        self.tree.heading("URL", text="Car URL", anchor=tk.W)
        self.tree.column("Checkbox", width=70, stretch=tk.NO, anchor=tk.CENTER)
        self.tree.column("URL", width=800, stretch=tk.YES)
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree_scrollbar = ttk.Scrollbar(self.link_frame, orient="vertical", command=self.tree.yview)
        self.tree_scrollbar.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=self.tree_scrollbar.set)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

        # --- Control Buttons for URL selection ---
        self.url_control_frame = ttk.Frame(master)
        self.url_control_frame.pack(pady=5, padx=10, fill="x")

        self.load_urls_button = ttk.Button(self.url_control_frame, text="Load URLs", command=self.load_urls)
        self.load_urls_button.pack(side="left", padx=5)

        self.select_all_button = ttk.Button(self.url_control_frame, text="Select All", command=self.select_all_urls)
        self.select_all_button.pack(side="left", padx=5)

        self.deselect_all_button = ttk.Button(self.url_control_frame, text="Deselect All", command=self.deselect_all_urls)
        self.deselect_all_button.pack(side="left", padx=5)

        # --- Main Control Buttons Frame ---
        self.control_frame = ttk.Frame(master)
        self.control_frame.pack(pady=10)

        self.start_button = ttk.Button(self.control_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side="left", padx=10)

        self.stop_button = ttk.Button(self.control_frame, text="Stop Scraping", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side="left", padx=10)

        # --- Progress Bar ---
        self.progress_bar = ttk.Progressbar(master, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=5)

        # --- Log Display Frame ---
        self.log_frame = ttk.LabelFrame(master, text="Logs and Errors")
        self.log_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, height=15)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state=tk.DISABLED)

        # Configure tags for colored text
        self.log_text.tag_config("red", foreground="red")
        self.log_text.tag_config("green", foreground="green")
        self.log_text.tag_config("blue", foreground="blue")
        self.log_text.tag_config("orange", foreground="orange")

    def load_urls(self):
        file_path = filedialog.askopenfilename(
            initialdir="./",
            title="Select taladrod_links.json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.car_urls = json.load(f)
                self.tree.delete(*self.tree.get_children())
                for url in self.car_urls:
                    self.tree.insert("", "end", values=[self.UNCHECK_CHAR, url])
                self.log("URLs loaded successfully.", "green")
            except Exception as e:
                self.log(f"Error loading URLs: {e}", "red")

    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # Column 1 is "Checkbox"
                item_id = self.tree.identify_row(event.y)
                if item_id:
                    current_value = self.tree.item(item_id, "values")[0]
                    url = self.tree.item(item_id, "values")[1]
                    if current_value == self.UNCHECK_CHAR:
                        self.tree.item(item_id, values=[self.CHECK_CHAR, url])
                    else:
                        self.tree.item(item_id, values=[self.UNCHECK_CHAR, url])

    def select_all_urls(self):
        for item_id in self.tree.get_children():
            url = self.tree.item(item_id, "values")[1]
            self.tree.item(item_id, values=[self.CHECK_CHAR, url])

    def deselect_all_urls(self):
        for item_id in self.tree.get_children():
            url = self.tree.item(item_id, "values")[1]
            self.tree.item(item_id, values=[self.UNCHECK_CHAR, url])

    def get_selected_urls(self):
        selected = []
        for item_id in self.tree.get_children():
            if self.tree.item(item_id, "values")[0] == self.CHECK_CHAR:
                selected.append(self.tree.item(item_id, "values")[1])
        return selected

    def log(self, message, color="black"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", color)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_scraping(self):
        selected_urls = self.get_selected_urls()
        if not selected_urls:
            self.log("Please select at least one URL to scrape.", "red")
            return

        if self.running_scraper:
            self.log("Scraper is already running.", "orange")
            return

        self.running_scraper = True
        self.stop_event.clear()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0

        threading.Thread(target=self._run_scraper_thread, args=(selected_urls,), daemon=True).start()

    def stop_scraping(self):
        self.stop_event.set()
        self.log("Scraping stop requested. Waiting for current operation to finish...", "orange")

    def _run_scraper_thread(self, urls_to_scrape):
        all_cars = []
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920x1080")

        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            total_urls = len(urls_to_scrape)
            self.progress_bar["maximum"] = total_urls

            for idx, url in enumerate(urls_to_scrape, start=1):
                if self.stop_event.is_set():
                    self.log("Scraping stopped by user.", "blue")
                    break

                try:
                    driver.get(url)
                    time.sleep(2)

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    script_tag = soup.find('script', text=re.compile(r'SchDataJSON'))

                    if not script_tag:
                        self.log(f"[{idx}] ⚠️ Cannot find SchDataJSON script in: {url}", "orange")
                        continue

                    match = re.search(r'var SchDataJSON\s*=\s*(\{.*?\});', script_tag.string, re.DOTALL)
                    if match:
                        data = json.loads(match.group(1))
                        car_count = 0
                        for car in data.get('cars', []):

                            all_cars.append(car)
                            car_count += 1
                        self.log(f"[{idx}] ✅ {car_count} cars from: {url}", "green")
                    else:
                        self.log(f"[{idx}] ❌ Cannot find JSON data in: {url}", "red")
                except Exception as e:
                    self.log(f"[{idx}] ❌ Error processing {url}: {e}", "red")
                finally:
                    self.master.after(0, lambda: self.progress_bar.step(1))

            if all_cars:
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    title="Save Car Data As..."
                )
                if save_path:
                    with open(save_path, "w", encoding="utf-8") as f:
                        json.dump(all_cars, f, ensure_ascii=False, indent=2)
                    self.log(f"\n✅ Finished! Scraped {len(all_cars)} cars → {save_path}", "green")
                else:
                    self.log("\n⚠️ Save cancelled by user.", "orange")
            else:
                self.log("\nNo cars were scraped.", "blue")

        except Exception as e:
            self.log(f"Fatal error during scraping: {e}", "red")
        finally:
            if driver:
                driver.quit()
            self.running_scraper = False
            self.master.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.master.after(0, lambda: self.stop_button.config(state=tk.DISABLED))


if __name__ == "__main__":
    root = tk.Tk()
    app = CarScraperGUI(root)
    root.mainloop()