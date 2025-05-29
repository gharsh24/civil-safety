from fastapi import APIRouter
import requests
import os
import json
import re
from datetime import datetime
from typing import List
from models import QuizItem, QuizItemList

router = APIRouter()
KEY = os.getenv("MISTRAL_API_KEY")
CACHE_FILE = "quiz_cache.json"

PROMPT = """
Generate 10 multiple-choice quiz questions in JSON format for a Safety Hackathon Quiz. Each question should focus on public safety, in events of emergency what to do, good practices in emergency , how to be vigilant and be good citizen in difficult situations . For each item, provide:

question: A clear, relevant question

options: List of 4 answer choices (strings)

correct_option_index: Integer (0-3), the index of the correct answer

Respond only with a JSON array of objects like:
[
  {
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correct_option_index": 2
  }
]
"""

def load_cached_quiz() -> List[QuizItem] | None:
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE, "r") as f:
        data = json.load(f)

    if data["date"] == str(datetime.utcnow().date()):
        return data["items"]
    return None

def save_cached_quiz(quiz_items: List[dict]):
    with open(CACHE_FILE, "w") as f:
        json.dump({"date": str(datetime.utcnow().date()), "items": quiz_items}, f)

@router.post("/generate-quiz", response_model=QuizItemList)
async def generate_quiz():
    cached_items = load_cached_quiz()
    if cached_items:
        return {"items": cached_items}

    headers = {
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": PROMPT}],
        "temperature": 0.7
    }

    response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=body)
    content = response.json()["choices"][0]["message"]["content"]

    try:
        # Remove ```json ... ``` if present
        cleaned = re.sub(r"^```(?:json)?\n|\n```$", "", content.strip())
        parsed = json.loads(cleaned)

        # Validate items using Pydantic
        validated = [QuizItem(**item).dict() for item in parsed]
        save_cached_quiz(validated)
        return {"items": validated}
    except Exception as e:
        return {"items": []}  # Or raise HTTPException if you want to indicate error
