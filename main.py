# main.py
from fastapi import FastAPI
from handlers import report, alerts, education, resources  # import all route modules

app = FastAPI()

app.include_router(report.router)
app.include_router(alerts.router,prefix="/alerts")

@app.on_event("startup")
async def startup_event():
    import asyncio
    asyncio.create_task(alerts.poll_weather())

# app.include_router(education.router)
# app.include_router(resources.router)
