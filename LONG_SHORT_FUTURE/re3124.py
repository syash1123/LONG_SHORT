import logging
import json
from datetime import datetime
from kiteconnect import KiteConnect
from collections import defaultdict
import ast
import asyncio
from telegram import Bot

# Your bot's API token
bot_token = '7031311606:AAH8eVbdxkQpAPTW6b4zPQu5zJ8z_Q3CyLc'
bot = Bot(token=bot_token)

# Async function to send message to Telegram
async def send_telegram_message(message):
    # chat_id = -4249796811
    # chat_id = -1002228606742
    chat_id = 6235508050  # Replace with your numeric chat ID
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
    chat_id = 6863806813# Replace with your numeric chat ID
    await bot.send_message(chat_id=chat_id, text=message)

# Function to call send_telegram_message asynchronously within the existing event loop
def call_send_message2(message):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(send_telegram_message2(message))

    


# File path for the strike price dictionary
STRIKE_PRICE_FILE = 'strike.txt'

# Function to load the strike price dictionary from the file
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

# # Setup logging
# logging.basicConfig(level=logging.DEBUG)


# Initialize Kite Connect
kite = KiteConnect(api_key="5gio34lqmlmn83a5")
kite.set_access_token("sjMcPbysnWOBiOqnCkfjQyOki9dqKHCp")


strike_price_dict=load_strike_price_dict()
# Order file
order_file = "long.txt"
order_file2="short.txt"

def fetch_last_price(instrument_token):
    ltp = kite.ltp([instrument_token])
    return ltp[str(instrument_token)]['last_price']

# def fetch_last_price2(trading_symbol):
#     ltp = kite.ltp([trading_symbol])
#     return ltp[trading_symbol]['last_price']

def calculate_atm_strike_price(last_traded_price, strike_difference):
    return round(last_traded_price / strike_difference) * strike_difference

def square_off_position315(tradingsymbol, transaction_type, quantity):
    try:
        print("Squaring off position")
        ltp = kite.ltp([tradingsymbol])[tradingsymbol]['last_price']
        if transaction_type == "BUY":
            limit_price = round(ltp -0.10, 1)  # Set limit price for SELL order
            new_transaction_type = kite.TRANSACTION_TYPE_SELL
        elif transaction_type == "SELL":
            limit_price = round(ltp + 0.10, 1)  # Set limit price for BUY order
            new_transaction_type = kite.TRANSACTION_TYPE_BUY
        kite.place_order(
            tradingsymbol=tradingsymbol[4:],
            exchange="NFO",
            transaction_type=new_transaction_type,
            quantity=quantity,
            order_type=kite.ORDER_TYPE_LIMIT,
            price=limit_price,
            product=kite.PRODUCT_NRML,
            variety=kite.VARIETY_REGULAR
        )
        logging.info(f"Successfully placed {new_transaction_type} order for {tradingsymbol} at limit price {limit_price}")
        call_send_message(f"Successfully placed {new_transaction_type} order for {tradingsymbol} at limit price {limit_price}")
        call_send_message2(f"Successfully placed {new_transaction_type} order for {tradingsymbol} at limit price {limit_price}")
    except Exception as e:
        logging.error(f"Error placing order for {tradingsymbol}: {e}")
        call_send_message(f"Error placing order for {tradingsymbol}: {e}")
        call_send_message2(f"Error placing order for {tradingsymbol}: {e}")

