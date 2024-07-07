# import time
# from datetime import datetime as dt
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from kiteconnect import KiteConnect
# from webdriver_manager.chrome import ChromeDriverManager

# # Load configuration
# configFile = 'config.json'
# with open(configFile, 'r') as configFile:
#     config = json.load(configFile)

# zerodhaLoginName = config['ZerodhaLoginName']
# zerodhaPass = config['ZerodhaPass']
# apiKey = config['apiKey']
# apisec = config['apisec']
# TOTP_seed = config['TOTP_seed']

# def get_request_token():
#     try:
#         # Initialize KiteConnect
#         kite = KiteConnect(api_key=apiKey)
#         url = kite.login_url()

#         # Set up Selenium options
#         options = Options()
#         options.headless = True
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=options)

#         # Open login page
#         driver.get(url)

#         # Wait for login elements to load and input credentials
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div/div[2]/form/div[1]/input'))).send_keys(zerodhaLoginName)
#         driver.find_element(By.XPATH, '//*[@id="container"]/div/div/div[2]/form/div[2]/input').send_keys(zerodhaPass)
#         driver.find_element(By.XPATH, '//*[@id="container"]/div/div/div/form/div[4]/button').click()

#         # Wait for TOTP page to load and input TOTP
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/form/div[1]/input')))
#         totp = pyotp.TOTP(TOTP_seed).now()
#         driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/form/div[1]/input').send_keys(totp)
#         driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/form/div[2]/button').click()

#         # Wait for the redirect URL
#         time.sleep(5)
#         token_url = driver.current_url

#         # Extract request token from URL
#         req_token = token_url.split("request_token=")[1].split("&")[0]

#         driver.quit()
#         return req_token

#     except Exception as e:
#         print(f"Exception occurred: {e}")
#         print(traceback.format_exc())
#         if driver:
#             driver.quit()
#         return None


# request_token = get_request_token()
# if request_token:
#     print(f"Request Token: {request_token}")
# else:
#     print("Failed to retrieve request token.")
# kite=KiteConnect("5gio34lqmlmn83a5")
# data=kite.generate_session(request_token,"i35ybn2e29yqzu5cz0cnfigv3fta7osm")
# kite.set_access_token(data["access_token"])
# print("kite session Generated ")
# print(kite.access_token)
import time
import json
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from kiteconnect import KiteConnect
from webdriver_manager.chrome import ChromeDriverManager
import pyotp
import traceback

# Load configuration
configFile = 'config.json'
with open(configFile, 'r') as configFile:
    config = json.load(configFile)

zerodhaLoginName = config['ZerodhaLoginName']
zerodhaPass = config['ZerodhaPass']
apiKey = config['apiKey']
apisec = config['apisec']
TOTP_seed = config['TOTP_seed']

def get_request_token():
    try:
        # Initialize KiteConnect
        kite = KiteConnect(api_key=apiKey)
        url = kite.login_url()

        # Set up Selenium options
        options = Options()
        options.headless = True
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Open login page
        driver.get(url)

        # Wait for login elements to load and input credentials
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div/div[2]/form/div[1]/input'))).send_keys(zerodhaLoginName)
        driver.find_element(By.XPATH, '//*[@id="container"]/div/div/div[2]/form/div[2]/input').send_keys(zerodhaPass)
        driver.find_element(By.XPATH, '//*[@id="container"]/div/div/div/form/div[4]/button').click()

        # Wait for TOTP page to load and input TOTP
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/form/div[1]/input')))
        totp = pyotp.TOTP(TOTP_seed).now()
        driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/form/div[1]/input').send_keys(totp)
        driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/form/div[2]/button').click()

        # Wait for the redirect URL
        time.sleep(5)
        token_url = driver.current_url

        # Extract request token from URL
        req_token = token_url.split("request_token=")[1].split("&")[0]

        driver.quit()
        return req_token

    except Exception as e:
        print(f"Exception occurred: {e}")
        print(traceback.format_exc())
        if driver:
            driver.quit()
        return None

def store_access_token(req_token):
    try:
        kite = KiteConnect(api_key=apiKey)
        data = kite.generate_session(req_token, apisec)
        access_token = data['access_token']

        # Store access token in a file
        with open('access_token.txt', 'w') as file:
            file.write(access_token)

        # Set access token in KiteConnect instance
        kite.set_access_token(access_token)
        print("Kite session generated")
        print(f"Access Token: {access_token}")
    except Exception as e:
        print(f"Exception occurred while storing access token: {e}")
        print(traceback.format_exc())

if __name__ == '__main__':
    request_token = get_request_token()
    if request_token:
        print(f"Request Token: {request_token}")
        store_access_token(request_token)
    else:
        print("Failed to retrieve request token.")


def get_access_token_from_file():
    try:
        with open('access_token.txt', 'r') as file:
            access_token = file.read().strip()
        return access_token
    except Exception as e:
        print(f"Exception occurred while reading access token: {e}")
        return None

access_token=get_access_token_from_file()
print(access_token)
