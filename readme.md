# 🚀 Getting Started

Follow the steps below to set up and run the project locally.

## ✅ Setup Instructions

For Creating virtual environment

```bash
python -m venv venv
 .\venv\Scripts\Activate.ps1
```

Now do all pip install if reqd and if some new package added do

```bash
pip freeze > requirements.txt
```

**0.** Create a `.env` file by copying from `.demoenv`.  
Ask **Harsh** for the actual credentials to fill in.

**1.** Install dependencies:

```bash
pip install -r requirements.txt
```

**2.** Start the development server:

```bash
uvicorn main:app --reload
```

**3.** Access the interactive API docs at: localhost:8000/docs

**4.** Run

```bash
python .\telegram-bot.py
```

to start the bot ( make sure api and bot are running inside venev and separate terminals to handle logs separately.)
Any commit made should include a clear and concise message summarizing:

The purpose of the changes and a brief overview of what was modified or added.
