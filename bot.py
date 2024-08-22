import os
import datetime
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BLOGSPOT_URL = os.getenv('BLOGSPOT_URL')
MONGO_URI = os.getenv('MONGO_URI')

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client['bot_database']
users_collection = db['users']

# Initialize Application
app = Application.builder().token(TELEGRAM_TOKEN).build()

# Define handlers and commands
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    user = users_collection.find_one({'_id': user_id})
    
    current_time = datetime.datetime.now()
    if user:
        last_verify_time = user.get('last_verify_time')
        if last_verify_time:
            last_verify_time = datetime.datetime.fromisoformat(last_verify_time)
            if (current_time - last_verify_time).seconds < 3600:
                await update.message.reply_text("You have already verified. You can now use the bot.")
                return

    # Send verification message with button
    keyboard = [[
        InlineKeyboardButton("Verify", url=BLOGSPOT_URL)
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click the button below to verify. After verification, you can use the bot.", reply_markup=reply_markup)

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    user = users_collection.find_one({'_id': user_id})
    
    current_time = datetime.datetime.now()
    if not user:
        await update.message.reply_text("Please verify to continue using the bot. Use /start to get the verification link.")
        return
    
    last_verify_time = user.get('last_verify_time')
    if last_verify_time:
        last_verify_time = datetime.datetime.fromisoformat(last_verify_time)
        if (current_time - last_verify_time).seconds >= 3600:
            await update.message.reply_text("Please verify to continue using the bot. Use /start to get the verification link.")
            return

    # Send a response
    await update.message.reply_text("This is a response from the bot.")

async def verify(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    current_time = datetime.datetime.now().isoformat()
    
    users_collection.update_one(
        {'_id': user_id},
        {'$set': {'last_verify_time': current_time}},
        upsert=True
    )
    
    await update.message.reply_text("Verification successful! You can now use the bot.")

# Add handlers to application
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('verify', verify))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Start polling for updates
app.run_polling()
