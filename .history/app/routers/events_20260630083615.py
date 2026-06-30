from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.event_processor import process_rfid_event

router = APIRouter(prefix="/events", tags=["RFID Events"])


class RFIDEventIn(BaseModel):
    reader_code: str = Field(..., examples=["R30_Male_Bronze_Main_Entrance"])
    tag_uid: str = Field(..., examples=["STU000001"])
    event_type: str = Field(default="scan", examples=["scan"])


@router.post("")
async def receive_event(event: RFIDEventIn):
    try:
        return process_rfid_event(event.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/health")
async def events_health():
    return {
        "status": "ok",
        "message": "RFID event processor is ready",
    }