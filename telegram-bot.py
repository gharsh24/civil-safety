from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import os
from db.supabase import create_supabase_client
from telegram import Update , Poll
from telegram.ext import Updater, CommandHandler
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)
from dotenv import load_dotenv
import requests
import httpx
import json
import random

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
REPORT_API_ENDPOINT = "http://localhost:8000/report"  # FastAPI POST /report
HELP_API_ENDPOINT = "http://localhost:8000/find-help"  # FastAPI POST /report
EMERGENCY_CONTACTS_API = "http://localhost:8000/emergency-contacts" # its a get
ASK_API_ENDPOINT = "http://localhost:8000/ask"  # FastAPI POST /ask mistral ai endpoint use carefully not to exploit api limits
QUIZ_FILE="quiz_cache.json"
LOCATION, DESCRIPTION = range(2)
PHOTO =2
ASK_QUESTION = 5 
QUIZ_QUESTION=10
QUIZ_ANSWER=11 
FIND_LOCATION, HELP_TYPE = range(2, 4)  # Continue from previous states
HELP_TYPE_MAP = {
    "1": "police",
    "2": "hospitals",
    "3": "fire stations"
}


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
    context.user_data["description"] = description
    await update.message.reply_text("📸 Please send a photo of the incident.")
    return PHOTO

#receive photo
async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    supabase = create_supabase_client()
    if not update.message.photo:
        await update.message.reply_text(" No photo found. Please send a photo.")
        return PHOTO
    photo = update.message.photo[-1]  # get the best quality photo
    photo_file = await photo.get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    file_path = f"incident_photos/{update.effective_user.id}_{photo.file_unique_id}.jpg"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(photo_bytes)

    supabase.storage.from_("incident-images").upload(file_path, file_path, {"content-type": "image/jpeg"})

    # Get public URL
    photo_url = supabase.storage.from_("incident-images").get_public_url(file_path)

    # Store incident report in Supabase
    data = {
        "user_id": update.effective_user.id,
        "location": context.user_data["location"],
        "description": context.user_data["description"],
        "photo_url": photo_url
    }
    print(data)

    try:
        res = requests.post(REPORT_API_ENDPOINT, json=data)
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
    "🔍 What kind of help do you need?\n"
    "Type the number:\n"
    "1 - Police\n"
    "2 - Hospitals\n"
    "3 - Fire stations"
)
    return HELP_TYPE

# Handle help type selection
async def receive_help_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # help_type = update.message.text.lower()
    location = context.user_data["find_location"]

    # if help_type not in ["police", "hospitals", "fire stations"]:
    #     await update.message.reply_text("❌ Please choose one of: police , hospitals, fire stations")
    #     return HELP_TYPE
    help_type_input = update.message.text.strip()
    help_type = HELP_TYPE_MAP.get(help_type_input)

    if not help_type:
        await update.message.reply_text("❌ Please type 1, 2, or 3 to select the help type.")
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
            
            # Call emergency contacts API
            lat, lon = map(float, location.split(","))
            emer_response = await client.get(
                EMERGENCY_CONTACTS_API,
                params={"lat": lat, "lon": lon}
            )
            emer_response.raise_for_status()
            emer_data = emer_response.json()

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
         # Emergency contacts formatting
        contacts = emer_data.get("emergency_contacts", {})
        country = emer_data.get("country", "Unknown")

        emergency_text = f"\n🚨 Emergency Numbers in {country}:\n"
        if contacts.get("police"):
            emergency_text += f"👮 Police: {', '.join(contacts['police'])}\n"
        if contacts.get("ambulance"):
            emergency_text += f"🚑 Ambulance: {', '.join(contacts['ambulance'])}\n"
        if contacts.get("dispatch"):
            emergency_text += f"📞 Dispatch: {', '.join(contacts['dispatch'])}\n"
        if not any([contacts.get("police"), contacts.get("ambulance"), contacts.get("dispatch")]):
            emergency_text += "No emergency contacts found.\n"

        response_text += emergency_text

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



# /ask command entry — bot asks user to type question
async def ask_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬 Please type your safety question:")
    return ASK_QUESTION

# Receive user question, call API and reply
async def ask_receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text

    payload = {"query": query}
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(ASK_API_ENDPOINT, json=payload)
            res.raise_for_status()
            data = res.json()
            answer = data.get("answer", "❌ No response received.")
            await update.message.reply_text(f"🤖\n  {answer}",parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error fetching reply: {str(e)}")

    return ConversationHandler.END

def load_questions():
    with open(QUIZ_FILE, "r") as f:
        data = json.load(f)
    # Extract the list of questions from "items" key
    questions = data.get("items", [])
    return questions


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = load_questions()
    if not questions:
        await update.message.reply_text("No quiz questions available.")
        return ConversationHandler.END

    context.user_data['quiz_questions'] = questions
    context.user_data['quiz_index'] = 0
    context.user_data['score'] = 0

    question_data = questions[0]
    question_text = question_data["question"]
    options = question_data["options"]
    options_text = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))

    await update.message.reply_text(f"\n\n {question_text}\n\nOptions:\n{options_text}\n\nPlease type the number of your answer.")

    return QUIZ_ANSWER

async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip()

    if not user_answer.isdigit():
        await update.message.reply_text("Please reply with a valid option number.")
        return QUIZ_ANSWER

    user_answer = int(user_answer) - 1  # zero-based index
    questions = context.user_data['quiz_questions']
    index = context.user_data['quiz_index']
    current_question = questions[index]

    correct_index = current_question['correct_option_index']

    if user_answer == correct_index:
        context.user_data['score'] += 1
        await update.message.reply_text("✅ Correct!")
    else:
        correct_answer = current_question['options'][correct_index]
        await update.message.reply_text(f"❌ Wrong!\n The correct answer was: {correct_answer}")

    # Move to next question
    context.user_data['quiz_index'] += 1
    if context.user_data['quiz_index'] >= len(questions):
        # Quiz finished
        score = context.user_data['score']
        total = len(questions)
        await update.message.reply_text(f"🏁 Quiz completed! Your score: {score}/{total}")
        return ConversationHandler.END
    else:
        # Send next question
        next_question = questions[context.user_data['quiz_index']]
        question_text = next_question["question"]
        options = next_question["options"]
        options_text = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))

        await update.message.reply_text(f"{question_text}\n\nOptions:\n{options_text}\n\nPlease type the number of your answer.")
        return QUIZ_ANSWER

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
            PHOTO: [MessageHandler(filters.PHOTO, receive_photo)],
            
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
    
    ask_conv = ConversationHandler(
    entry_points=[CommandHandler("ask", ask_start)],
    states={
        ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_receive_question)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

    app.add_handler(ask_conv)

    quiz_conv = ConversationHandler(
        entry_points=[CommandHandler("quiz", start_quiz)],
        states={
            QUIZ_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(quiz_conv)



    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
