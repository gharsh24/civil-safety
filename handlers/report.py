# handlers/report.py
from fastapi import APIRouter, HTTPException
from db.supabase import create_supabase_client
from models import Incident


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
