from telegram import Update
from telegram.ext import ContextTypes
from utils.file_utils import load_users, save_users

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

    if str(user_id) in registered_users:
        await update.message.reply_text(f"You are already registered!")
    else:
        registered_users[str(user_id)] = {"username": username, "payment_verified": False}
        save_users(registered_users)
        await update.message.reply_text("Registration successful! Please send the payment confirmation image.")
