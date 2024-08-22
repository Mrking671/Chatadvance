import os
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BLOGSPOT_URL = os.getenv('BLOGSPOT_URL')

# Initialize Updater and Dispatcher
updater = Updater(token=TELEGRAM_TOKEN)
dp = updater.dispatcher

# Define handlers and commands
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    last_verify_time = context.chat_data.get('last_verify_time')
    current_time = datetime.datetime.now()

    # Check if verification is required
    if last_verify_time and (current_time - last_verify_time).seconds < 3600:
        context.bot.send_message(chat_id=user_id, text="Please verify to continue.")
        return

    # Send verification message with button
    keyboard = [[
        InlineKeyboardButton("Verify", url=BLOGSPOT_URL)
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=user_id, text="Click the button below to verify.", reply_markup=reply_markup)

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    last_verify_time = context.chat_data.get('last_verify_time')
    current_time = datetime.datetime.now()

    # Check if verification is required
    if last_verify_time and (current_time - last_verify_time).seconds < 3600:
        context.bot.send_message(chat_id=user_id, text="Please verify to continue.")
        return

    # Send a response
    context.bot.send_message(chat_id=user_id, text="This is a response from the bot.")

def verify(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    context.chat_data['last_verify_time'] = datetime.datetime.now()
    context.bot.send_message(chat_id=user_id, text="Verification successful! You can now use the bot.")

# Add handlers to dispatcher
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('verify', verify))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Start polling for updates
updater.start_polling()
updater.idle()
