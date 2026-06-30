import asyncio
import random
from datetime import datetime

import requests
import simpy


class RGSMSimulator:
    def __init__(self):
        self.readers = [
            "R1_Main_University_Gate",
            "R2_Friendship_Center_Main_Entrance",
            "R3_Postgraduate_Building_Main_Entrance",
            "R4_COLNAS_Dept_Building_Main_Entrance",
            "R5_COLNAS_Computer_Science_Section_Entrance",
            "R6_Lecture_Classroom_1",
            "R7_Lecture_Classroom_2",
            "R8_Lecture_Classroom_3",
            "R9_Lecture_Classroom_4",
            "R10_Lecture_Classroom_5",
            "R11_Lecture_Classroom_6",
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
            "R24_Adenuga_Main_Entrance",
            "R25_Adenuga_Hardware_Lab",
            "R26_Adenuga_Library",
            "R27_Adenuga_ICT_Center",
            "R28_Female_Silver_Hostel_Main_Entrance",
            "R29_Male_Silver_1_Main_Entrance",
            "R30_Male_Bronze_Main_Entrance",
            "R31_Male_Silver_2_Main_Entrance",
            "R32_Male_Silver_3_Main_Entrance",
            "R33_Female_Emerald_1_Main_Entrance",
            "R34_Female_Emerald_2_Main_Entrance",
            "R35_Female_New_Hall_Main_Entrance",
        ]

    async def generate_events(self, num_students: int = 100, duration: int = 300):
        env = simpy.Environment()

        for student_id in range(num_students):
            env.process(self.student_movement(env, student_id))

        print(
            f"Starting RGSM simulation with {num_students} students "
            f"for {duration} simulated seconds..."
        )

        env.run(until=duration)

        print("Simulation completed successfully.")

    def student_movement(self, env, student_id: int):
        while True:
            reader_code = random.choice(self.readers)

            event = {
                "reader_code": reader_code,
                "tag_uid": f"STU{student_id:06d}",
                "event_type": random.choice(["scan", "enter", "exit"]),
                "simulated_at": datetime.now().isoformat(),
            }

            asyncio.create_task(self.send_event(event))

            yield env.timeout(random.uniform(5, 25))

    async def send_event(self, event: dict):
        try:
            response = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: requests.post(
                    "http://127.0.0.1:8000/api/events",
                    json=event,
                    timeout=5,
                ),
            )

            if response.status_code not in [200, 201]:
                print(f"Failed to send event: {response.status_code} {response.text}")

        except Exception as exc:
            print(f"Event send failed: {exc}")