# handlers/report.py
from fastapi import APIRouter, HTTPException
from db.supabase import create_supabase_client
from models import Incident
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_KEY=os.getenv("ADMIN_KEY")
router = APIRouter()
supabase = create_supabase_client()

@router.post("/report")
def report_incident(incident: Incident):
    try:
        # response = (supabase.table("incidents").insert({"user_id":int(incident.user_id),"location":incident.location,"description":incident.description}).execute())
        data = {
            "user_id": int(incident.user_id),
            "location": incident.location,
            "description": incident.description,
            "photo_url": incident.photo_url  
            }
        response = supabase.table("incidents").insert(data).execute()
        return {"status": "success", "data": response}
    except Exception as e:
        print("Exception ",e)
        return {"message":"Incident failed to report"}


@router.get("/get_all_incidents")
def get_all_incidents(key: str):
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid Admin key")

    try:
        response = supabase.table("incidents").select("*").execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        print("Exception while fetching incidents:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch incidents")