import   logging
import time as tm
import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta
from kiteconnect import KiteTicker, KiteConnect
import json
import os
from datetime import datetime,time
from time import sleep
import ast
from re3124 import *
import asyncio
from telegram import Bot
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
print("hello")

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
        tm.sleep(5)
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

request_token = get_request_token()
if request_token:
    print(f"Request Token: {request_token}")
    store_access_token(request_token)
else:
    print("Failed to retrieve request token.")


# Your bot's API token
bot_token = '7031311606:AAH8eVbdxkQpAPTW6b4zPQu5zJ8z_Q3CyLc'
bot = Bot(token=bot_token)

# Async function to send message to Telegram
async def send_telegram_message(message):
    # chat_id = -4249796811 
    chat_id = 2039601966
    # chat_id = -1002228606742
      # Replace with your numeric chat ID
    await bot.send_message(chat_id=chat_id, text=message)

# Function to call send_telegram_message asynchronously within the existing event loop
def call_send_message(message):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(send_telegram_message(message))

# Async function to send message to Telegram
async def send_telegram_message2(message):
    # chat_id = -4249796811
    # chat_id = -1002228606742
    chat_id = 6863806813# SANJAY BHAI CHAT IT
    await bot.send_message(chat_id=chat_id, text=message)

# Function to call send_telegram_message asynchronously within the existing event loop
def call_send_message2(message):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(send_telegram_message2(message))

call_send_message("Hello I'am running.")
call_send_message2("Hello I'am running.")

def get_access_token_from_file():
    try:
        with open('access_token.txt', 'r') as file:
            access_token = file.read().strip()
        return access_token
    except Exception as e:
        print(f"Exception occurred while reading access token: {e}")
        return None

access_token = get_access_token_from_file()
print(access_token)

#Example usage:
# call_send_message("HELLO ,Its 9:25")

logging.basicConfig(level=logging.DEBUG)

# Initialize Kite Connect
kite = KiteConnect(api_key="5gio34lqmlmn83a5")
kite.set_access_token(access_token)

# Get the current directory
current_directory = os.getcwd()

# Construct the file path for the order file
order_file = os.path.join(current_directory, "long.txt")
order_file2=os.path.join(current_directory,'short.txt')

STRIKE_PRICE_FILE = 'strike.txt'


# Dictionary to store whether an order has been placed for an instrument token
order_placed = {}

#Dictionary to store the tokens for the squared off orders.
square_off_orderss=[779521]
square_off_orderss2=[]
square_off_bear=[]
square_off_bear2 =[]

# Dictionary to store historical data
historical_data_dict = {}

nifty_instrument_token = 256265

def load_strike_price_dict():
    with open(STRIKE_PRICE_FILE, 'r') as f:
        content = f.read()
    return ast.literal_eval(content)

# Function to save the strike price dictionary to the file
def save_strike_price_dict(strike_price_dict):
    with open(STRIKE_PRICE_FILE, 'w') as f:
        f.write(str(strike_price_dict))

# Function to update the expiry date
def update_expiry(strike_price_dict, old_expiry, new_expiry):
    for key, value in strike_price_dict.items():
        if value['expiry'] == old_expiry:
            value['expiry'] = new_expiry


