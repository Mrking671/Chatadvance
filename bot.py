import os
import datetime
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

# Read environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BLOGSPOT_URL = os.getenv('BLOGSPOT_URL')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

app = Flask(__name__)

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
    context.bot.send_message(chat_id=update.effective_chat.id, text="This is a response from the bot.")

# Define the webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, updater.bot)
    dp.process_update(update)
    return jsonify(success=True)

# Set up webhook for Telegram
def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    updater.bot.set_webhook(url=webhook_url)

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=80)
