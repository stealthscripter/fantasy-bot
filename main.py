from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
from telegram.error import TimedOut

# Telegram bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Define file paths
REGISTERED_USERS_FILE = "registered_users.json"
# Initialize your Selenium WebDrive

urlx = ("https://onefootball.com/en/competition/premier-league-9/fixtures")
# Split the URL by slashes and get the relevant part
parts = urlx.split('/')
# Extract the part that contains the number
competition_part = parts[5]  # This is 'premier-league-9'
# Split that part by the hyphen and get the last element
competition_number = competition_part.split('-')[-1]  # This is '9'

# Increase timeout to 60 seconds (default is usually lower)
application = Application.builder().token(BOT_TOKEN).connect_timeout(10).build()

# Initialize WebDriver for scraping
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Function to load registered users from a file
def load_registered_users():
    if os.path.exists(REGISTERED_USERS_FILE):
        with open(REGISTERED_USERS_FILE, "r") as file:
            return json.load(file)
    return {}

# Function to save registered users to a file
def save_registered_users(users):
    with open(REGISTERED_USERS_FILE, "w") as file:
        json.dump(users, file)

# Scrape fixtures to get the first match of the game week
def get_first_match():
    driver.get("https://onefootball.com/en/competition/premier-league-9/fixtures")
    today = datetime.utcnow()
    next_week = today + timedelta(days=7)
    
    try:
        match_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.MatchCard_matchCard__iOv4G"))
        )
        fixtures = []
        for match_card in match_cards:
            teams = match_card.find_elements(By.CSS_SELECTOR, ".SimpleMatchCardTeam_simpleMatchCardTeam__name__7Ud8D")
            home_team = teams[0].text if len(teams) > 0 else "Unknown Home Team"
            away_team = teams[1].text if len(teams) > 1 else "Unknown Away Team"
            match_date_element = match_card.find_element(By.CSS_SELECTOR, "time.title-8-bold")
            match_date_str = match_date_element.get_attribute("datetime")
            match_date = datetime.fromisoformat(match_date_str[:-1])

            if today <= match_date < next_week:
                fixtures.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': match_date
                })

        # Return the earliest match
        if fixtures:
            return min(fixtures, key=lambda x: x['date'])
        return None
    except Exception as e:
        print(f"Error: {e}")
    return None

# Start command handler
async def start(update: Update, context):
    await update.message.reply_text("Welcome to the Fantasy League! Use /register to join the league.")

# Register command handler
async def register(update: Update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    registered_users = load_registered_users()

    first_match = get_first_match()

    if first_match:
        now = datetime.utcnow()
        registration_deadline = first_match['date'] - timedelta(hours=2)

        if now >= registration_deadline:
            await update.message.reply_text("Sorry, registration for this game week has closed. Please register for the next game week.")
            return

    if str(user_id) in registered_users:
        await update.message.reply_text(f"You are already registered! for game week {competition_number} ")
    else:
        registered_users[str(user_id)] = {"username": username, "payment_verified": False}
        save_registered_users(registered_users)
        await update.message.reply_text(f"Registration successful you registered for game week {competition_number}! Please send the payment via telebirr +251941267019   confirmation image.")

async def notify_first_match(context):
    registered_users = load_registered_users()
    first_match = get_first_match()

    if first_match:
        message = f"The first game of this game week is {first_match['home_team']} vs {first_match['away_team']} on {first_match['date']}. Make sure to finalize your team before the game starts!"
        for user_id in registered_users.keys():
            await safe_send_message(context, chat_id=user_id, text=message)

# Main bot function remains the same.


# Notify users about the first match
async def notify_first_match(context):
    registered_users = load_registered_users()
    first_match = get_first_match()

    if first_match:
        message = f"The first game of this game week is {first_match['home_team']} vs {first_match['away_team']} on {first_match['date']}. Make sure to finalize your team before the game starts!"
        for user_id in registered_users.keys():
            await context.bot.send_message(chat_id=user_id, text=message)

# Handle payment confirmation images
async def handle_payment_image(update: Update, context):
    user = update.message.from_user
    username = user.username if user.username else f"User_{user.id}"
    
    photo = update.message.photo[-1]  # Get the highest resolution photo
    try:
        photo_file = await photo.get_file()

        photo_path = f"payment_confirmations/{username}_payment.jpg"
        await photo_file.download_to_drive(photo_path)
        
        await update.message.reply_text("Image received and saved successfully! We will check if your payment is verified.")
    
    except TimedOut:
        await update.message.reply_text("The request timed out. Please try again.")
        await asyncio.sleep(5)
        await handle_payment_image(update, context)
    
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    
    # Handle images for payment confirmation
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_image))
    
    # Create directory for saving payment confirmation images
    if not os.path.exists("payment_confirmations"):
        os.makedirs("payment_confirmations")

    # Schedule a task to notify users about the first match of the week
    first_match = get_first_match()
    if first_match:
        notification_time = first_match['date'] - timedelta(hours=2)
        application.job_queue.run_once(notify_first_match, when=notification_time)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