def place_order3(instrument_token, strike_price, min_quantity, transaction_type, strike_type):
    symbol = strike_price_dict[instrument_token]['symbol']
    expiry = strike_price_dict[instrument_token]['expiry']
    trading_symbol = f"NFO:{symbol}{expiry}{strike_price}PE"
    last_price = ltp = kite.ltp([trading_symbol])[trading_symbol]['last_price']
    print(last_price)
    if transaction_type== kite.TRANSACTION_TYPE_BUY:
        limit_price=last_price + 0.10
    else:
        limit_price=last_price -0.10
    # limit_price = round(last_price * (0.8 if transaction_type == kite.TRANSACTION_TYPE_SELL else 1.2), 1)

    try:
        kite.place_order(
            tradingsymbol=trading_symbol[4:],
            exchange=kite.EXCHANGE_NFO,
            transaction_type=transaction_type,
            quantity=min_quantity,
            order_type=kite.ORDER_TYPE_LIMIT,
            price=limit_price,
            variety=kite.VARIETY_REGULAR,
            product=kite.PRODUCT_NRML,
            validity=kite.VALIDITY_DAY
        )
        print("Order has been placed")
        call_send_message(f"Successfully placed  order for {trading_symbol} at limit price {limit_price}")
        call_send_message2(f"Successfully placed  order for {trading_symbol} at limit price {limit_price}")

        order_details = {
            'timestamp': str(datetime.now()),
            'instrument_token': instrument_token,
            'transaction_type': transaction_type,
            'symbol': trading_symbol,
            'quantity': min_quantity,
            'price': limit_price,
            'strike_price': strike_price,
            'strike_type': strike_type
        }
        return order_details
    except Exception as e:
        logging.error(f"Error placing {transaction_type} order: {e}")
        call_send_message(f"Error placing {transaction_type} order: {e}")
        call_send_message2(f"Error placing {transaction_type} order: {e}")
        return None

def place_order4(instrument_token, strike_price, min_quantity, transaction_type, strike_type):
    symbol = strike_price_dict[instrument_token]['symbol']
    expiry = strike_price_dict[instrument_token]['expiry']
    trading_symbol = f"NFO:{symbol}{expiry}{strike_price}CE"
    last_price = ltp = kite.ltp([trading_symbol])[trading_symbol]['last_price']
    print(last_price)
    if transaction_type== kite.TRANSACTION_TYPE_BUY:
        limit_price=last_price + 0.10
    else:
        limit_price=last_price -0.10
    # limit_price = round(last_price * (0.8 if transaction_type == kite.TRANSACTION_TYPE_SELL else 1.2), 1)

    try:
        kite.place_order(
            tradingsymbol=trading_symbol[4:],
            exchange=kite.EXCHANGE_NFO,
            transaction_type=transaction_type,
            quantity=min_quantity,
            order_type=kite.ORDER_TYPE_LIMIT,
            price=limit_price,
            variety=kite.VARIETY_REGULAR,
            product=kite.PRODUCT_NRML,
            validity=kite.VALIDITY_DAY
        )
        print("Order has been placed")
        call_send_message(f"Successfully placed order for {trading_symbol} at limit price {limit_price}")
        call_send_message2(f"Successfully placed order for {trading_symbol} at limit price {limit_price}")

        order_details = {
            'timestamp': str(datetime.now()),
            'instrument_token': instrument_token,
            'transaction_type': transaction_type,
            'symbol': trading_symbol,
            'quantity': min_quantity,
            'price': limit_price,
            'strike_price': strike_price,
            'strike_type': strike_type
        }
        return order_details
    except Exception as e:
        logging.error(f"Error placing {transaction_type} order: {e}")
        call_send_message(f"Error placing {transaction_type} order: {e}")
        call_send_message2(f"Error placing {transaction_type} order: {e}")
        return None


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

