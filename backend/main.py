import asyncio
import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from models import engine, Tracker, History, NotificationLog, create_db_and_tables
from scraper import fetch_element_value, parse_numeric_value
from notifier import send_email_notification, generate_alert_body

# Settings management
SETTINGS_FILE = "settings.json"

def get_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"check_interval_minutes": 2}
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

scheduler = AsyncIOScheduler()

async def check_tracker_logic(tracker: Tracker, session: Session):
    print(f"Checking tracker: {tracker.name} ({tracker.url})")
    current_value = await fetch_element_value(tracker.url, tracker.selector)
    if current_value is None:
         print(f"Failed to fetch value for {tracker.name}")
         tracker.is_active = False # Mark as problematic if needed, or just log
         session.add(tracker)
         session.commit()
         return

    old_value = tracker.last_value
    tracker.last_value = current_value
    
    history = History(tracker_id=tracker.id, value=current_value)
    session.add(history)
    
    should_notify = False
    if tracker.condition == "changes" and old_value and old_value != current_value:
        should_notify = True
    elif tracker.condition in ["below", "above"]:
        cur_num = parse_numeric_value(current_value)
        target_num = tracker.target_value
        if cur_num is not None and target_num is not None:
            if tracker.condition == "below" and cur_num < target_num:
                should_notify = True
            elif tracker.condition == "above" and cur_num > target_num:
                should_notify = True
    elif tracker.condition == "contains" and tracker.target_text:
        if tracker.target_text.lower() in current_value.lower():
            if not old_value or tracker.target_text.lower() not in old_value.lower():
                should_notify = True

    if should_notify:
        print(f"NOTIFICATION TRIGGERED for {tracker.name}!")
        subject = f"Status Update: {tracker.name}"
        body = generate_alert_body(tracker.name, tracker.url, old_value or "N/A", current_value)
        send_email_notification(tracker.user_email, subject, body)
        log = NotificationLog(
            tracker_id=tracker.id, 
            title=subject, 
            message=f"Value changed from {old_value} to {current_value}"
        )
        session.add(log)

    session.add(tracker)
    session.commit()

async def run_all_trackers():
    with Session(engine) as session:
        trackers = session.exec(select(Tracker).where(Tracker.is_active == True)).all()
        for tracker in trackers:
            await check_tracker_logic(tracker, session)
            await asyncio.sleep(2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    settings = get_settings()
    scheduler.add_job(run_all_trackers, 'interval', minutes=settings["check_interval_minutes"], id="main_tracker_job")
    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(title="TRACKMANT API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/settings")
def read_settings():
    return get_settings()

@app.post("/settings")
def update_settings(new_settings: dict):
    save_settings(new_settings)
    interval = new_settings.get("check_interval_minutes", 2)
    # Reschedule existing job
    scheduler.reschedule_job("main_tracker_job", trigger='interval', minutes=interval)
    print(f"Scheduler rescheduled to {interval} minutes.")
    return new_settings

@app.get("/trackers")
def list_trackers():
    with Session(engine) as session:
        return session.exec(select(Tracker)).all()

@app.post("/trackers")
def add_tracker(tracker: Tracker):
    with Session(engine) as session:
        session.add(tracker)
        session.commit()
        session.refresh(tracker)
        return tracker

@app.put("/trackers/{tracker_id}")
def update_tracker(tracker_id: int, updated_tracker: Tracker):
    with Session(engine) as session:
        db_tracker = session.get(Tracker, tracker_id)
        if not db_tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        
        # Update fields
        db_tracker.name = updated_tracker.name
        db_tracker.url = updated_tracker.url
        db_tracker.selector = updated_tracker.selector
        db_tracker.target_value = updated_tracker.target_value
        db_tracker.condition = updated_tracker.condition
        db_tracker.target_text = updated_tracker.target_text
        db_tracker.user_email = updated_tracker.user_email
        db_tracker.is_active = updated_tracker.is_active
        
        session.add(db_tracker)
        session.commit()
        session.refresh(db_tracker)
        return db_tracker

@app.delete("/trackers/{tracker_id}")
def delete_tracker(tracker_id: int):
    with Session(engine) as session:
        tracker = session.get(Tracker, tracker_id)
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        session.delete(tracker)
        session.commit()
        return {"status": "success", "message": "Tracker deleted"}

@app.get("/trackers/{tracker_id}/history")
def get_history(tracker_id: int):
    with Session(engine) as session:
        return session.exec(select(History).where(History.tracker_id == tracker_id).order_by(History.timestamp.desc())).all()

@app.post("/trackers/{tracker_id}/check")
async def trigger_check(tracker_id: int):
    with Session(engine) as session:
        tracker = session.get(Tracker, tracker_id)
        if not tracker:
            raise HTTPException(status_code=404, detail="Tracker not found")
        await check_tracker_logic(tracker, session)
        return {"status": "success", "new_value": tracker.last_value}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
