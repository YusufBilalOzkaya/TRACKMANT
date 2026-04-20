from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime

class Tracker(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: str
    selector: str
    target_value: Optional[float] = None
    condition: str = "changes"  # "below", "above", "changes", "contains"
    target_text: Optional[str] = None
    last_value: Optional[str] = None
    is_active: bool = True
    check_interval_minutes: int = 60
    user_email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class History(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracker_id: int = Field(foreign_key="tracker.id")
    value: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NotificationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracker_id: int = Field(foreign_key="tracker.id")
    title: str
    message: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)

# Database setup
sqlite_file_name = "trackmant.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_db_and_tables()
