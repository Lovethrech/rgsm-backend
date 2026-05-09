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

        return{
            "status":"success",
            "access_status": access_status,
            "message":"Event processed successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def apply_security_rules(event: RFIDEvent) -> str:
    conn=get_db_connection()
    cursor=conn.cursor()

    # Examples of JSON rules stored in database
    rules=[
        {
            "zone": "Science_Labs_Zone",
            "allowed_roles":["Student", "Lecturer", "Lab_Technician"],
            "allowed_hour": ["08:00", "18:00"],
            "action": "DENIED"
        },
        {
            "zone":"Postgraduate_Zone",
            "allowed_roles":["Pg_Student", "Lecturer", "Admin"],
            "allowed_hour": ["07:00", "18:00"],
            "action": "DENIED"
        },
        {
            "zone": "Female_Hostel_Zone",
            "allowed_roles":["Female_Student", "Admin"],
            "allowed_hour": ["06:00", "22:00"],
            "action": "DENIED"
        },
        {
            "zone": "Male_Hostel_Zone",
            "allowed_roles":["Male_Student", "Admin"],
            "allowed_hour": ["06:00", "22:00"],
            "action": "DENIED"
        }
    ]

    current_hour=datetime.now().strftime("%H:%M")

    for rule in rules:
        if event.zone == rule["zone"]:
            if event.zone==rule["zone"]:
                if current_time < rule["allowed_hour"]

    # Rule 1: Restricted Zone Access
    if event.zone in restricted_zones:
        return "DENIED - Restricted Zone"

    # Rule 2: Time-based restriction
    if current_hour>="19:00" or current_hour<="06:00":
        if "Hostel_Zone" not in event.zone:
            return "DENIED - Outside Allowed Hours"
    return "ALLOWED"