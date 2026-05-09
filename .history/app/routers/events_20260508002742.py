from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
from ..core.database import get_db_connection
import asyncio

router=APIRouter()

# Pydantic Model for incoming events 
class RFIDEvent(BaseModel):
    timestamp: str
    reader_id: str
    student_uid: str
    zone: str

# Global variable to store latest events for real-time display
latest_events