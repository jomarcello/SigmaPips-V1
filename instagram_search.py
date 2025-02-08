from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Stel het pad naar je ChromeDriver in
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
service = Service(CHROMEDRIVER_PATH)

# Instellen van User-Agent
options = webdriver.ChromeOptions()
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)
driver = webdriver.Chrome(service=service, options=options)

# Instagram-login
def login_to_instagram(driver):
    driver.get("https://www.instagram.com/accounts/login/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys("itsjomarcello")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    ).send_keys("JmT!102510")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    ).click()
    print("Inloggegevens ingevuld.")
    
    # Wacht op "Niet nu" knop
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Niet nu')]"))
        ).click()
        print("Gegevens opslaan: Niet nu aangeklikt.")
    except Exception as e:
        print(f"Knop 'Niet nu' kon niet worden gevonden: {e}")

# Zoek een term
def search_instagram(driver, search_query):
    search_bar_xpath = "//input[@placeholder='Search']"
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, search_bar_xpath))
    ).send_keys(search_query)
    print(f"Zoekopdracht ingevoerd: {search_query}")

# Script uitvoeren
try:
    login_to_instagram(driver)
    time.sleep(5)  # Even wachten na het inloggen
    search_instagram(driver, "villa crete")
finally:
    driver.quit()