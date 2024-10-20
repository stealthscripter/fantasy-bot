import datetime

async def handle_payment_image(update, context):
    user = update.message.from_user
    username = user.username if user.username else f"User_{user.id}"
    
    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    
    photo = update.message.photo[-1]  # Get the highest resolution photo
    try:
        photo_file = await photo.get_file()

        # Add timestamp to the file name
        photo_path = f"payment_confirmations/{username}_payment_{timestamp}.jpg"
        await photo_file.download_to_drive(photo_path)
        
        await update.message.reply_text("Image received and saved successfully! We will check if your payment is verified.")
    
    except TimedOut:
        await update.message.reply_text("The request timed out. Please try again.")
        await asyncio.sleep(5)
        await handle_payment_image(update, context)
    
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")
