from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from ..core.database import get_db_connection

router=APIRouter()

# Pydantic Model for incoming events 
class RFIDEvent(BaseModel):
    timestamp: str
    reader_id: str
    student_uid: str
    zone: str

# Global variable to store latest events for real-time display
latest_events=[]

@router.post("/events")
async def receive_event(event: RFIDEvent):
    # Receive RFID events from simulation and process them 
    try:
        access_status= await apply_security_rules(event)

        # Svae to database
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute('''
            INSERT INTO event_logs
            (timestamp, reader_id, student_uid, zone, access_status, processed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp,
            event.reader_id,
            event.student_uid,
            event.zone,
            access_status,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()


        # Store event for real-time display
        event_dict=event.dict()
        event_dict["processed_at"]=datetime.now().isoformat()
        latest_events.append(event_dict)

        # Keep only last 100 events
        if len(latest_events)>100:
            latest_events.pop(0)

        # Process security rules
        await process_security_rules(event_dict)

        return{
            "status":"success",
            "message":"Event received and processed",
            "event": event_dict
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def process_security_rules(event: dict):
    # Apply JSON rules and trigger alerts if necessary
    restricted_zones=["Science_Labs_Zone", "Adenuga_Complex_Zone"]

    if event["zone"] in restricted_zones:
        alert_message=f"🚨 ALERT: Student {event['student_uid']} accessed restricted zone {event['zone']} at {event['timestamp']}"
        print(alert_message)
        # Later: Save to database + send to dashboard via sse