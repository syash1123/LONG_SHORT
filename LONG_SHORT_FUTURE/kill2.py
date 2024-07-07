# from typing import Final
# from telegram import Update
# from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes

# TOKEN: Final = '7031311606:AAH8eVbdxkQpAPTW6b4zPQu5zJ8z_Q3CyLc'
# BOT_USERNAME :Final = '@ALPHA'

# async def start_command(update: Update,context:ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Hellooo")

# async def help_command(update: Update,context:ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Iam bana bot")

# async def start_command(update: Update,context:ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Hellooo")

# async def custom_command(update: Update,context:ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("This is a custom command")

# def handle_response(text: str)->str:
#     processed:str =text.lower()

#     if 'hello' in processed:
#         return 'HEY there'
#     if 'sexy ' in processed:
#         return 'Iam good'
#     return 'I do not understand .'

# async def handle_message(update:Update,context :ContextTypes.DEFAULT_TYPE):
#     message_type :str =update.message.chat.type
#     text:str = update.message.text

#     print(f'USER ({update.message.chatid}) in {message_type}: "{test}')

#     if message_type=='group':
#         if BOT_USERNAME in text:
#             new_text:str =text.replace(BOT_USERNAME,'').strip()
#             response:str=handle_response(new_text)
#         else:
#             return
#     else:
#         response: str=handle_response(text)

#     print('Bot ',response)
#     await update.message.reply_text(response)

# async def error(update: Update,context :ContextTypes.DEFAULT_TYPE):
#     print(f"Update {update} caused error {context.error}")

# if __name__ =='__main__':
#     app=Application.builder().token(TOKEN).build()

#     app.add_handler(CommandHandler('start',start_command))
#     app.add_handler(CommandHandler('help',help_command))
#     app.add_handler(CommandHandler('start',custom_command))
#     app.add_error_handler(error)

#     app.add_handler(MessageHandler(filters.TEXT,handle_response))
#     app.run_polling(poll_interval=3)

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '7031311606:AAH8eVbdxkQpAPTW6b4zPQu5zJ8z_Q3CyLc'
BOT_USERNAME = '@ALPHA'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your bot. How can I help you?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I can respond to your messages. Just type something!")

def handle_response(text: str) -> str:
    processed = text.lower()
    if 'hello' in processed:
        return 'Hey there!'
    if 'how are you' in processed:
        return 'I am just a bot, but I am doing great!'
    return 'I do not understand.'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = handle_response(text)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.add_error_handler(error)

    print("Bot is running...")
    app.run_polling()


