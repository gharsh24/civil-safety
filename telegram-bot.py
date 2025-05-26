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
import httpx

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
REPORT_API_ENDPOINT = "http://localhost:8000/report"  # FastAPI POST /report
HELP_API_ENDPOINT = "http://localhost:8000/find-help"  # FastAPI POST /report
LOCATION, DESCRIPTION = range(2)
FIND_LOCATION, HELP_TYPE = range(2, 4)  # Continue from previous states


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! to public safety bot. Click on Menu to see all active options.")

# Start incident report
async def start_incident(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📍 Please enter the location of the incident. Click 📎 , select Location and send current location")
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
        res = requests.post(REPORT_API_ENDPOINT, json=payload)
        if res.status_code == 200:
            await update.message.reply_text("✅ Incident reported successfully. Thanks for being a good responsible citizen 🏅")
        else:
            await update.message.reply_text("❌ Failed to report incident.")
    except Exception:
        await update.message.reply_text("❌ Error occurred while reporting.")

    return ConversationHandler.END


# Start /find conversation
async def start_find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📍 Please share your current location to find nearby help stations."
    )
    return FIND_LOCATION

# Handle location
async def receive_find_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.location:
        loc = update.message.location
        latitude = loc.latitude
        longitude = loc.longitude
        context.user_data["find_location"] = f"{latitude},{longitude}"
    else:
        context.user_data["find_location"] = update.message.text

    await update.message.reply_text(
        "🔍 What kind of help do you need?\nType one of: police , hospitals, fire stations"
    )
    return HELP_TYPE

# Handle help type selection
async def receive_help_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_type = update.message.text.lower()
    location = context.user_data["find_location"]

    if help_type not in ["police", "hospitals", "fire stations"]:
        await update.message.reply_text("❌ Please choose one of: police , hospitals, fire stations")
        return HELP_TYPE

    try:
        # Prepare API request data
        data = {
            "location": location,
            "help_type": help_type
        }

        print ("data sent", data)
        async with httpx.AsyncClient() as client:
            # Call your FastAPI endpoint
            response = await client.post(
                HELP_API_ENDPOINT,
                json=data
            )
            response.raise_for_status()
            results = response.json()

        print("response ",response)
        print("received list ", results)
        # Format the response
        if not results:
            await update.message.reply_text("🚨 No results found for the specified location")
            return ConversationHandler.END

        response_text = f"📍 Nearest {help_type} to {location}:\n\n"
        for index, item in enumerate(results, start=1):
            response_text += (
                f"{index}. {item['name']}\n"
                f"   Latitude: {item['latitude']}\n"
                f"   Longitude: {item['longitude']}\n\n"
            )

        await update.message.reply_text(response_text)

    except httpx.HTTPStatusError as e:
        await update.message.reply_text(f"⚠️ API Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ An error occurred: {str(e)}")

    return ConversationHandler.END


# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Ongoing action cancelled.")
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

    # Find help stations conversation
    find_conv = ConversationHandler(
        entry_points=[CommandHandler("find", start_find)],
        states={
            FIND_LOCATION: [MessageHandler(filters.LOCATION | (filters.TEXT & ~filters.COMMAND), receive_find_location)],
            HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_help_type)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(find_conv)


    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
