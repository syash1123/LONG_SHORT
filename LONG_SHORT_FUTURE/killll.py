# import asyncio
# import threading
# from queue import Queue
# from kiteconnect import KiteTicker
# from telegram import Update, Bot
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# # Telegram bot token
# TOKEN = '7031311606:AAH8eVbdxkQpAPTW6b4zPQu5zJ8z_Q3CyLc'
# BOT_USERNAME = '@ALPHA'

# # Initialize the message queue
# message_queue = Queue()

# # Initialize the Telegram bot
# bot = Bot(token=TOKEN)

# # async def send_telegram_message(message):
# #     # chat_id = -4249796811 
# #     chat_id = 2039601966
# #     # chat_id = -1002228606742
# #       # Replace with your numeric chat ID
# #     await bot.send_message(chat_id=chat_id, text=message)

# # # Function to call send_telegram_message asynchronously within the existing event loop
# # def call_send_message(message):
# #     loop = asyncio.get_event_loop()
# #     if loop.is_closed():
# #         loop = asyncio.new_event_loop()
# #         asyncio.set_event_loop(loop)
# #     loop.run_until_complete(send_telegram_message(message))

# # # Async function to send message to Telegram
# # async def send_telegram_message2(message):
# #     # chat_id = -4249796811
# #     # chat_id = -1002228606742
# #     chat_id = 6863806813# SANJAY BHAI CHAT IT
# #     await bot.send_message(chat_id=chat_id, text=message)

# # # Function to call send_telegram_message asynchronously within the existing event loop
# # def call_send_message2(message):
# #     loop = asyncio.get_event_loop()
# #     if loop.is_closed():
# #         loop = asyncio.new_event_loop()
# #         asyncio.set_event_loop(loop)
# #     loop.run_until_complete(send_telegram_message2(message))



# # Function to handle the sending of messages from the queue
# async def process_queue(bot):
#     while True:
#         message = message_queue.get()
#         if message is None:
#             break
#         await bot.send_message(chat_id=2039601966, text=message)
#         await asyncio.sleep(1)  # Respect rate limit
#         message_queue.task_done()

# # Telegram bot handlers
# async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Hello! I'm your bot. How can I help you?")

# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("I can respond to your messages. Just type something!")


# def handle_response(text: str) -> str:
#     processed = text.lower()
#     if 'kill' in processed:
#         return 'I do not unddddderstand.'
#     if 'how are you' in processed:
#         return 'I am just a bot, but I am doing great!'
#     return 'I do not understand.'

# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     text = update.message.text
#     response = handle_response(text)
#     await update.message.reply_text(response)

# async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print(f"Update {update} caused error {context.error}")

# # WebSocket on_ticks function
# def on_ticks(ws, ticks):
#     # Your existing on_ticks logic...
#     for tick in ticks:
#         instrument_token = tick['instrument_token']
#         if instrument_token == 'YOUR_INSTRUMENT_TOKEN_CONDITION':  # Replace with your actual condition
#             message_queue.put("Kill message from on_ticks function")

# def on_connect(ws, response):
#     ws.subscribe(instrument_tokens + [nifty_instrument_token])

# def on_close(ws, code, reason):
#     ws.stop()

# # Function to run the process_queue coroutine in a new event loop
# def start_queue_processor(bot):
#     asyncio.set_event_loop(asyncio.new_event_loop())
#     asyncio.get_event_loop().run_until_complete(process_queue(bot))

# if __name__ == '__main__':
#     # Initialize the Telegram bot application
#     app = Application.builder().token(TOKEN).build()

#     app.add_handler(CommandHandler('start', start_command))
#     app.add_handler(CommandHandler('help', help_command))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#     app.add_error_handler(error)

#     # Start the background task to process the queue in a new thread
#     threading.Thread(target=lambda: start_queue_processor(bot), daemon=True).start()

#     # Start the Telegram bot
#     app.run_polling()

#     # Initialize and connect the WebSocket
#     kws = KiteTicker("5gio34lqmlmn83a5", "3EOxDsDNpGJvpz77DbgNmdt0VZnuCN47")

#     # Assign the callbacks.
#     kws.on_ticks = on_ticks
#     kws.on_connect = on_connect
#     kws.on_close = on_close

#     kws.connect()
import asyncio
import threading
from queue import Queue
from kiteconnect import KiteTicker
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram bot token
TOKEN = '7031311606:AAH8eVbdxkQpAPTW6b4zPQu5zJ8z_Q3CyLc'
BOT_USERNAME = '@ALPHA'

# Initialize the message queue
message_queue = Queue()

# Initialize the Telegram bot
bot = Bot(token=TOKEN)

# Define the function to be called on "kill"
def kill_function():
    print("Executing kill function...")
    # Add your kill function logic here
    call_send_message("Kill function executed.")

async def send_telegram_message(message):
    chat_id = 2039601966
    await bot.send_message(chat_id=chat_id, text=message)

# Function to call send_telegram_message asynchronously within the existing event loop
def call_send_message(message):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(send_telegram_message(message))

# Function to handle the sending of messages from the queue
async def process_queue(bot):
    while True:
        message = message_queue.get()
        if message is None:
            break
        await bot.send_message(chat_id=2039601966, text=message)
        await asyncio.sleep(1)  # Respect rate limit
        message_queue.task_done()

# Telegram bot handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your bot. How can I help you?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I can respond to your messages. Just type something!")

def handle_response(text: str) -> str:
    processed = text.lower()
    if 'kill' in processed:
        kill_function()  # Call the kill function
        return 'Action initiated: squaring off.'
    if 'how are you' in processed:
        return 'I am just a bot, but I am doing great!'
    return 'I do not understand.'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = handle_response(text)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

# WebSocket on_ticks function
def on_ticks(ws, ticks):
    # Your existing on_ticks logic...
    for tick in ticks:
        instrument_token = tick['instrument_token']
        if instrument_token == 'YOUR_INSTRUMENT_TOKEN_CONDITION':  # Replace with your actual condition
            message_queue.put("Kill message from on_ticks function")

def on_connect(ws, response):
    ws.subscribe(instrument_tokens + [nifty_instrument_token])

def on_close(ws, code, reason):
    ws.stop()

# Function to run the process_queue coroutine in a new event loop
def start_queue_processor(bot):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_queue(bot))

# Function to initialize and run the Telegram bot
def start_telegram_bot():
    # Initialize the Telegram bot application
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.add_error_handler(error)

    # Start the Telegram bot polling
    app.run_polling()

# Function to initialize and connect the WebSocket
def start_websocket():
    # Initialize and connect the WebSocket
    kws = KiteTicker("5gio34lqmlmn83a5", "3EOxDsDNpGJvpz77DbgNmdt0VZnuCN47")

    # Assign the callbacks.
    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close

    kws.connect()

if __name__ == '__main__':
    # Start the WebSocket in a separate thread
    threading.Thread(target=start_websocket, daemon=True).start()

    # Start the background task to process the queue in a new thread
    threading.Thread(target=lambda: start_queue_processor(bot), daemon=True).start()

    # Start the Telegram bot in the main thread
    start_telegram_bot()