def fetch_historical_data(instrument_token, days):
    today = pd.Timestamp.today().date()
    from_date = today - timedelta(days=days - 1)
    to_date = today
    historical_data = kite.historical_data(instrument_token, from_date, to_date, interval='day')
    df = pd.DataFrame(historical_data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df


def fetch_last_price(instrument_token):
    last_price = kite.ltp(instrument_token)[str(instrument_token)]['last_price']
    return last_price


def calculate_ema(prices, period):
    prices_array = np.array(prices)
    return talib.EMA(prices_array, timeperiod=period)


def update_last_row(k, instrument_token,last_p):
    last_close = last_p
    k.iloc[-1, k.columns.get_loc('close')] = last_close

    # Calculate EMAs for different periods
    k['5_day_ema'] = calculate_ema(k['close'], 5)
    k['13_day_ema'] = calculate_ema(k['close'], 13)
    k['21_day_ema'] = calculate_ema(k['close'], 21)


def calculate_atm_strike_price(last_traded_price, strike_difference):
    print('calculating atm')
    return round(last_traded_price / strike_difference) * strike_difference

def is_file_empty(file_path):
    with open(file_path, 'r') as file:
        first_char = file.read(1)
        return not first_char

def save_order_details(order_details):
    try:
        with open(order_file, 'a') as file:
            json.dump(order_details, file)
            file.write("\n")
        print("Order details saved to file.")
    except Exception as e:
        print(f"Error saving order details: {e}")

def save_order_details2(order_details):
    try:
        with open(order_file2, 'a') as file:
            json.dump(order_details, file)
            file.write("\n")
        print("Order details saved to file.")
    except Exception as e:
        print(f"Error saving order details: {e}")

def remove_order_details(order_details):
    try:
        with open(order_file, 'r') as file:
            orders = [json.loads(line) for line in file]

        orders = [order for order in orders if order != order_details]

        with open(order_file, 'w') as file:
            for order in orders:
                json.dump(order, file)
                file.write("\n")
        print("Order details removed from file.")
    except Exception as e:
        print(f"Error removing order details: {e}")

def remove_order_details2(order_details):
    try:
        with open(order_file2, 'r') as file:
            orders = [json.loads(line) for line in file]

        orders = [order for order in orders if order != order_details]

        with open(order_file, 'w') as file:
            for order in orders:
                json.dump(order, file)
                file.write("\n")
        print("Order details removed from file.")
    except Exception as e:
        print(f"Error removing order details: {e}")

def extract_stock_name_reject(tradingsymbol):
    match = re.match(r'^([A-Z]+)', tradingsymbol)
    if match:
        return match.group(1)
    return None

# Function to square off an order
def square_off_order_reject(tradingsymbol, quantity):
    transaction_type = kite.TRANSACTION_TYPE_SELL
    full_tradingsymbol = f'NFO:{tradingsymbol}'
    try:
        ltp_data = kite.ltp(full_tradingsymbol)[full_tradingsymbol]
        if 'last_price' in ltp_data and ltp_data['last_price'] is not None:
            last_price = ltp_data['last_price']
            market_price = last_price -0.10 if transaction_type == kite.TRANSACTION_TYPE_SELL else last_price + 0.10
            # kite.place_order(
            #     tradingsymbol=tradingsymbol,
            #     exchange=kite.EXCHANGE_NFO,
            #     transaction_type=transaction_type,
            #     quantity=quantity,
            #     order_type=kite.ORDER_TYPE_LIMIT,
            #     price=round(market_price, 1),
            #     variety=kite.VARIETY_REGULAR,
            #     product=kite.PRODUCT_NRML,
            #     validity=kite.VALIDITY_DAY
            # )
            print(f"Placed {transaction_type} order for {full_tradingsymbol} at price {round(market_price, 1)}")
    except Exception as e:
        print(f"Error in placing order for {full_tradingsymbol}: {e}")

def filter_orders_reject(order_file, stock_name):
    if os.path.exists(order_file):
        with open(order_file, 'r') as file:
            lines = file.readlines()
        
        # Write back only the lines that do not contain the stock name
        with open(order_file, 'w') as file:
            for line in lines:
                if stock_name not in line:
                    file.write(line)
                else:
                    print(f"Removing line: {line.strip()}")

        print(f"Removed orders with {stock_name} from {order_file}")
    else:
        print(f"{order_file} does not exist")

# Process the orders data
def process_orders_reject(orders):
    for order in orders:
        if order['status'] == 'REJECTED':
            stock_name = extract_stock_name_reject(order['tradingsymbol'])
            print(stock_name)
            if stock_name:
                # Find and square off the corresponding buy order
                for o in orders:
                    if o['status'] == 'COMPLETE' and o['tradingsymbol'].startswith(stock_name) and o['transaction_type'] == 'BUY':
                        print(o['tradingsymbol'])
                        square_off_order_reject(o['tradingsymbol'], o['quantity'])
                        break

                # Filter the orders in order.txt
                filter_orders('yoyo.txt', stock_name)

# Function to fetch orders
def get_orders():
    try:
        orders = kite.orders()
        return orders
    except Exception as e:
        print("Error in fetching orders:", e)
        return []


def buy_signal(instrument_token,last_close_price_instrument,last_close_price_nifty):
    print("buy signal")
    # Fetch historical data if not already fetched
    if instrument_token not in historical_data_dict:
        historical_data_dict[instrument_token] = fetch_historical_data(instrument_token, days=250)

    # Fetch Nifty historical data if not already fetched
    if nifty_instrument_token not in historical_data_dict:
        historical_data_dict[nifty_instrument_token] = fetch_historical_data(nifty_instrument_token, days=250)

    # Fetch last traded price
    last_traded_price =last_close_price_instrument

    # Update historical data with the last traded price
    update_last_row(historical_data_dict[instrument_token], instrument_token, last_close_price_instrument)
    update_last_row(historical_data_dict[nifty_instrument_token], nifty_instrument_token, last_close_price_nifty)

    # Check the condition for the stock
    ema_5 = historical_data_dict[instrument_token]['5_day_ema'].iloc[-1]
    ema_13 = historical_data_dict[instrument_token]['13_day_ema'].iloc[-1]
    ema_21 = historical_data_dict[instrument_token]['21_day_ema'].iloc[-1]

    # Check the condition for Nifty
    nifty_ema_5 = historical_data_dict[nifty_instrument_token]['5_day_ema'].iloc[-1]
    nifty_ema_13 = historical_data_dict[nifty_instrument_token]['13_day_ema'].iloc[-1]
    nifty_ema_21 = historical_data_dict[nifty_instrument_token]['21_day_ema'].iloc[-1]

    if ema_5 > ema_13 > ema_21 and nifty_ema_5 > nifty_ema_13 > nifty_ema_21:
        return True, last_traded_price
    else:
        return False, last_traded_price

            

def short_signal(instrument_token,last_close_price_instrument,last_close_price_nifty):
    # Fetch historical data if not already fetched
    print(" checkinh short signal")
    if instrument_token not in historical_data_dict:
        historical_data_dict[instrument_token] = fetch_historical_data(instrument_token, days=250)

    # Fetch Nifty historical data if not already fetched
    if nifty_instrument_token not in historical_data_dict:
        historical_data_dict[nifty_instrument_token] = fetch_historical_data(nifty_instrument_token, days=250)

    # Fetch last traded price
    last_traded_price =last_close_price_instrument

    # Update historical data with the last traded price
    update_last_row(historical_data_dict[instrument_token], instrument_token, last_close_price_instrument)
    update_last_row(historical_data_dict[nifty_instrument_token], nifty_instrument_token, last_close_price_nifty)

    # Check the condition for the stock
    ema_5 = historical_data_dict[instrument_token]['5_day_ema'].iloc[-1]
    ema_13 = historical_data_dict[instrument_token]['13_day_ema'].iloc[-1]
    ema_21 = historical_data_dict[instrument_token]['21_day_ema'].iloc[-1]

    # Check the condition for Nifty
    nifty_ema_5 = historical_data_dict[nifty_instrument_token]['5_day_ema'].iloc[-1]
    nifty_ema_13 = historical_data_dict[nifty_instrument_token]['13_day_ema'].iloc[-1]
    nifty_ema_21 = historical_data_dict[nifty_instrument_token]['21_day_ema'].iloc[-1]

    if ema_5 < ema_13 < ema_21 and nifty_ema_5 < nifty_ema_13 < nifty_ema_21:
        return True, last_traded_price
    else:
        return False, last_traded_price
    

def sell_signal(instrument_token, last_close_price_instrument, last_close_price_nifty):
    print(" checking sell sigansl")
    # Fetch historical data if not already fetched
    if instrument_token not in historical_data_dict:
        historical_data_dict[instrument_token] = fetch_historical_data(instrument_token, days=250)

    # Fetch Nifty historical data if not already fetched
    if nifty_instrument_token not in historical_data_dict:
        historical_data_dict[nifty_instrument_token] = fetch_historical_data(nifty_instrument_token, days=250)

    # Fetch last traded price
    last_traded_price =last_close_price_instrument

    # Update historical data with the last traded price
    update_last_row(historical_data_dict[instrument_token], instrument_token, last_close_price_instrument)
    update_last_row(historical_data_dict[nifty_instrument_token], nifty_instrument_token, last_close_price_nifty)

    # Check the condition for the stock
    ema_5 = historical_data_dict[instrument_token]['5_day_ema'].iloc[-1]
    ema_13 = historical_data_dict[instrument_token]['13_day_ema'].iloc[-1]
    ema_21 = historical_data_dict[instrument_token]['21_day_ema'].iloc[-1]

    # Check the condition for Nifty
    nifty_ema_5 = historical_data_dict[nifty_instrument_token]['5_day_ema'].iloc[-1]
    nifty_ema_13 = historical_data_dict[nifty_instrument_token]['13_day_ema'].iloc[-1]
    nifty_ema_21 = historical_data_dict[nifty_instrument_token]['21_day_ema'].iloc[-1]

    if nifty_ema_5<nifty_ema_13 or nifty_ema_5<nifty_ema_21 or ema_5<ema_13 or ema_5<ema_21:
        return True
    return False


def sell_short(instrument_token, last_close_price_instrument, last_close_price_nifty):
    print(" checking sell shrt")
    # Fetch historical data if not already fetched
    if instrument_token not in historical_data_dict:
        historical_data_dict[instrument_token] = fetch_historical_data(instrument_token, days=250)

    # Fetch Nifty historical data if not already fetched
    if nifty_instrument_token not in historical_data_dict:
        historical_data_dict[nifty_instrument_token] = fetch_historical_data(nifty_instrument_token, days=250)

    # Fetch last traded price
    last_traded_price =last_close_price_instrument

    # Update historical data with the last traded price
    update_last_row(historical_data_dict[instrument_token], instrument_token, last_close_price_instrument)
    update_last_row(historical_data_dict[nifty_instrument_token], nifty_instrument_token, last_close_price_nifty)

    # Check the condition for the stock
    ema_5 = historical_data_dict[instrument_token]['5_day_ema'].iloc[-1]
    ema_13 = historical_data_dict[instrument_token]['13_day_ema'].iloc[-1]
    ema_21 = historical_data_dict[instrument_token]['21_day_ema'].iloc[-1]

    # Check the condition for Nifty
    nifty_ema_5 = historical_data_dict[nifty_instrument_token]['5_day_ema'].iloc[-1]
    nifty_ema_13 = historical_data_dict[nifty_instrument_token]['13_day_ema'].iloc[-1]
    nifty_ema_21 = historical_data_dict[nifty_instrument_token]['21_day_ema'].iloc[-1]

    if nifty_ema_5>nifty_ema_13 or nifty_ema_5>nifty_ema_21 or ema_5>ema_13 or ema_5>ema_21:
        return True
    return False


def place_order_fut(instrument_token, min_quantity, transaction_type):
    symbol = strike_price_dict[instrument_token]['symbol']
    expiry = strike_price_dict[instrument_token]['expiry']
    fut_trading_symbol = f"NFO:{symbol}{expiry}FUT"

    try:
        if transaction_type == kite.TRANSACTION_TYPE_BUY:
            
            ltp_data_fut = kite.ltp(fut_trading_symbol)[fut_trading_symbol]
            if 'last_price' in ltp_data_fut and ltp_data_fut['last_price'] is not None:
                market_price_fut = ltp_data_fut['last_price']
                # kite.place_order(tradingsymbol=fut_trading_symbol[4:],
                #                  exchange=kite.EXCHANGE_NFO,
                #                  transaction_type=kite.TRANSACTION_TYPE_BUY,
                #                  quantity=min_quantity,
                #                  order_type=kite.ORDER_TYPE_LIMIT,
                #                  price=round(market_price_fut, 1),
                #                  variety=kite.VARIETY_REGULAR,
                #                  product=kite.PRODUCT_NRML,
                #                  validity=kite.VALIDITY_DAY)
                print(f"Successfully placed buy order for {fut_trading_symbol} at market price: {market_price_fut}")
                call_send_message(f"Successfully placed buy order for {fut_trading_symbol} at market price: {market_price_fut}")
                # Save the order details
                order_details = {
                    'timestamp': str(datetime.now()),
                    'instrument_token': instrument_token,
                    'transaction_type': 'BUY',
                    'symbol': fut_trading_symbol,
                    'quantity': min_quantity,
                    'price': market_price_fut,
                    'strike_price': None,
                    'strike_type': 'FUT'
                }
                save_order_details(order_details)
            else:
                print("Error: 'last_price' not found in market data for FUTURE option")
                call_send_message("Error: 'last_price' not found in market data for FUTURE option")
                

        elif transaction_type == kite.TRANSACTION_TYPE_SELL:
            
            ltp_data_fut = kite.ltp(fut_trading_symbol)[fut_trading_symbol]
            if 'last_price' in ltp_data_fut and ltp_data_fut['last_price'] is not None:
                market_price_fut = ltp_data_fut['last_price'] 
                # kite.place_order(tradingsymbol=fut_trading_symbol[4:],
                #                  exchange=kite.EXCHANGE_NFO,
                #                  transaction_type=kite.TRANSACTION_TYPE_SELL,
                #                  quantity=min_quantity,
                #                  order_type=kite.ORDER_TYPE_LIMIT,
                #                  price=round(market_price_fut, 1),
                #                  variety=kite.VARIETY_REGULAR,
                #                  product=kite.PRODUCT_NRML,
                #                  validity=kite.VALIDITY_DAY)
                print(f"Successfully placed sell order for {fut_trading_symbol} at market price: {market_price_fut}")
                call_send_message(f"Successfully placed sell order for {fut_trading_symbol} at market price: {market_price_fut}")
                # Save the order details
                order_details = {
                    'timestamp': str(datetime.now()),
                    'instrument_token': instrument_token,
                    'transaction_type': 'SELL',
                    'symbol': fut_trading_symbol,
                    'quantity': min_quantity,
                    'price': market_price_fut,
                    'strike_price': None,
                    'strike_type': 'ATM'
                }
                save_order_details2(order_details)
            else:
                print("Error: 'last_price' not found in market data for FUTURE ")
                call_send_message("Error: 'last_price' not found in market data for FUTURE ")
                
    except Exception as e:
        print(f"Error placing {transaction_type} order: {e}")
        call_send_message(f"Error placing {transaction_type} order: {e}")
        
def place_order(instrument_token, atm_strike_price, min_quantity, transaction_type):
    symbol = strike_price_dict[instrument_token]['symbol']
    expiry = strike_price_dict[instrument_token]['expiry']

    # Determine the put option strikes
    atm_put_trading_symbol = f"NFO:{symbol}{expiry}{atm_strike_price}PE"
    otm_put_strike_price = atm_strike_price - 2 * strike_price_dict[instrument_token]['strike_difference']
    otm_put_trading_symbol = f"NFO:{symbol}{expiry}{otm_put_strike_price}PE"

    try:
        if transaction_type == kite.TRANSACTION_TYPE_BUY:
            # Buy OTM put option
            ltp_data_otm_put = kite.ltp(otm_put_trading_symbol)[otm_put_trading_symbol]
            if 'last_price' in ltp_data_otm_put and ltp_data_otm_put['last_price'] is not None:
                market_price_otm_put = ltp_data_otm_put['last_price'] + 0.10
                # kite.place_order(tradingsymbol=otm_put_trading_symbol[4:],
                #                  exchange=kite.EXCHANGE_NFO,
                #                  transaction_type=kite.TRANSACTION_TYPE_BUY,
                #                  quantity=min_quantity,
                #                  order_type=kite.ORDER_TYPE_LIMIT,
                #                  price=round(market_price_otm_put, 1),
                #                  variety=kite.VARIETY_REGULAR,
                #                  product=kite.PRODUCT_NRML,
                #                  validity=kite.VALIDITY_DAY)
                print(f"Successfully placed buy order for {otm_put_trading_symbol} at market price: {market_price_otm_put}")
                call_send_message(f"Successfully placed buy order for {otm_put_trading_symbol} at market price: {market_price_otm_put}")
                
                # Save the order details
                order_details = {
                    'timestamp': str(datetime.now()),
                    'instrument_token': instrument_token,
                    'transaction_type': 'BUY',
                    'symbol': otm_put_trading_symbol,
                    'quantity': min_quantity,
                    'price': market_price_otm_put,
                    'strike_price': otm_put_strike_price,
                    'strike_type': 'OTM'
                }
                save_order_details(order_details)
            else:
                print("Error: 'last_price' not found in market data for OTM put option")
                call_send_message("Error: 'last_price' not found in market data for OTM put option")
                
        elif transaction_type == kite.TRANSACTION_TYPE_SELL:
            # Sell ATM put option
            ltp_data_atm_put = kite.ltp(atm_put_trading_symbol)[atm_put_trading_symbol]
            if 'last_price' in ltp_data_atm_put and ltp_data_atm_put['last_price'] is not None:
                market_price_atm_put = ltp_data_atm_put['last_price'] -0.10
                # kite.place_order(tradingsymbol=atm_put_trading_symbol[4:],
                #                  exchange=kite.EXCHANGE_NFO,
                #                  transaction_type=kite.TRANSACTION_TYPE_SELL,
                #                  quantity=min_quantity,
                #                  order_type=kite.ORDER_TYPE_LIMIT,
                #                  price=round(market_price_atm_put, 1),
                #                  variety=kite.VARIETY_REGULAR,
                #                  product=kite.PRODUCT_NRML,
                #                  validity=kite.VALIDITY_DAY)
                print(f"Successfully placed sell order for {atm_put_trading_symbol} at market price: {market_price_atm_put}")
                call_send_message(f"Successfully placed sell order for {atm_put_trading_symbol} at market price: {market_price_atm_put}")
                
                # Save the order details
                order_details = {
                    'timestamp': str(datetime.now()),
                    'instrument_token': instrument_token,
                    'transaction_type': 'SELL',
                    'symbol': atm_put_trading_symbol,
                    'quantity': min_quantity,
                    'price': market_price_atm_put,
                    'strike_price': atm_strike_price,
                    'strike_type': 'ATM'
                }
                save_order_details(order_details)
            else:
                print("Error: 'last_price' not found in market data for ATM put option")
                call_send_message("Error: 'last_price' not found in market data for ATM put option")
                

    except Exception as e:
        print(f"Error placing {transaction_type} order: {e}")
        call_send_message(f"Error placing {transaction_type} order: {e}")
        

def place_order2(instrument_token, atm_strike_price, min_quantity, transaction_type):
    symbol = strike_price_dict[instrument_token]['symbol']
    expiry = strike_price_dict[instrument_token]['expiry']

    # Determine the put option strikes
    atm_call_trading_symbol = f"NFO:{symbol}{expiry}{atm_strike_price}CE"
    itm_call_strike_price = atm_strike_price + 2 * strike_price_dict[instrument_token]['strike_difference']
    itm_call_trading_symbol = f"NFO:{symbol}{expiry}{itm_call_strike_price}CE"

    try:
        if transaction_type == kite.TRANSACTION_TYPE_BUY:
            # Buy ITM call option
            ltp_data_itm_call = kite.ltp(itm_call_trading_symbol)[itm_call_trading_symbol]
            if 'last_price' in ltp_data_itm_call and ltp_data_itm_call['last_price'] is not None:
                market_price_itm_call = ltp_data_itm_call['last_price'] + 0.10
                # kite.place_order(tradingsymbol=itm_call_trading_symbol[4:],
                #                  exchange=kite.EXCHANGE_NFO,
                #                  transaction_type=kite.TRANSACTION_TYPE_BUY,
                #                  quantity=min_quantity,
                #                  order_type=kite.ORDER_TYPE_LIMIT,
                #                  price=round(market_price_itm_call, 1),
                #                  variety=kite.VARIETY_REGULAR,
                #                  product=kite.PRODUCT_NRML,
                #                  validity=kite.VALIDITY_DAY)
                print(f"Successfully placed buy order for {itm_call_trading_symbol} at market price: {market_price_itm_call}")
                call_send_message(f"Successfully placed buy order for {itm_call_trading_symbol} at market price: {market_price_itm_call}")
                
                # Save the order details
                order_details = {
                    'timestamp': str(datetime.now()),
                    'instrument_token': instrument_token,
                    'transaction_type': 'BUY',
                    'symbol': itm_call_trading_symbol,
                    'quantity': min_quantity,
                    'price': market_price_itm_call,
                    'strike_price': itm_call_strike_price,
                    'strike_type': 'ITM'
                }
                save_order_details2(order_details)
            else:
                print("Error: 'last_price' not found in market data for OTM call option")
                call_send_message("Error: 'last_price' not found in market data for OTM call option")
                
        elif transaction_type == kite.TRANSACTION_TYPE_SELL:
            # Sell ATM call option
            ltp_data_atm_call = kite.ltp(atm_call_trading_symbol)[atm_call_trading_symbol]
            if 'last_price' in ltp_data_atm_call and ltp_data_atm_call['last_price'] is not None:
                market_price_atm_call = ltp_data_atm_call['last_price'] -0.10
                # kite.place_order(tradingsymbol=atm_call_trading_symbol[4:],
                #                  exchange=kite.EXCHANGE_NFO,
                #                  transaction_type=kite.TRANSACTION_TYPE_SELL,
                #                  quantity=min_quantity,
                #                  order_type=kite.ORDER_TYPE_LIMIT,
                #                  price=round(market_price_atm_call, 1),
                #                  variety=kite.VARIETY_REGULAR,
                #                  product=kite.PRODUCT_NRML,
                #                  validity=kite.VALIDITY_DAY)
                print(f"Successfully placed sell order for {atm_call_trading_symbol} at market price: {market_price_atm_call}")
                call_send_message(f"Successfully placed sell order for {atm_call_trading_symbol} at market price: {market_price_atm_call}")
                
                # Save the order details
                order_details = {
                    'timestamp': str(datetime.now()),
                    'instrument_token': instrument_token,
                    'transaction_type': 'SELL',
                    'symbol': atm_call_trading_symbol,
                    'quantity': min_quantity,
                    'price': market_price_atm_call,
                    'strike_price': atm_strike_price,
                    'strike_type': 'ATM'
                }
                save_order_details2(order_details)
            else:
                print("Error: 'last_price' not found in market data for ATM call option")
                call_send_message("Error: 'last_price' not found in market data for ATM call option")
                

    except Exception as e:
        print(f"Error placing {transaction_type} order: {e}")
        call_send_message(f"Error placing {transaction_type} order: {e}")
        



def square_off_order(order_details):
    symbol = order_details['symbol']
    quantity = order_details['quantity']
    transaction_type = kite.TRANSACTION_TYPE_BUY if order_details['transaction_type'] == 'SELL' else kite.TRANSACTION_TYPE_SELL
    strike_type = order_details.get('strike_type', '')

    try:
        ltp_data = kite.ltp(symbol)[symbol]
        if 'last_price' in ltp_data and ltp_data['last_price'] is not None:
            last_price = ltp_data['last_price']
            if strike_type == 'ATM':
                market_price = last_price -0.10 if transaction_type == kite.TRANSACTION_TYPE_SELL else last_price + 0.10
            elif strike_type == 'OTM':
                market_price = last_price -0.10 if transaction_type == kite.TRANSACTION_TYPE_SELL else last_price + 0.10
            else:
                market_price = last_price  # No multiplier for other strike types

            # kite.place_order(tradingsymbol=symbol[4:],
            #                  exchange=kite.EXCHANGE_NFO,
            #                  transaction_type=transaction_type,
            #                  quantity=quantity,
            #                  order_type=kite.ORDER_TYPE_LIMIT,
            #                  price=round(market_price, 1),
            #                  variety=kite.VARIETY_REGULAR,
            #                  product=kite.PRODUCT_NRML,
            #                  validity=kite.VALIDITY_DAY)
            print(f"Successfully placed square off order for {symbol} at limit price: {market_price}")
            call_send_message(f"Successfully placed square off order for {symbol} at limit price: {market_price}")
            
            
        else:
            print(f"Error: 'last_price' not found in market data for {symbol}")
            call_send_message(f"Error: 'last_price' not found in market data for {symbol}")
            
    except Exception as e:
        print(f"Error placing square off order for {symbol}: {e}")
        call_send_message(f"Error placing square off order for {symbol}: {e}")
        

def square_off_order2(order_details):
    symbol = order_details['symbol']
    quantity = order_details['quantity']
    transaction_type = kite.TRANSACTION_TYPE_BUY if order_details['transaction_type'] == 'SELL' else kite.TRANSACTION_TYPE_SELL
    strike_type = order_details.get('strike_type', '')

    try:
        ltp_data = kite.ltp(symbol)[symbol]
        if 'last_price' in ltp_data and ltp_data['last_price'] is not None:
            last_price = ltp_data['last_price']
            if strike_type == 'ATM':
                market_price = last_price -0.10 if transaction_type == kite.TRANSACTION_TYPE_SELL else last_price + 0.10
            elif strike_type == 'ITM':
                market_price = last_price -0.10 if transaction_type == kite.TRANSACTION_TYPE_SELL else last_price + 0.10
            else:
                market_price = last_price  # No multiplier for other strike types
            # kite.place_order(tradingsymbol=symbol[4:],
            #                  exchange=kite.EXCHANGE_NFO,
            #                  transaction_type=transaction_type,
            #                  quantity=quantity,
            #                  order_type=kite.ORDER_TYPE_LIMIT,
            #                  price=round(market_price, 1),
            #                  variety=kite.VARIETY_REGULAR,
            #                  product=kite.PRODUCT_NRML,
            #                  validity=kite.VALIDITY_DAY)
            print(f"Successfully placed square off order for {symbol} at limit price: {market_price}")
            call_send_message(f"Successfully placed square off order for {symbol} at limit price: {market_price}")
            
        else:
            print(f"Error: 'last_price' not found in market data for {symbol}")
            call_send_message(f"Error: 'last_price' not found in market data for {symbol}")
            
    except Exception as e:
        print(f"Error placing square off order for {symbol}: {e}")
        call_send_message(f"Error placing square off order for {symbol}: {e}")
        

def read_existing_orders():
    try:
        with open(order_file, 'r') as file:
            orders = [json.loads(line) for line in file]
        return orders
    except FileNotFoundError:
        return []

def read_existing_orders2():
    try:
        with open(order_file2, 'r') as file:
            orders = [json.loads(line) for line in file]
        return orders
    except FileNotFoundError:
        return []

def check_existing_orders(instrument_token):
    for order in read_existing_orders():
        if order['instrument_token'] == instrument_token :
            return True
    return False

def check_existing_orders2(instrument_token):
    for order in read_existing_orders2():
        if order['instrument_token'] == instrument_token :
            return True
    return False

date_list = ['2024-06-21', '2024-06-27']

def is_today_expiry(date_list):
    today = datetime.now().date()
    for date_str in date_list:
        date = datetime.strptime(date_str, '%Y-%m-%d').date() 
        if today == date:
            return True
    return False

def get_current_and_next_month():
    current_date = datetime.now()
    current_month_name = current_date.strftime('%b').upper()
    next_month_date = current_date + timedelta(days=30)  # Adding approximate days for next month
    next_month_name = next_month_date.strftime('%b').upper()

    return current_month_name, next_month_name

# Define variables to store last close prices
last_close_prices = {}
last_close_price_nifty = None

# List of instrument tokens to check
instrument_tokens = [ 341249,738561,1270529,408065,424961,2939649,779521,2953217,1510401,2714625]# Replace with your instrument tokens
nifty_instrument_token = 256265 # Replace with your Nifty index token

# Dictionary to store strike price difference and minimum quantity
strike_price_dict =load_strike_price_dict()
        
def on_ticks(ws, ticks):
    global last_close_prices, last_close_price_nifty
    for tick in ticks:
        instrument_token = tick['instrument_token']
        
        if instrument_token in instrument_tokens:
            last_close_prices[instrument_token] = tick['last_price']
        elif instrument_token == nifty_instrument_token:
            last_close_price_nifty = tick['last_price']

    # Ensure we have last close prices for both the instrument tokens and Nifty index token
    if last_close_price_nifty is not None:
        print("Last Close Price of Nifty Index Token:", last_close_price_nifty)

        for instrument_token in instrument_tokens:
            if instrument_token in last_close_prices:
                last_close_price_instrument = last_close_prices[instrument_token]
                print(f"Last Close Price of Instrument Token {instrument_token}:", last_close_price_instrument)
                
                # Print both prices together
                print(f"Instrument Token: {instrument_token}, Last Close Price: {last_close_price_instrument}, Nifty Last Close Price: {last_close_price_nifty}")

                # Check if the instrument_token exists in strike_price_dict
                if instrument_token in strike_price_dict:
                  
                    # Calculate ATM strike price
                    atm_strike_price = calculate_atm_strike_price(last_close_price_instrument, strike_price_dict[instrument_token]['strike_difference'])
                    if instrument_token not in square_off_orderss:
                        if not check_existing_orders(instrument_token):
                            signal, last_traded_price = buy_signal(instrument_token, last_close_price_instrument, last_close_price_nifty)
                            if signal:
                                strike_difference = strike_price_dict[instrument_token]['strike_difference']
                                min_quantity = strike_price_dict[instrument_token]['min_quantity']
                                atm_strike_price = calculate_atm_strike_price(last_traded_price, strike_difference)
                                place_order(instrument_token, atm_strike_price, min_quantity, kite.TRANSACTION_TYPE_BUY)
                                place_order(instrument_token, atm_strike_price, min_quantity, kite.TRANSACTION_TYPE_SELL)
                                place_order_fut(instrument_token,min_quantity,kite.TRANSACTION_TYPE_BUY)
                                print(f"Buy Order Placed for Instrument Token: {instrument_token} at ATM strike price: {atm_strike_price}")
    
                        else:
                            if sell_signal(instrument_token, last_close_price_instrument, last_close_price_nifty):
                                with open(order_file, 'r') as file:
                                    orders = [json.loads(line) for line in file]
                                orders_to_square_off = [order for order in orders if order['instrument_token'] == instrument_token]
                                orders_to_square_off.reverse()
                                for order in orders_to_square_off:
                                    # print(order)
                                    print("sellllllllllllllllllllllllll")
                                    square_off_order(order)
                                    square_off_orderss.append(order['instrument_token'])
                                    remove_order_details(order)
                                    print(f"Sell Order Placed for Instrument Token: {instrument_token} at strike price: {order['symbol']}")

                            else:
                                print("No sell signal detected for", instrument_token, ". Continuing to monitor prices.")

                    if instrument_token not in square_off_bear:
                        print("hello    ")                       
                        if not check_existing_orders2(instrument_token):   
                            bear_signal ,last_traded_price = short_signal (instrument_token,last_close_price_instrument,last_close_price_nifty)
                            if bear_signal:
                                strike_difference=strike_price_dict[instrument_token]['strike_difference']
                                min_quantity= strike_price_dict[instrument_token]['min_quantity']
                                atm_strike_price=calculate_atm_strike_price(last_traded_price,strike_difference)
                                place_order2(instrument_token,atm_strike_price,min_quantity,kite.TRANSACTION_TYPE_BUY)
                                place_order2(instrument_token,atm_strike_price,min_quantity,kite.TRANSACTION_TYPE_SELL)
                                place_order_fut(instrument_token,min_quantity,kite.TRANSACTION_TYPE_SELL)
                        else:
                            if sell_signal(instrument_token, last_close_price_instrument, last_close_price_nifty):
                                with open(order_file, 'r') as file:
                                    orders = [json.loads(line) for line in file]
                                orders_to_square_off = [order for order in orders if order['instrument_token'] == instrument_token]
                                orders_to_square_off.reverse()
                                for order in orders_to_square_off:
                                    # print(order)
                                    print("sellllllllllllllllllllllllll")
                                    square_off_order(order)
                                    square_off_bear.append(order['instrument_token'])
                                    remove_order_details(order)
                                    print(f"Sell Order Placed for Instrument Token: {instrument_token} at strike price: {order['symbol']}")

                            else:
                                print("No sell signal detected for", instrument_token, ". Continuing to monitor prices.")
                else:
                    print(f"Instrument token {instrument_token} is not in strike_price_dict")
                                
    current_time = datetime.now().time()
    print(current_time)
    end_time = time(15,15)  # 3:15 PM
    if current_time >=end_time:
        call_send_message("Its 3 :15 code!!!!!!!!")
        if is_today_expiry(date_list):
            current_month,next_month = get_current_and_next_month()
            update_expiry(strike_price_dict,f"24{current_month}",f"24{next_month}")
            save_strike_price_dict(strike_price_dict)
            if not is_file_empty("long.txt"):
                with open(order_file, 'r') as file:
                    orders = [json.loads(line) for line in file]
                orders.reverse()
                for order in orders:
                    square_off_order(order)
                    remove_order_details(order)
                    tm.sleep(0.2)
            else:
                with open(order_file2, 'r') as file:
                    orders = [json.loads(line) for line in file]
                orders.reverse()
                for order in orders:
                    square_off_order(order)
                    remove_order_details(order)
                    tm.sleep(0.2)

            ws.on_ticks=on_ticks2
        else:
            process_orders()
            # process_orders2()
            # print('processingggggg')
            # if not is_file_empty(order_file):
            #     process_orders()
            # else:process_orders2()
            
        ws.on_ticks=on_ticks2

def on_ticks2(ws, ticks):
    global last_close_prices, last_close_price_nifty
    # Capture the last close prices
    print(ticks)
    for tick in ticks:
        instrument_token = tick['instrument_token']
        
        if instrument_token in instrument_tokens:
            last_close_prices[instrument_token] = tick['last_price']
        elif instrument_token == nifty_instrument_token:
            last_close_price_nifty = tick['last_price']

    # Ensure we have last close prices for both the instrument tokens and Nifty index token
    if last_close_price_nifty is not None:
        print("Last Close Price of Nifty Index Token:", last_close_price_nifty)

        for instrument_token in instrument_tokens:
            if instrument_token in last_close_prices:
                last_close_price_instrument = last_close_prices[instrument_token]
                print(f"Last Close Price of Instrument Token {instrument_token}:", last_close_price_instrument)
                
                # Print both prices together
                print(f"Instrument Token: {instrument_token}, Last Close Price: {last_close_price_instrument}, Nifty Last Close Price: {last_close_price_nifty}")

                # Check if the instrument_token exists in strike_price_dict
                if instrument_token in strike_price_dict:
                  
                    # Calculate ATM strike price
                    atm_strike_price = calculate_atm_strike_price(last_close_price_instrument, strike_price_dict[instrument_token]['strike_difference'])
                    if instrument_token not in square_off_orderss2:
                        if not check_existing_orders(instrument_token):
                            signal, last_traded_price = buy_signal(instrument_token, last_close_price_instrument, last_close_price_nifty)
                            if signal:
                                strike_difference = strike_price_dict[instrument_token]['strike_difference']
                                min_quantity = strike_price_dict[instrument_token]['min_quantity']
                                atm_strike_price = calculate_atm_strike_price(last_traded_price, strike_difference)
                                buy_signal(instrument_token, last_close_price_instrument, last_close_price_nifty)
                                place_order(instrument_token, atm_strike_price, min_quantity, kite.TRANSACTION_TYPE_BUY)
                                place_order(instrument_token, atm_strike_price, min_quantity, kite.TRANSACTION_TYPE_SELL)
                                place_order_fut(instrument_token,min_quantity,kite.TRANSACTION_TYPE_BUY)
                                print(f"Buy Order Placed for Instrument Token: {instrument_token} at ATM strike price: {atm_strike_price}")
    
                        else:
                            if sell_signal(instrument_token, last_close_price_instrument, last_close_price_nifty):
                                with open(order_file, 'r') as file:
                                    orders = [json.loads(line) for line in file]
                                orders_to_square_off = [order for order in orders if order['instrument_token'] == instrument_token]
                                orders_to_square_off.reverse()
                                for order in orders_to_square_off:
                                    # print(order)
                                    print("sellllllllllllllllllllllllll")
                                    square_off_order(order)
                                    square_off_orderss2.append(order['instrument_token'])
                                    remove_order_details(order)
                                    print(f"Sell Order Placed for Instrument Token: {instrument_token} at strike price: {order['symbol']}")

                            else:
                                print("No sell signal detected for", instrument_token, ". Continuing to monitor prices.")

                    
                    if instrument_token not in square_off_bear2:
                        if not check_existing_orders2(instrument_token):
                            bear_signal ,last_traded_price = short_signal (instrument_token,last_close_price_instrument,last_close_price_nifty)
                            if bear_signal:
                                strike_difference=strike_price_dict[instrument_token]['strike_difference']
                                min_quantity= strike_price_dict[instrument_token]['min_quantity']
                                atm_strike_price=calculate_atm_strike_price(last_traded_price,strike_difference)
                                place_order2(instrument_token,atm_strike_price,min_quantity,kite.TRANSACTION_TYPE_BUY)
                                place_order2(instrument_token,atm_strike_price,min_quantity,kite.TRANSACTION_TYPE_SELL)
                                place_order_fut(instrument_token,min_quantity,kite.TRANSACTION_TYPE_SELL)

                            else:
                                if sell_short(instrument_token,last_close_price_instrument,last_close_price_nifty):
                                    with open(order_file2,'r') as file:
                                        orders = [json.loads(line) for line in file]
                                    orders_to_squar_off2 = [order for order in  orders if order['instrument_token']== instrument_token]
                                    orders_to_squar_off2.reverse()
                                    for order in orders_to_squar_off2:
                                        print("selll shorts")
                                        square_off_order(order)
                                        square_off_bear2.append(order['instrument_token'])
                                        remove_order_details2(order)
                                        print(f"Sell Order Placed for Instrument Token: {instrument_token} at strike price: {order['symbol']}")

                                else:
                                    print("No BEAR sell signal detected for", instrument_token, ". Continuing to monitor prices.")

                else:
                    print(f"Instrument token {instrument_token} is not in strike_price_dict")

def on_connect(ws, response):
    ws.subscribe(instrument_tokens + [nifty_instrument_token])


def on_close(ws, code, reason):
    ws.stop()

# Initialize WebSocket
kws = KiteTicker("5gio34lqmlmn83a5",access_token)

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

kws.connect()