def process_orders():
    print('Processing orders')
    try:
        with open(order_file, 'r') as file:
            orders = [json.loads(line) for line in file if line.strip()]

        orders_by_token = defaultdict(list)

        for order in orders:
            orders_by_token[order['instrument_token']].append(order)

        updated_orders = []

        for instrument_token, token_orders in orders_by_token.items():
            if instrument_token not in strike_price_dict:
                updated_orders.extend(token_orders)
                continue

            last_price = fetch_last_price(instrument_token)
            strike_difference = strike_price_dict[instrument_token]['strike_difference']
            min_quantity = strike_price_dict[instrument_token]['min_quantity']

            current_atm_strike_price = calculate_atm_strike_price(last_price, strike_difference)
            current_otm_strike_price = current_atm_strike_price - 2 * strike_difference

            # Filter out FUT orders
            non_fut_orders = [o for o in token_orders if o['strike_type'] != 'FUT']

            # Check if the last ATM order and OTM order are at the current strike prices
            atm_order = next((o for o in non_fut_orders if o['strike_type'] == 'ATM'), None)
            otm_order = next((o for o in non_fut_orders if o['strike_type'] == 'OTM'), None)

            if (atm_order and atm_order['strike_price'] != current_atm_strike_price) or \
               (otm_order and otm_order['strike_price'] != current_otm_strike_price):
                if atm_order:
                    square_off_position315(atm_order['symbol'], atm_order['transaction_type'], atm_order['quantity'])
                if otm_order:
                    square_off_position315(otm_order['symbol'], otm_order['transaction_type'], otm_order['quantity'])

                if otm_order:
                    new_otm_order = place_order3(instrument_token, current_otm_strike_price, min_quantity, otm_order['transaction_type'], 'OTM')
                    if new_otm_order:
                        updated_orders.append(new_otm_order)
                if atm_order:
                    new_atm_order = place_order3(instrument_token, current_atm_strike_price, min_quantity, atm_order['transaction_type'], 'ATM')
                    if new_atm_order:
                        updated_orders.append(new_atm_order)

                for order in non_fut_orders:
                    remove_order_details(order)
            else:
                updated_orders.extend(non_fut_orders)

            # Add FUT orders back in original order
            fut_orders = [o for o in token_orders if o['strike_type'] == 'FUT']
            updated_orders.extend(fut_orders)

        with open(order_file, 'w') as file:
            for order in updated_orders:
                json.dump(order, file)
                file.write("\n")
    except Exception as e:
        logging.error(f"Error processing orders: {e}")


def process_orders2():
    print('Processing orders')
    try:
        with open(order_file2, 'r') as file:
            orders = [json.loads(line) for line in file if line.strip()]

        orders_by_token = defaultdict(list)

        for order in orders:
            orders_by_token[order['instrument_token']].append(order)

        updated_orders = []

        for instrument_token, token_orders in orders_by_token.items():
            if instrument_token not in strike_price_dict:
                updated_orders.extend(token_orders)
                continue

            last_price = fetch_last_price(instrument_token)
            strike_difference = strike_price_dict[instrument_token]['strike_difference']
            min_quantity = strike_price_dict[instrument_token]['min_quantity']

            current_atm_strike_price = calculate_atm_strike_price(last_price, strike_difference)
            current_itm_strike_price = current_atm_strike_price + 2 * strike_difference

            # Filter out FUT orders
            non_fut_orders = [o for o in token_orders if o['strike_type'] != 'FUT']

            # Check if the last ATM order and ITM order are at the current strike prices
            atm_order = next((o for o in non_fut_orders if o['strike_type'] == 'ATM'), None)
            itm_order = next((o for o in non_fut_orders if o['strike_type'] == 'ITM'), None)

            if (atm_order and atm_order['strike_price'] != current_atm_strike_price) or \
               (itm_order and itm_order['strike_price'] != current_itm_strike_price):
                if atm_order:
                    square_off_position315(atm_order['symbol'], atm_order['transaction_type'], atm_order['quantity'])
                if itm_order:
                    square_off_position315(itm_order['symbol'], itm_order['transaction_type'], itm_order['quantity'])

                if itm_irder:
                    new_otm_order = place_order4(instrument_token, current_itm_strike_price, min_quantity, itm_order['transaction_type'], 'ITM')
                    if new_itm_order:
                        updated_orders.append(new_itm_order)
                if atm_order:
                    new_atm_order = place_order4(instrument_token, current_atm_strike_price, min_quantity, atm_order['transaction_type'], 'ATM')
                    if new_atm_order:
                        updated_orders.append(new_atm_order)

                for order in non_fut_orders:
                    remove_order_details2(order)
            else:
                updated_orders.extend(non_fut_orders)

            # Add FUT orders back in original order
            fut_orders = [o for o in token_orders if o['strike_type'] == 'FUT']
            updated_orders.extend(fut_orders)

        with open(order_file2, 'w') as file:
            for order in updated_orders:
                json.dump(order, file)
                file.write("\n")
    except Exception as e:
        logging.error(f"Error processing orders: {e}")
