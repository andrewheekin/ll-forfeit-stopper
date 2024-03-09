import os
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

# Load environment variables from .env file for local execution
load_dotenv()

"""
LL Forfeit Stopper
Author: Andrew Heekin

Runs in interactive mode using the ChromeDriver for Mac.

Instructions:
0. Create the `.env` file
1. Add the Mac ARM ChromeDriver to `webdrivers/chromedriver-122-mac-arm64`
2. Create the venv: `python3 -m venv venv`
2. Activate the virtualenv: `. venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python3 simpler_app.py`

Deploy to crontab:
1. `crontab -e`
2. Add the following line to run the script every day at 9pm:
	`0 17 * * * /usr/bin/python3 /path/to/simpler_app.py`


"""

# Retrieve credentials and Twilio details from environment or .env file
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SITE_URL = os.getenv("SITE_URL")
INNER_TEXT = os.getenv("INNER_TEXT")
GROUPME_API_URL = os.getenv("GROUPME_API_URL")
GROUPME_BOT_ID = os.getenv("GROUPME_BOT_ID")


def setup_driver_mac():
	options = webdriver.ChromeOptions()

	# Construct the path to the ChromeDriver
	webdriver_path = os.path.join(os.path.dirname(
		__file__), 'webdrivers', 'chromedriver-122-mac-arm64')
	print(f"Using ChromeDriver located at: {webdriver_path}")
	# Ensure the ChromeDriver has executable permissions
	os.chmod(webdriver_path, 0o755)

	# Specify the path to ChromeDriver using the Service object
	service = Service(executable_path=webdriver_path)
	driver = webdriver.Chrome(service=service, options=options)
	return driver


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
		print("Login successful. Checking submission for today.")
		return True
	except TimeoutException:
		print("Timed out waiting for login elements to appear.")
		return False


def check_todays_submission(driver):
	has_submitted_today = False

	try:
		# Wait up to 10 seconds for the div with inner text to be present.
		# Note, this will be present on the page regardless of whether the user has submitted for the day.
		WebDriverWait(driver, 10).until(
			EC.presence_of_element_located(
				(By.XPATH, f"//div[text()='{INNER_TEXT}']"))
		)

		element = driver.find_element(By.CLASS_NAME, "no_sub")

		# Check if the div does not have the style property "display:none"
		if element.get_attribute("style") != "display:none":
			has_submitted_today = False
		else:
			has_submitted_today = True

		print(
			f"User {'has' if has_submitted_today else 'has NOT'} submitted today.")
		return has_submitted_today
	except:
		# If the div is not found or any other exception occurs, assume submission has occurred
		has_submitted_today = True

		print(
			f"User {'has' if has_submitted_today else 'has NOT'} submitted today.")
		return has_submitted_today


def send_groupme_message(message):
	"""
	Send a message to a GroupMe group using the bot API.

	Equivalent to the following curl command:
	curl -d '{"text" : GROUPME_MESSAGE, "bot_id" : GROUPME_BOT_ID}' GROUPME_API_URL
	"""
	try:
		data = {
			"text": message,
			"bot_id": GROUPME_BOT_ID
		}
		headers = {
			"Content-Type": "application/json"
		}
		response = requests.post(
			GROUPME_API_URL, data=json.dumps(data), headers=headers)
		response.raise_for_status()
		print(f"Message sent to GroupMe: {message}")
		return response
	except requests.exceptions.RequestException as e:
		print(f"Error sending message to GroupMe: {e}")


def main():
	driver = setup_driver_mac()
	while True:
		print("\nType 1 to access LL site")
		print("Type 2 to login to LL site")
		print("Type 3 for submission check")
		print("Type 0 to quit")

		choice = input("Enter your choice: ")

		if choice == "1":
			access_ll_site(driver)
		elif choice == "2":
			login(driver, USERNAME, PASSWORD)
		elif choice == "3":
			result = check_todays_submission(driver)
			send_groupme_message(
				"You've submitted LL" if result else "🚨 Please submit LL today :)")
		elif choice == "0":
			print("Exiting...")
			if driver:
				driver.quit()
			break
		else:
			print("Invalid choice. Please enter a valid option.")


if __name__ == "__main__":
	main()
