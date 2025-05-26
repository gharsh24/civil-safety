from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)
from dotenv import load_dotenv
import requests

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ENDPOINT = "http://localhost:8000/report"  # FastAPI POST /report
LOCATION, DESCRIPTION = range(2)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! to public safety bot. Click on Menu to see all active options.")

# Start incident report
async def start_incident(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📍 Please enter the location of the incident. Click 📎 , select Loation and send current location")
    return LOCATION

# Receive location
async def receive_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.location:
        # User sent a location object
        loc = update.message.location
        print("HERE")
        latitude = loc.latitude
        longitude = loc.longitude
        print(latitude,longitude)
        context.user_data["location"] = f"{latitude},{longitude}"
        await update.message.reply_text("📝 Enter a short description of the issue.")
        return DESCRIPTION
    else:
        # User sent text instead of location
        context.user_data["location"] = update.message.text
    await update.message.reply_text("📝 Now enter a short description of the issue.")
    return DESCRIPTION

# Receive description and send to FastAPI
async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    location = context.user_data["location"]
    user_id = update.effective_user.id
    payload = {
        "user_id": user_id,
        "location": location,
        "description": description,
    }

    try:
        res = requests.post(API_ENDPOINT, json=payload)
        if res.status_code == 200:
            await update.message.reply_text("✅ Incident reported successfully. Thanks for being a good responsible citizen 🏅")
        else:
            await update.message.reply_text("❌ Failed to report incident.")
    except Exception:
        await update.message.reply_text("❌ Error occurred while reporting.")

    return ConversationHandler.END

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Incident report cancelled.")
    return ConversationHandler.END

# Main bot runner
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start command
    app.add_handler(CommandHandler("start", start))

    # Incident reporting conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("incident", start_incident)],
        states={
            LOCATION: [MessageHandler(filters.LOCATION, receive_location)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
