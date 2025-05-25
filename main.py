# main.py
from fastapi import FastAPI
from handlers import report, alerts, education, resources  # import all route modules

app = FastAPI()

app.include_router(report.router)
# app.include_router(alerts.router)
# app.include_router(education.router)
# app.include_router(resources.router)
