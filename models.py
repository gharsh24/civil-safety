from pydantic import BaseModel
from typing import Optional,List

class Incident(BaseModel):
    user_id: int
    # type: str
    location: str
    # lat: Optional[float] = None
    # lon: Optional[float] = None
    description: str
    photo_url: str 

class BroadcastRequest(BaseModel):
    # sender_chat_id: str
    alert_type:str # e.g. Heat Warning , Wind Adviosry , Thunderstorm
    location: str
    message: str
    admin_key:str

class HelpRequest(BaseModel):
    location: str  # e.g. "28.6139,77.2090"
    help_type: str  # e.g. "police station"

class ChatRequest(BaseModel):
    query: str

class QuizItem(BaseModel):
    question: str
    options: List[str]
    correct_option_index: int

class QuizItemList(BaseModel):
    items: List[QuizItem]