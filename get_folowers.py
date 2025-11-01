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
            go_to_followers_and_scroll(driver)

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

def get_followers_count(driver):
    """
    Extract the total number of followers for the target Instagram user.
    """
    try:
        followers_text = driver.find_element(By.XPATH, "//a[contains(@href, '/followers')]//span").text
        followers_count = int(followers_text.replace(',', ''))
        print_with_timestamp(f"Total followers count extracted: {followers_count}")
        if followers_count == 0:
            print_with_timestamp('this account is private')
        return followers_count
    except Exception as e:
        print_with_timestamp(f"Failed to get followers count: {e}")
        return 0

def scroll_followers_list(driver, target_followers_count):
    """
    Scroll through the followers list and collect follower IDs.
    """
    follower_ids = set()
    try:
        print_with_timestamp("Scrolling through followers...")

        followers_popup = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6']"))
        )

        last_height = driver.execute_script("return arguments[0].scrollHeight", followers_popup)

        while len(follower_ids) < target_followers_count:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_popup)
            time.sleep(random.uniform(7, 10))

            new_height = driver.execute_script("return arguments[0].scrollHeight", followers_popup)
            if new_height == last_height:
                print_with_timestamp("Reached the end of the followers list.")
                break

            last_height = new_height

            follower_elements = driver.find_elements(By.CLASS_NAME, "_ap3a")
            for element in follower_elements:
                follower_id = element.text.strip()  
                if follower_id:
                    follower_ids.add(follower_id)

            print_with_timestamp(f"Collected {len(follower_ids)} follower IDs.")

            if len(follower_ids) >= target_followers_count:
                print_with_timestamp(f"Collected enough followers: {len(follower_ids)} out of {target_followers_count}. Stopping.")
                break

        print_with_timestamp("Finished scrolling followers list.")
        return list(follower_ids)
    except Exception as e:
        print_with_timestamp(f"Failed to scroll followers list: {e}")
        return []

def go_to_followers_and_scroll(driver):
    """
    Navigate to the target user's followers page and start scrolling.
    """
    try:
        target_username = input("Enter the target username: ")

        driver.get(f"https://www.instagram.com/{target_username}/")
        time.sleep(random.uniform(2, 4))

        driver.find_element(By.XPATH, "//a[contains(@href, '/followers')]").click()
        time.sleep(random.uniform(2, 4))

        target_followers_count = get_followers_count(driver)
        print_with_timestamp(f"Target user {target_username} has {target_followers_count} followers.")

        follower_ids = scroll_followers_list(driver, target_followers_count)

        follower_ids_list = list(follower_ids)

        data = {
            "target": follower_ids_list  
            }
        
        json_filename = f"{target_username}_followers.json"

        with open(json_filename, "w") as f:
            json.dump(data, f, indent=4)
        print_with_timestamp(f"Followers file saved as {json_filename}.")
        driver.quit()
    except Exception as e:
        print_with_timestamp(f"Failed to navigate to followers list: {e}")

if __name__ == "__main__":
    print_with_timestamp("Hello and welcome to the Instagram automation tool!")
    print_with_timestamp("I'm here to help you gather followers from a target Instagram account.")
    print_with_timestamp("Let's get started!")

    start_choice = input("Do you want to log into Instagram and begin? (yes/no): ").strip().lower()
    if start_choice in ["yes", "y"]:
        print_with_timestamp("Great! Let's begin.")
        login_to_instagram()
    else:
        print_with_timestamp("No worries! You can run this again whenever you're ready. Goodbye!")
