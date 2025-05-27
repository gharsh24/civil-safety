from pydantic import BaseModel
from typing import Optional

class Incident(BaseModel):
    user_id: int
    # type: str
    location: str
    # lat: Optional[float] = None
    # lon: Optional[float] = None
    description: str

class BroadcastRequest(BaseModel):
    # sender_chat_id: str
    alert_type:str # e.g. Heat Warning , Wind Adviosry , Thunderstorm
    location: str
    message: str

class HelpRequest(BaseModel):
    location: str  # e.g. "28.6139,77.2090"
    help_type: str  # e.g. "police station"

class ChatRequest(BaseModel):
    query: str
