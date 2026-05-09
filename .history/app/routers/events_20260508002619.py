from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
from ..core.database import get_db_connection
import asyncio

router=APIRouter()

