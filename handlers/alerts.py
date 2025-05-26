from fastapi import APIRouter
import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from .emergency import send_telegram_alert
from db.supabase import create_supabase_client


load_dotenv()

API_KEY = os.getenv("OPEN_WEATHER_KEY")

router = APIRouter()
supabase = create_supabase_client()

LAT, LON = 39.7684, -86.1581 # Indy ke fix coordinates


# All below ones are from References:
# [NWS Indianapolis Criteria and Definitions]
# [NWS Thunderstorm Safety]
# [NWS Wind Safety]
# [NWS Severe Weather Warning Criteria
#[Indiana Extreme Heat Guidelines]


HEAT_ADVISORY = 40.6
HEAT_WARNING = 43.3
WIND_ADVISORY = 13.4
WIND_WARNING = 17.9
WIND_GUST_WARNING = 25.9

async def check_emergency(data):
    emergencies = []
    #emergencies.append("Heat Warning")
    
    main = data.get("main", {})
    wind = data.get("wind", {})
    weather = data.get("weather", [{}])[0]

    feels_like_c = main.get("feels_like", 0) - 273.15
    wind_speed = wind.get("speed", 0)
    wind_gust = wind.get("gust", 0)
    weather_id = weather.get("id", 0)

    if feels_like_c >= HEAT_WARNING:
        emergencies.append("Heat Warning")
    elif feels_like_c >= HEAT_ADVISORY:
        emergencies.append("Heat Advisory")

    if wind_speed >= WIND_WARNING or wind_gust >= WIND_GUST_WARNING:
        emergencies.append("Wind Warning")
    elif wind_speed >= WIND_ADVISORY:
        emergencies.append("Wind Advisory")

    if 200 <= weather_id <= 232:
        emergencies.append("Thunderstorm Warning")

    return emergencies


async def fetch_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to fetch weather: {response.status}")
                return {}

async def send_alert(emergencies):
    alert_type=" , ".join(emergencies)
    location="Indianpolis, IN"
    message="Automatically detected from weather services"

    #fetch users from db
    users=supabase.table("users").select("chat_id").eq("is_admin",False).execute()
    chat_ids=[user["chat_id"] for user in users.data]

    await send_telegram_alert(alert_type,location,message,chat_ids)
    # Add tele notification logic here

async def poll_weather(): #Check every 2 min for weather updates and if emergency found report it to tele
    while True:
        try:
            data = await fetch_weather()
            if data:
                print("Fetched weather data:", data)
                emergencies = await check_emergency(data)
                if emergencies:
                    await send_alert(emergencies)
        except Exception as e:
            print("Polling error:", e)
        await asyncio.sleep(6000)  # Wait 2 min(120) maybe change later as per demands currenly i am setting large no to prevent reduncdant checks and save bankrupcy by api calls



@router.get("/")
async def home():
    return {"status": "Weather emergency checker running"}

@router.get("/current-weather")
async def current_weather():
    data = await fetch_weather()
    if data:
        return {"status": "success", "data": data}
    else:
        return {"status": "error", "message": "Failed to fetch weather data"}
