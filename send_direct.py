import time
import random
import json
import os
import datetime
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure browser options
options = Options()
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
    Returns a random user-agent from the predefined list of user agents.
    """
    if not user_agents:
        raise ValueError("User-agent list is empty.")
    return random.choice(user_agents)

def setup_browser_with_user_agent():
    """
    Initializes the browser with necessary options like disabling extensions, 
    enabling headless mode if requested, and setting a random user-agent.
    """
    global driver
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("accept-language=en-US,en;q=0.9")
    options.add_argument("referer=https://google.com")

    headless_choice = input("Do you want to run the browser ? (yes/no): ").strip().lower()
    if headless_choice in ["no","n"]:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    user_agent = get_random_user_agent()
    options.add_argument(f'user-agent={user_agent}')

    # Exclude automation flags to avoid detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options, service=Service("/usr/local/bin/chromedriver"))

    # Disable the 'navigator.webdriver' property to avoid detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })

def login_to_instagram():
    """
    Logs in to Instagram using the provided username and password. 
    After logging in, it handles potential login pop-ups and proceeds to load a JSON file for messaging.
    """
    global driver
    print_with_timestamp("Welcome! Please log in to your Instagram account.")
    username = input("Enter account username: ")
    password = getpass.getpass("Enter account password: ")
    setup_browser_with_user_agent()

    try:
        driver.get("https://www.instagram.com")
        while True:
            try:
                # Wait for the username field and input username/password
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
                driver.find_element(By.NAME, "password").send_keys(password)
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                print_with_timestamp("Login button not found, refreshing the page...")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button//div[text()='Log in']"))).click()
                time.sleep(random.uniform(2, 4))
                continue 

            # Handle pop-up after login (if present)
            click_not_now()
            selected_file = choose_json_file("./")
            if selected_file:
                load_json_file(selected_file)
                break  # Exit the loop once the file is loaded
    except Exception as e:
        print_with_timestamp(f"Failed to log in: {e}")
        driver.quit()

def click_not_now():
    """
    Clicks the 'Not Now' button to dismiss any pop-ups (e.g., notifications or follow suggestions) after login.
    """
    global driver
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Not now')]"))).click()
        print_with_timestamp("Clicked 'Not Now' successfully.")
    except Exception as e:
        print_with_timestamp(f"Failed to click 'Not Now'or incorrect username/password: {e}")

def list_json_files(directory):
    """
    Lists all JSON files in the specified directory.
    """
    return [f for f in os.listdir(directory) if f.endswith('.json')]

def choose_json_file(directory):
    """
    Prompts the user to choose a JSON file from the available files in the specified directory.
    """
    json_files = list_json_files(directory)
    
    if not json_files:
        print_with_timestamp("No JSON files found.")
        return None
    
    print_with_timestamp("Available JSON files:")
    for idx, file in enumerate(json_files, start=1):
        print_with_timestamp(f"{idx}. {file}")
    
    choice = input(f"Please choose a file (1-{len(json_files)}): ").strip()
    
    try:
        choice = int(choice)
        if 1 <= choice <= len(json_files):
            selected_file = json_files[choice - 1]
            print_with_timestamp(f"You selected: {selected_file}")
            return os.path.join(directory, selected_file)
        else:
            print_with_timestamp("Invalid choice. Please select a valid file number.")
            return None
    except ValueError:
        print_with_timestamp("Invalid input. Please enter a number.")
        return None

def load_json_file(file_path):
    """
    Loads the selected JSON file and initiates the messaging process to target users listed in the file.
    """
    global driver
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        if "target" in data and isinstance(data["target"], list):
            message = input("Enter the message to send: ")
            for target_id in data["target"]:
                print_with_timestamp(f"Processing target ID: {target_id}")
                send_message_to_instagram_user(target_id, message)
        else:
            print_with_timestamp("Invalid data format in JSON file.")
    except Exception as e:
        print_with_timestamp(f"Failed to load JSON file: {e}")

def send_message_to_instagram_user(target_id, message):
    """
    Sends a direct message to a user on Instagram by navigating to their profile and sending the provided message.
    """
    global driver
    try:
        driver.get(f"https://www.instagram.com/{target_id}/")
        time.sleep(random.uniform(2, 4))

        try:
            message_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Message')]"))
            )
            print_with_timestamp(f"Message button found for {target_id}, clicking on it...")
            message_button.click()

        except Exception as e:
            print_with_timestamp(f"Message button not found for {target_id}, clicking on Options...")
            options_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'svg[aria-label="Options"]'))
            )
            options_button.click()
            time.sleep(random.uniform(2, 4))  

            send_message_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Send message')]"))
            )
            send_message_button.click()
            try:
                button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Not Now')]")))
                button.click()
            except:
                pass
        # Wait for message input and send the message
        try:
            message_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Message']")))
            message_input.click()
            message_input.send_keys(message)
            time.sleep(random.uniform(1, 2))  

            send_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Send')]"))
            )
            send_button.click()
            print_with_timestamp(f"Message sent to {target_id}.")
                
        except:
            print_with_timestamp("This account does not allow you to access their direct")
    except Exception as e:
        print_with_timestamp(f"Failed to send message to {target_id}: {e}")

if __name__ == "__main__":
    print_with_timestamp("Hello and welcome to the Instagram messaging bot!")
    print_with_timestamp("I'm here to help you log in to Instagram and send messages to users from a selected JSON file.")
    print_with_timestamp("Let's get started!")

    start_choice = input("Do you want to log into Instagram and begin? (yes/no): ").strip().lower()
    if start_choice in ["yes", "y"]:
        print_with_timestamp("Great! Let's begin the login process.")
        login_to_instagram()
    else:
        print_with_timestamp("No worries! You can run this again whenever you're ready. Goodbye!")
