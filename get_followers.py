# get_followers.py
import time
import random
import json
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import print_with_timestamp, get_random_user_agent

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

    headless_choice = input("Do you want to run the browser in headless mode? (yes/no): ").strip().lower()
    if headless_choice in ["yes", "y"]:
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
        print_with_timestamp(f"No 'Not Now' button found or already dismissed: {e}")

def get_followers_count(driver):
    """
    Extract the total number of followers for the target Instagram user.
    """
    try:
        followers_text = driver.find_element(By.XPATH, "//a[contains(@href, '/followers')]//span").text
        followers_count = int(followers_text.replace(',', ''))
        print_with_timestamp(f"Total followers count extracted: {followers_count}")
        if followers_count == 0:
            print_with_timestamp('This account is private or has no followers')
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
            EC.presence_of_element_located((By.XPATH, "//div[contains(@role, 'dialog')]"))
        )

        last_height = driver.execute_script("return arguments[0].scrollHeight", followers_popup)
        scroll_attempts = 0
        max_scroll_attempts = 50

        while len(follower_ids) < target_followers_count and scroll_attempts < max_scroll_attempts:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_popup)
            time.sleep(random.uniform(2, 4))

            new_height = driver.execute_script("return arguments[0].scrollHeight", followers_popup)
            if new_height == last_height:
                print_with_timestamp("Reached the end of the followers list.")
                break

            last_height = new_height
            scroll_attempts += 1

            # Extract follower usernames
            follower_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/')]")
            for element in follower_elements:
                href = element.get_attribute('href')
                if '/p/' not in href and '/stories/' not in href and href.count('/') == 3:
                    username = href.split('/')[-2]
                    if username and username not in ['', 'accounts', 'explore', 'reels']:
                        follower_ids.add(username)

            print_with_timestamp(f"Collected {len(follower_ids)} unique follower IDs.")

            if len(follower_ids) >= target_followers_count:
                print_with_timestamp(f"Collected enough followers: {len(follower_ids)}")
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
        target_username = input("Enter the target username: ").strip()

        driver.get(f"https://www.instagram.com/{target_username}/")
        time.sleep(random.uniform(3, 5))

        # Click followers link
        followers_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers')]"))
        )
        followers_link.click()
        time.sleep(random.uniform(2, 4))

        target_followers_count = get_followers_count(driver)
        if target_followers_count == 0:
            print_with_timestamp("Cannot proceed - no followers found")
            return

        print_with_timestamp(f"Target user {target_username} has {target_followers_count} followers.")

        follower_ids = scroll_followers_list(driver, min(target_followers_count, 1000))

        # Save to JSON
        data = {"target": follower_ids}
        json_filename = f"{target_username}_followers.json"

        with open(json_filename, "w") as f:
            json.dump(data, f, indent=4)
        print_with_timestamp(f"Followers saved to {json_filename}")
        
    except Exception as e:
        print_with_timestamp(f"Failed to navigate to followers list: {e}")
    finally:
        driver.quit()

def login_to_instagram():
    """
    Log into Instagram using the provided username and password.
    """
    username = input("Enter account username: ").strip()
    password = getpass.getpass("Enter account password: ")
    driver = setup_browser_with_user_agent()

    try:
        driver.get("https://www.instagram.com")
        time.sleep(random.uniform(2, 4))
        
        # Login process
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(random.uniform(3, 5))

        # Handle popups
        click_not_now(driver)
        
        # Proceed to followers extraction
        go_to_followers_and_scroll(driver)

    except Exception as e:
        print_with_timestamp(f"Failed to log in: {e}")
        driver.quit()

if __name__ == "__main__":
    print_with_timestamp("Instagram Follower Extraction Tool")
    print_with_timestamp("=" * 50)
    
    start_choice = input("Do you want to log into Instagram and begin? (yes/no): ").strip().lower()
    if start_choice in ["yes", "y"]:
        login_to_instagram()
    else:
        print_with_timestamp("Operation cancelled.")
