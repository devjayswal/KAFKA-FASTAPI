
from pymongo import MongoClient
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
from datetime import datetime

class MessageSettings(BaseSettings):
    mongo_connection_string: str = "mongodb://localhost:27017"
    mongo_database_name: str = "eda"
    mongo_collection_name: str = "messages"

class MessageSchema(BaseModel):
    message: str = Field(..., min_length=1, max_length=250)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    