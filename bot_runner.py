# entrypoint.py
import threading
import os
import uvicorn
from main import app
from telegram_bot import main

def start_fastapi():
    port = int(os.environ.get("PORT", 8000))  # Render auto-sets this
    uvicorn.run(app, host="0.0.0.0", port=port)

def run_both():
    api_thread = threading.Thread(target=start_fastapi)
    api_thread.start()

    main()  # Blocking call for telegram bot

if __name__ == "__main__":
    run_both()
