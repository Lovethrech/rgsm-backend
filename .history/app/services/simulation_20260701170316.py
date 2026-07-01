import asyncio
import random
from datetime import datetime

from app.services.event_processor import process_rfid_event
import simpy


class RGSMSimulator:
    def __init__(self):
        self.is_running = False

        self.normal_readers = [
            "R1_Main_University_Gate",
            "R3_COLNAS_Entrance",
            "R4_Computer_Science_Entrance",
            "R7_Adenuga_Library",
            "R8_Lecture_Hall_1",
            "R9_Lecture_Hall_2",
        ]

        self.hostel_readers = [
            "R30_Male_Bronze_Main_Entrance",
            "R31_Female_Silver_Main_Entrance",
            "R32_Male_Silver_Main_Entrance",
            "R33_Female_Emerald_Main_Entrance",
        ]

        self.restricted_readers = [
            "R2_Admin_Block_Entrance",
            "R5_Old_Software_Lab",
            "R6_New_Software_Lab",
            "R10_Server_Room",
        ]

        self.valid_tags = [
            "STU000001",
            "STU000002",
            "STU000003",
            "STU000004",
            "STU000005",
            "STU000006",
            "STU000007",
            "STU000008",
            "STU000009",
            "STU000010",
        ]

        self.unknown_tags = [
            "UNKNOWN_TAG_001",
            "UNKNOWN_TAG_002",
            "VISITOR_TAG_001",
            "CLONED_CARD_001",
        ]

    async def generate_events(
        self,
        num_students: int = 20,
        duration: int = 120,
        scenario: str = "mixed",
    ):
        if self.is_running:
            return

        self.is_running = True

        env = simpy.Environment()

        for student_index in range(num_students):
            env.process(self.student_movement(env, student_index, scenario))

        print(
            f"Starting RGSM simulation: scenario={scenario}, "
            f"students={num_students}, duration={duration}s"
        )

        env.run(until=duration)

        self.is_running = False
        print("RGSM simulation completed.")

    def student_movement(self, env, student_index: int, scenario: str):
        while self.is_running:
            event = self.generate_scenario_event(student_index, scenario)
            asyncio.create_task(self.send_event(event))

            delay = random.uniform(2, 8)
            yield env.timeout(delay)

    def generate_scenario_event(self, student_index: int, scenario: str) -> dict:
        tag_uid = self.valid_tags[student_index % len(self.valid_tags)]

        if scenario == "normal":
            reader_code = random.choice(self.normal_readers + self.hostel_readers)

        elif scenario == "violations":
            reader_code = random.choice(self.restricted_readers + self.hostel_readers)

            if random.random() < 0.25:
                tag_uid = random.choice(self.unknown_tags)

        elif scenario == "hostel":
            reader_code = random.choice(self.hostel_readers)

        elif scenario == "restricted":
            reader_code = random.choice(self.restricted_readers)

        elif scenario == "unknown":
            reader_code = random.choice(self.normal_readers + self.hostel_readers)
            tag_uid = random.choice(self.unknown_tags)

        else:
            event_type_roll = random.random()

            if event_type_roll < 0.55:
                reader_code = random.choice(self.normal_readers)
            elif event_type_roll < 0.78:
                reader_code = random.choice(self.hostel_readers)
            elif event_type_roll < 0.93:
                reader_code = random.choice(self.restricted_readers)
            else:
                reader_code = random.choice(self.normal_readers + self.hostel_readers)
                tag_uid = random.choice(self.unknown_tags)

        return {
            "reader_code": reader_code,
            "tag_uid": tag_uid,
            "event_type": random.choice(["scan", "enter", "exit"]),
            "scenario": scenario,
            "simulated_at": datetime.now().isoformat(),
        }

    async def send_event(self, event: dict):
        try:
            await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: process_rfid_event(event),
            )
        except Exception as exc:
            print(f"Event processing failed: {exc}")

    def stop(self):
        self.is_running = False