from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
opts.add_argument("--headless")
opts.add_argument("--enable-logging")
opts.add_argument("--v=1")
opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})

driver = webdriver.Chrome(options=opts)
try:
    print("Navigating to http://127.0.0.1:8000...")
    driver.get("http://127.0.0.1:8000")
    time.sleep(2)
    print("Console Logs:")
    for log in driver.get_log("browser"):
        print(f"[{log['level']}] {log['message']}")
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
