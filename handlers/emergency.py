from fastapi import APIRouter, HTTPException
from db.supabase import create_supabase_client
from models import BroadcastRequest
from datetime import datetime
# import requests
import os
from telegram import Bot
from telegram.error import TelegramError

router = APIRouter()
supabase = create_supabase_client()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram bot token
bot = Bot(token=BOT_TOKEN)



@router.post("/broadcast-alert") 
async def broadcast_alert(data: BroadcastRequest):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    msg = (
        f"🚨 *{data.alert_type}*\n\n"
        f"📍 Location: {data.location}\n"
        f"🕒 Time: {current_time}\n"
    )
    if data.message:
        msg += f"\n📝 Notes: {data.message}"

    # fetch all non-admin users
    users = supabase.table("users").select("chat_id").eq("is_admin", False).execute()
    print(users)

    # Collect all chat IDs
    chat_ids = [user["chat_id"] for user in users.data]
    photo_url = "https://img.freepik.com/free-vector/modern-emergency-word-concept-with-flat-design_23-2147935068.jpg?semt=ais_hybrid&w=740"

    # Neeraj's chat ID for testing
    # my_chat_id =1441076235
    # chat_ids.append(my_chat_id)

    for chat_id in chat_ids:
        try:
            await bot.send_photo(chat_id=chat_id, photo=photo_url)
            print(f"Sending to {chat_id}: {msg}")
            await bot.send_message(chat_id=chat_id, text=msg,parse_mode="Markdown")
        except Exception as e:
            print(f"❌ Failed to send to {chat_id}: {e}")

    return {"status": "success", "sent_to": len(chat_ids)}




async def send_telegram_alert(alert_type, location, message, chat_ids):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = (
        f"🚨 *{alert_type}*\n\n"
        f"📍 Location: {location}\n"
        f"🕒 Time: {current_time}\n"
    )
    if message:
        msg += f"\n📝 Notes: {message}"

    # my_chat_id =1441076235 #Neeraj id for test
    # chat_ids.append(my_chat_id)
    photo_url = "https://img.freepik.com/free-vector/modern-emergency-word-concept-with-flat-design_23-2147935068.jpg?semt=ais_hybrid&w=740"

    for chat_id in chat_ids:
        try:
            await bot.send_photo(chat_id=chat_id, photo=photo_url)
            await bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
        except Exception as e:
            print(f"❌ Failed to send to {chat_id}: {e}")