import os
import platform
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
import boto3
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file for local execution
load_dotenv()

# Retrieve credentials and Twilio details from environment or .env file
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
SMS_BODY = os.getenv("SMS_BODY")
SITE_URL = os.getenv("SITE_URL")
AWS_REGION = os.getenv("AWS_REGION")


def setup_driver(headless=False):
    # chrome_options = Options()
    chrome_options = ChromeOptions()
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.binary_location = "/opt/homebrew/bin/chromedriver" # Path to headless chromium binary

    # Determine the correct ChromeDriver based on OS and potentially architecture
    driver_filename = ""
    if platform.system() == 'Linux':
        driver_filename = "chromedriver-122-linux64"
    elif platform.system() == 'Darwin':  # macOS
        # Optionally, you might differentiate by architecture (e.g., ARM vs. Intel) if necessary
        driver_filename = "chromedriver-122-mac-arm64"
    
    # Construct the path to the ChromeDriver
    webdriver_path = os.path.join(os.path.dirname(__file__), 'webdrivers', driver_filename)

    print(f"Platform: {platform.system()}")
    print(f"Using ChromeDriver located at: {webdriver_path}")
    # Ensure the ChromeDriver has executable permissions
    os.chmod(webdriver_path, 0o755)

    # Specify the path to ChromeDriver using the Service object
    service = Service(executable_path=webdriver_path)

    return webdriver.Chrome(service=service, options=chrome_options)


def access_ll_site(driver):
    if driver:
        driver.get(SITE_URL)
        print("Accessed LL site")
    else:
        print("Driver not initialized. Please setup the driver first.")


def login(driver, username, password):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "username")))
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        submit_button = driver.find_element(By.NAME, "login")

        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()
        return True
    except TimeoutException:
        print("Timed out waiting for login elements to appear.")
        return False


def check_todays_submission(driver):
    has_submitted_today = False

    try:
        # Wait up to 10 seconds for the div with inner text "LearnedLeague" to be present.
        # Note, this will be present on the page regardless of whether the user has submitted for the day.
        ll_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[text()='LearnedLeague']"))
        )

        element = driver.find_element(By.CLASS_NAME, "no_sub")

        # Check if the div does not have the style property "display:none"
        if element.get_attribute("style") != "display:none":
            has_submitted_today = False
        else:
            has_submitted_today = True

        return has_submitted_today
    except:
        # If the div is not found or any other exception occurs, assume submission has occurred
        has_submitted_today = True

        return has_submitted_today



def send_twilio_sms_message():
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=SMS_BODY,
        from_=TWILIO_PHONE_NUMBER,
        to=PHONE_NUMBER
    )
    print(f"Message sent: {message.sid}")



def send_aws_sns_sms_message(phone_number, message):
    # Create an SNS client
    sns = boto3.client('sns', region_name=AWS_REGION)

    # Send an SMS message
    response = sns.publish(
        PhoneNumber=phone_number,
        Message=message,
    )

    return response



def parse_arguments():
    parser = argparse.ArgumentParser(description="Run Selenium script in different modes.")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run script in interactive mode")
    # Use -H instead of -h for headless mode to avoid conflict with the help option
    parser.add_argument("-H", "--headless", action="store_true", help="Run Chrome in headless mode")
    args = parser.parse_args()
    
    # Check if both interactive and headless flags are set
    if args.interactive and args.headless:
        parser.error("The options -i/--interactive and -H/--headless cannot be used together.")
    
    return args


def main():
    args = parse_arguments()
    driver = setup_driver(headless=args.headless)

    if args.interactive:
        while True:
            print("\nType 1 to access LL site")
            print("Type 2 to login to LL site")
            print("Type 3 for submission check")
            print("Type 4 to send SMS message")
            print("Type 0 to quit")

            choice = input("Enter your choice: ")

            if choice == "1":
                access_ll_site(driver)
            elif choice == "2":
                login(driver, USERNAME, PASSWORD)
            elif choice == "3":
                result = check_todays_submission(driver)
                print(f"User has submitted today: {result}")
            elif choice == "4":
                print("Sending message...")
                # send_twilio_sms_message()
                # response = send_aws_sns_sms_message(PHONE_NUMBER, SMS_BODY)
                # print(f"Message sent: {response}")
                
            elif choice == "0":
                if driver:
                    driver.quit()
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please enter a valid option.")
    else:
        access_ll_site(driver)
        if login(driver, USERNAME, PASSWORD):
            print("Login successful. Checking submission for today.")
            exists = check_todays_submission(driver)
            if not exists:
                print("Submission not found. Sending reminder text message.")
                # send_twilio_sms_message()
                # response = send_aws_sns_sms_message(PHONE_NUMBER, SMS_BODY)
                # print(f"Message sent: {response}")
            else:
                print("Submission found. No action needed.")
        else:
            print("Login failed or page did not load properly.")
        driver.quit()


if __name__ == "__main__":
    main()
