# send_direct.py
import time
import random
import json
import os
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import print_with_timestamp, get_random_user_agent

class InstagramDMBot:
    def __init__(self):
        self.driver = None

    def setup_browser_with_user_agent(self):
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

        self.driver = webdriver.Chrome(options=options, service=Service("/usr/local/bin/chromedriver"))

        # Inject JavaScript to prevent detection of automation
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })

    def click_not_now(self):
        """
        Click the 'Not Now' button if it appears to skip additional notifications.
        """
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Not now')]"))
            ).click()
            print_with_timestamp("Clicked 'Not Now' successfully.")
        except Exception as e:
            print_with_timestamp(f"No 'Not Now' button found: {e}")

    def list_json_files(self, directory):
        """
        Lists all JSON files in the specified directory.
        """
        return [f for f in os.listdir(directory) if f.endswith('.json')]

    def choose_json_file(self, directory):
        """
        Prompts the user to choose a JSON file from the available files.
        """
        json_files = self.list_json_files(directory)
        
        if not json_files:
            print_with_timestamp("No JSON files found in current directory.")
            return None
        
        print_with_timestamp("Available JSON files:")
        for idx, file in enumerate(json_files, start=1):
            print_with_timestamp(f"{idx}. {file}")
        
        try:
            choice = int(input(f"Please choose a file (1-{len(json_files)}): ").strip())
            if 1 <= choice <= len(json_files):
                selected_file = json_files[choice - 1]
                print_with_timestamp(f"You selected: {selected_file}")
                return os.path.join(directory, selected_file)
            else:
                print_with_timestamp("Invalid choice number.")
                return None
        except ValueError:
            print_with_timestamp("Please enter a valid number.")
            return None

    def load_json_file(self, file_path):
        """
        Loads the selected JSON file and returns the target list.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if "target" in data and isinstance(data["target"], list):
                return data["target"]
            else:
                print_with_timestamp("Invalid JSON format: 'target' list not found.")
                return []
        except Exception as e:
            print_with_timestamp(f"Failed to load JSON file: {e}")
            return []

    def send_message_to_instagram_user(self, target_id, message):
        """
        Sends a direct message to a user on Instagram.
        """
        try:
            print_with_timestamp(f"Attempting to message: {target_id}")
            
            # Navigate to user profile
            self.driver.get(f"https://www.instagram.com/{target_id}/")
            time.sleep(random.uniform(3, 5))

            # Try to find and click message button
            try:
                message_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Message')]"))
                )
                message_button.click()
                print_with_timestamp("Message button clicked.")
                
            except:
                # Alternative method: click options and then send message
                print_with_timestamp("Trying alternative method...")
                try:
                    options_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button//span[contains(@aria-label, 'Options')]"))
                    )
                    options_button.click()
                    time.sleep(random.uniform(1, 2))

                    send_message_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send message')]"))
                    )
                    send_message_button.click()
                    
                    # Handle any popups
                    try:
                        not_now_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                        )
                        not_now_button.click()
                    except:
                        pass
                        
                except Exception as e:
                    print_with_timestamp(f"Cannot access message options for {target_id}: {e}")
                    return False

            # Wait for message dialog and send message
            time.sleep(random.uniform(2, 3))
            
            try:
                message_input = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Message']//p"))
                )
                message_input.click()
                message_input.send_keys(message)
                time.sleep(random.uniform(1, 2))

                # Send message
                send_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Send')]"))
                )
                send_button.click()
                
                print_with_timestamp(f"✅ Message sent to {target_id}")
                time.sleep(random.uniform(2, 4))  # Wait between messages
                return True
                
            except Exception as e:
                print_with_timestamp(f"❌ Failed to send message to {target_id}: {e}")
                return False

        except Exception as e:
            print_with_timestamp(f"❌ Error processing {target_id}: {e}")
            return False

    def login_to_instagram(self):
        """
        Log into Instagram using the provided username and password.
        """
        username = input("Enter account username: ").strip()
        password = getpass.getpass("Enter account password: ")
        
        self.setup_browser_with_user_agent()

        try:
            self.driver.get("https://www.instagram.com")
            time.sleep(random.uniform(2, 4))
            
            # Login process
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(username)
            
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(random.uniform(3, 5))

            # Handle popups
            self.click_not_now()
            
            return True

        except Exception as e:
            print_with_timestamp(f"Failed to log in: {e}")
            return False

    def run(self):
        """
        Main execution function for the DM bot.
        """
        print_with_timestamp("Instagram Direct Message Bot")
        print_with_timestamp("=" * 40)
        
        # Login
        if not self.login_to_instagram():
            return

        # Select JSON file
        json_file = self.choose_json_file("./")
        if not json_file:
            self.driver.quit()
            return

        # Load targets
        targets = self.load_json_file(json_file)
        if not targets:
            print_with_timestamp("No targets found in the JSON file.")
            self.driver.quit()
            return

        print_with_timestamp(f"Loaded {len(targets)} targets from JSON file.")
        
        # Get message
        message = input("Enter the message to send: ").strip()
        if not message:
            print_with_timestamp("No message provided.")
            self.driver.quit()
            return

        # Send messages
        successful_messages = 0
        for i, target_id in enumerate(targets, 1):
            print_with_timestamp(f"Progress: {i}/{len(targets)}")
            
            if self.send_message_to_instagram_user(target_id, message):
                successful_messages += 1
            
            # Random delay between messages
            if i < len(targets):
                delay = random.uniform(5, 10)
                print_with_timestamp(f"Waiting {delay:.1f} seconds before next message...")
                time.sleep(delay)

        print_with_timestamp(f"✅ Completed! Successfully sent {successful_messages}/{len(targets)} messages.")
        
        # Cleanup
        self.driver.quit()

if __name__ == "__main__":
    bot = InstagramDMBot()
    bot.run()
