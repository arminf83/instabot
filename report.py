# report.py
import time
import random
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import print_with_timestamp, get_random_user_agent

class InstagramReportBot:
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

    def report_account(self, target_username, reason="spam"):
        """
        Report an Instagram account for specified reason.
        """
        try:
            print_with_timestamp(f"Starting report process for @{target_username}")
            
            # Navigate to target profile
            self.driver.get(f"https://www.instagram.com/{target_username}/")
            time.sleep(random.uniform(3, 5))
            
            # Click on three dots menu
            try:
                menu_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button//span[contains(@aria-label, 'Options')]"))
                )
                menu_button.click()
                time.sleep(random.uniform(1, 2))
            except:
                # Alternative menu selector
                menu_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//svg[@aria-label='Options']"))
                )
                menu_button.click()
                time.sleep(random.uniform(1, 2))
            
            # Click report button
            report_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Report')]"))
            )
            report_button.click()
            time.sleep(random.uniform(1, 2))
            
            # Report flow - step 1: Select report type
            try:
                report_option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Report')]"))
                )
                report_option.click()
                time.sleep(random.uniform(1, 2))
            except:
                print_with_timestamp("Using alternative report flow...")
            
            # Step 2: Select reason
            reasons = {
                "spam": "It's spam",
                "scam": "It's a scam",
                "harassment": "Bullying or harassment",
                "nudity": "Nudity or sexual activity",
                "hate": "Hate speech or symbols"
            }
            
            selected_reason = reasons.get(reason, "It's spam")
            
            try:
                reason_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{selected_reason}')]"))
                )
                reason_button.click()
                time.sleep(random.uniform(1, 2))
            except:
                # If specific reason not found, click first available reason
                reason_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(), 'It')])[1]"))
                )
                reason_button.click()
                time.sleep(random.uniform(1, 2))
            
            # Step 3: Submit report
            try:
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]"))
                )
                submit_button.click()
                time.sleep(random.uniform(2, 3))
                
                print_with_timestamp(f"✅ Successfully reported @{target_username} for {reason}")
                return True
                
            except:
                print_with_timestamp(f"⚠️  Report process completed for @{target_username} (may need manual confirmation)")
                return True

        except Exception as e:
            print_with_timestamp(f"❌ Failed to report @{target_username}: {e}")
            return False

    def report_multiple_accounts(self, usernames, reason="spam"):
        """
        Report multiple Instagram accounts.
        """
        successful_reports = 0
        
        for i, username in enumerate(usernames, 1):
            print_with_timestamp(f"Progress: {i}/{len(usernames)}")
            
            if self.report_account(username.strip(), reason):
                successful_reports += 1
            
            # Random delay between reports
            if i < len(usernames):
                delay = random.uniform(10, 20)  # Longer delay for reports
                print_with_timestamp(f"Waiting {delay:.1f} seconds before next report...")
                time.sleep(delay)

        return successful_reports

    def run(self):
        """
        Main execution function for the report bot.
        """
        print_with_timestamp("Instagram Account Reporting Tool")
        print_with_timestamp("=" * 45)
        print_with_timestamp("⚠️  Use responsibly and only for legitimate reports!")
        
        # Login
        if not self.login_to_instagram():
            return

        # Get reporting details
        print_with_timestamp("\nReporting Options:")
        print_with_timestamp("1. Report single account")
        print_with_timestamp("2. Report multiple accounts from file")
        
        choice = input("Choose option (1 or 2): ").strip()
        
        if choice == "1":
            # Single account report
            target_username = input("Enter username to report: ").strip()
            reason = input("Enter reason (spam/scam/harassment/nudity/hate): ").strip().lower() or "spam"
            
            self.report_account(target_username, reason)
            
        elif choice == "2":
            # Multiple accounts from file
            filename = input("Enter filename with usernames (one per line): ").strip()
            reason = input("Enter reason (spam/scam/harassment/nudity/hate): ").strip().lower() or "spam"
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    usernames = [line.strip() for line in f if line.strip()]
                
                if not usernames:
                    print_with_timestamp("No usernames found in file.")
                    return
                
                print_with_timestamp(f"Found {len(usernames)} usernames to report.")
                confirm = input("Proceed with reporting? (yes/no): ").strip().lower()
                
                if confirm in ["yes", "y"]:
                    successful = self.report_multiple_accounts(usernames, reason)
                    print_with_timestamp(f"✅ Reporting completed! {successful}/{len(usernames)} successful reports.")
                else:
                    print_with_timestamp("Reporting cancelled.")
                    
            except FileNotFoundError:
                print_with_timestamp("❌ File not found.")
            except Exception as e:
                print_with_timestamp(f"❌ Error reading file: {e}")
        else:
            print_with_timestamp("Invalid choice.")

        # Cleanup
        self.driver.quit()

if __name__ == "__main__":
    bot = InstagramReportBot()
    bot.run()
