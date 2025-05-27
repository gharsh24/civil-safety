from fastapi import APIRouter
import requests
import os
from models import ChatRequest

router = APIRouter()
KEY = os.getenv("MISTRAL_API_KEY")

@router.post("/ask")
async def ask_mistral(request: ChatRequest):
    query = request.query

    headers = {
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-small-2503",  
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a calm, empathetic disaster safety assistant. When someone is scared or in danger, "
                    "you comfort them and provide clear, step-by-step safety instructions. Be warm and supportive."
                    "Keep your answer short and consice in about 250 tokens only"
                    
                )
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "temperature": 0.7,
    
    }

    res = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload)
    print("Response text:", res.text)

    try:
        return {"answer": res.json()["choices"][0]["message"]["content"]}
    except KeyError:
        return {"error": "Unexpected response from Mistral", "details": res.text}
