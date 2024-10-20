import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers.command_handlers import start, register
from handlers.image_handler import handle_payment_image

# Telegram bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

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

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
