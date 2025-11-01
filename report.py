import time
import random
import json
import getpass
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# List of user agents to choose from randomly
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.119 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.6; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 9; en-us; Redmi Note 7 Build/PKQ1.190616.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/110.0.5481.77 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18",
    "Mozilla/5.0 (Linux; U; Android 10; en-us; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
]
def print_with_timestamp(message):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}] - {message}")
    
def get_random_user_agent():
    """
    Select a random user-agent from the list.
    """
    if not user_agents:
        raise ValueError("User-agent list is empty")
    return random.choice(user_agents)

def setup_browser_with_user_agent():
    """
    Set up the Selenium WebDriver with specified options including a random user-agent.
    """
    options = Options()
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("accept-language=en-US,en;q=0.9")
    options.add_argument("referer=https://google.com")

    headless_choice = input("Do you want to run the browser? (yes/no): ").strip().lower()
    if headless_choice in ["no", "n"]:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

    user_agent = get_random_user_agent()
    options.add_argument(f'user-agent={user_agent}')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options, service=Service("/usr/local/bin/chromedriver"))

    # Inject JavaScript to prevent detection of automation
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })

    return driver

def login_to_instagram():
    """
    Log into Instagram using the provided username and password.
    """
    username = input("Enter account username: ")
    password = getpass.getpass("Enter account password: ")
    driver = setup_browser_with_user_agent()

    try:
        driver.get("https://www.instagram.com")
        while True:
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
                driver.find_element(By.NAME, "password").send_keys(password)
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                print_with_timestamp("Username button not found, refreshing the page...")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button//div[text()='Log in']"))).click()
                time.sleep(random.uniform(2, 4))  
                continue 
            click_not_now(driver)
            report(driver)

    except Exception as e:
        print_with_timestamp(f"Failed to log in: {e}")
        time.sleep(random.uniform(2, 4))

def click_not_now(driver):
    """
    Click the 'Not Now' button if it appears to skip additional notifications.
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Not now')]"))
        ).click()
        print_with_timestamp("Clicked 'Not Now' successfully.")
    except Exception as e:
        print_with_timestamp(f"Failed to click 'Not Now' or incorrect username/password: {e}")


def report(driver):
    try:
        target_username = input("Enter the target username: ")

        driver.get(f"https://www.instagram.com/{target_username}/")
        time.sleep(random.uniform(2, 4))
        
