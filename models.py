from pydantic import BaseModel
from typing import Optional

class Incident(BaseModel):
    user_id: str
    # type: str
    location: str
    # lat: Optional[float] = None
    # lon: Optional[float] = None
    description: str

class BroadcastRequest(BaseModel):
    # sender_chat_id: str
    message: str