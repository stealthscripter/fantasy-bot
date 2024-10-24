from telegram import Update
from telegram.ext import ContextTypes
import pytz
import datetime
from utils.file_utils import load_users, save_users

DEADLINE = datetime.datetime(2024, 10, 23, 15, 0, 0, tzinfo=pytz.timezone('Africa/Addis_Ababa'))

REGISTERED_USERS_FILE = "registered_users.json"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    display_name = user.first_name
    if user.last_name:
        display_name += f" {user.last_name}"
    await update.message.reply_text(f"Welcome to the Fantasy League {display_name}! Use /register to join the league.")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    registered_users = load_users()

    current_time = datetime.datetime.now(pytz.timezone('Africa/Addis_Ababa'))
    
    if current_time > DEADLINE:
        await update.message.reply_text("The registration deadline has passed. You cannot register for this week's fantasy league.")
        return

    if str(user_id) in registered_users:
        await update.message.reply_text(f"You are already registered!")
    else:
        registered_users[str(user_id)] = {"username": username, "payment_verified": False}
        save_users(registered_users)
        await update.message.reply_text("Registration successful! Please send the payment confirmation image.")
