from fastapi import APIRouter, HTTPException
from db.supabase import create_supabase_client
from models import BroadcastRequest
# import requests
import os
from telegram import Bot
from telegram.error import TelegramError

router = APIRouter()
supabase = create_supabase_client()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram bot token
bot = Bot(token=BOT_TOKEN)


@router.post("/broadcast-alert")
def broadcast_alert(data: BroadcastRequest):

    # fetch all non-admin users
    users = supabase.table("users").select("chat_id").eq("is_admin", False).execute()
    print(users)
    
    for user in users.data:
        try:
            print(user["chat_id"], data.message)
            bot.send_message(chat_id=user["chat_id"], text=data.message)
        except Exception as e:
            print(f"❌ Failed to send to {user['chat_id']}: {e}")

    return {"status": "success", "sent_to": len(users.data)}

