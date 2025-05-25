from fastapi import APIRouter
from db.supabase import create_supabase_client

router = APIRouter()
supabase = create_supabase_client()

@router.get("/is-admin/{chat_id}")
def is_admin(chat_id: str):
    response = supabase.table("users").select("is_admin").eq("chat_id", chat_id).single().execute()
    if response.data:
        return {"is_admin": response.data["is_admin"]}
    return {"is_admin": False}
