import simpy
import random
from datetime import datetime
from typing import Dict, List
import asyncio
import requests

class RGSMSimulator: 
    def __init__(self):
        self.readers=[
            # Main Entrance & Central Areas
            "R1_Main_University_Gate",
            "R2_Friendship_Center_Main_Entrance",
            
            # Postgraduate & COLNAS
            "R3_Postgraduate_Building_Main_Entrance",
            "R4_COLNAS_Dept_Building_Main_Entrance",
            "R5_COLNAS_Computer_Science_Section_Entrance",
            
            # Lecture Classrooms
            "R6_Lecture_Classroom_1",
            "R7_Lecture_Classroom_2",
            "R8_Lecture_Classroom_3",
            "R9_Lecture_Classroom_4",
            "R10_Lecture_Classroom_5",
            "R11_Lecture_Classroom_6",
            
            # Labs & Specialized Buildings
            "R12_ELT_Entrance",
            "R13_Old_Software_Lab_Entrance",
            "R14_New_Software_Lab_Entrance",
            "R15_Physics_Lab_1",
            "R16_Physics_Lab_2",
            "R17_Physics_Lab_3",
            "R18_Chemistry_Lab_1",
            "R19_Chemistry_Lab_2",
            "R20_Chemistry_Lab_3",
            "R21_Biology_Lab_1",
            "R22_Biology_Lab_2",
            "R23_Biology_Lab_3",
            
            # Adenuga Complex
            "R24_Adenuga_Main_Entrance",
            "R25_Adenuga_Hardware_Lab",
            "R26_Adenuga_Library",
            "R27_Adenuga_ICT_Center",
            
            # Hostels (Residential Zone)
            "R28_Female_Silver_Hostel_Main_Entrance",
            "R29_Male_Silver_1_Main_Entrance",
            "R30_Male_Bronze_Main_Entrance",
            "R31_Male_Silver_2_Main_Entrance",
            "R32_Male_Silver_3_Main_Entrance",
            "R33_Female_Emerald_1_Main_Entrance",
            "R34_Female_Emerald_2_Main_Entrance",
            "R35_Female_New_Hall_Main_Entrance"
        ]
        self.zones: Dict[str, List[str]]={
            "Main_Campus_Entrance_Zone": [
                "R1_Main_University_Gate", 
                "R2_Friendship_Center_Main_Entrance"
            ],
            
            "Postgraduate_Zone": [
                "R3_Postgraduate_Building_Main_Entrance"
            ],
            
            "COLNAS_Academic_Zone": [
                "R4_COLNAS_Dept_Building_Main_Entrance",
                "R5_COLNAS_Computer_Science_Section_Entrance"
            ],
            
            "Lecture_Halls_Zone": [
                "R6_Lecture_Classroom_1", "R7_Lecture_Classroom_2", "R8_Lecture_Classroom_3",
                "R9_Lecture_Classroom_4", "R10_Lecture_Classroom_5", "R11_Lecture_Classroom_6"
            ],
            
            "Science_Labs_Zone": [
                "R12_ELT_Entrance", "R13_Old_Software_Lab_Entrance", "R14_New_Software_Lab_Entrance",
                "R15_Physics_Lab_1", "R16_Physics_Lab_2", "R17_Physics_Lab_3",
                "R18_Chemistry_Lab_1", "R19_Chemistry_Lab_2", "R20_Chemistry_Lab_3",
                "R21_Biology_Lab_1", "R22_Biology_Lab_2", "R23_Biology_Lab_3"
            ],
            
            "Adenuga_Complex_Zone": [
                "R24_Adenuga_Main_Entrance", "R25_Adenuga_Hardware_Lab",
                "R26_Adenuga_Library", "R27_Adenuga_ICT_Center"
            ],
            
            "Female_Hostel_Zone": [
                "R28_Female_Silver_Hostel_Main_Entrance",
                "R33_Female_Emerald_1_Main_Entrance",
                "R34_Female_Emerald_2_Main_Entrance",
                "R35_Female_New_Hall_Main_Entrance"
            ],
            
            "Male_Hostel_Zone": [
                "R29_Male_Silver_1_Main_Entrance",
                "R30_Male_Bronze_Main_Entrance",
                "R31_Male_Silver_2_Main_Entrance",
                "R32_Male_Silver_3_Main_Entrance"
            ]
        }
    def get_zone_from_reader(self, reader_id:str) -> str:
        # Return a zone a reader belongs to 
        for zone_name,readers in self.zones.items():
            if reader_id in readers:
                return zone_name
        return "General_Campus_Area"

async def generate_events(self, num_students: int=1000, duration: int=3600):
    """Simulate student movement and send events to backend"""
    env=simpy.Environment()

    for student_id in range(num_students):
        env.process(self.student_movement(env, student_id))

    print(f"🚀 Starting RGSM Simualtion with {num_students} students for {duration} seconds...")
    env.run(until=duration)
    print(f"✅Simulation completed successfully!")

def student_movement(self, env, student_id):
    while True:
        reader_id=random.choice(self.readers)
        timestamp=datetime.now().isoformat()

        event={
            "timestamp": timestamp,
            "reader_id": reader_id,
            "student_uid" : f"STU{student_id:06d}",
            "zone":self.get_zone_from_reader(reader_id)
        }
    # Send to FASTAPI endpoint
    asyncio.create_task(self.send_event(event))

    # Student moves every 15-120 seconds
    yield env.timeout(random.uniform(15,120)) 

async def send_event(self, event: dict):
    """Send event to the FastAPI endpoint"""
    try:
        async with asyncio.timeout(5):  # Prevent hanging
            response = await asyncio.get_running_loop().run_in_executor(
                None, 
                lambda: requests.post(
                    "http://127.0.0.1:8000/api/events", 
                    json=event, 
                    timeout=3
                )
            )
            if response.status_code != 200:
                print(f"⚠️ Failed to send event: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Event send failed: {e}")