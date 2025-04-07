from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DB_NAME
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import pytz

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]
chat_collection = db.get_collection("chats")

class Chat(BaseModel):
    user_email: str
    prompt: str
    response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(pytz.utc))  # Use pytz.utc