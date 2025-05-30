# Civil Safety - Telegram Safety Bot 🚨

Welcome to **Civil Safety**, a Telegram bot designed to enhance citizen safety during emergencies. Built as part of a hackathon, this bot provides real-time assistance, emergency resource locating, incident reporting, and safety education through an accessible and user-friendly platform.

## 📖 Overview

Civil Safety leverages Telegram's global reach and cross-platform compatibility to deliver critical safety features to users worldwide. Whether it's finding the nearest hospital, reporting an incident, or getting AI-powered emergency advice, this bot aims to be a lifeline in times of need.

### Key Features

- **/find**: Locate nearby emergency resources (police, hospitals, fire stations) based on user location, with country-specific emergency contacts.
- **/incident**: Report incidents with descriptions, locations, and images for community safety monitoring.
- **/ask**: Get real-time AI advice on emergency situations or safety queries.
- **/quiz**: Engage in daily interactive quizzes on safety tips and best practices.
- **Admin Tools**: Send emergency alerts, view incident reports via a dashboard, and automate weather warnings using OpenWeather API.

## 🚀 Getting Started

Follow the steps below to set up and run the project locally.

### ✅ Setup Instructions

#### Creating a Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Now, install required packages. If a new package is added, update the requirements file:

```bash
pip freeze > requirements.txt
```

#### Steps to Run the Project

0. **Create a `.env` file** by copying from `.demoenv`. Ask **Harsh** for the actual credentials to fill in.
1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Start the development server**:

```bash
uvicorn main:app --reload
```

3. **Access the interactive API docs** at: `localhost:8000/docs`
4. **Run the Telegram bot**:

```bash
python ./telegram-bot.py
```

**Note**: Ensure the API and bot are running inside the virtual environment in separate terminals to handle logs separately.

#### Commit Guidelines

Any commit made should include a clear and concise message summarizing:

- The purpose of the changes.
- A brief overview of what was modified or added.

## 🛠️ Technologies Used

- **Python**: Core programming language for bot and API development.
- **Telegram Bot API**: For bot interactions and user interface.
- **FastAPI/Uvicorn**: Backend server for handling API requests.
- **OpenWeather API**: For real-time weather data and automated alerts.

## 🤝 Contributing

We welcome contributions to improve Civil Safety! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Submit a pull request for review.
