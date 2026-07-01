import asyncio

from fastapi import APIRouter, Query

from app.services.simulation import RGSMSimulator

router = APIRouter(prefix="/simulation", tags=["Simulation"])

simulator = RGSMSimulator()


@router.post("/start")
async def start_simulation(
    num_students: int = Query(default=20, ge=1, le=200),
    duration: int = Query(default=120, ge=10, le=3600),
    scenario: str = Query(default="mixed"),
):
    if simulator.is_running:
        return {
            "status": "already_running",
            "message": "Simulation is already running.",
        }

    asyncio.create_task(
        simulator.generate_events(
            num_students=num_students,
            duration=duration,
            scenario=scenario,
        )
    )

    return {
        "status": "simulation_started",
        "num_students": num_students,
        "duration_seconds": duration,
        "scenario": scenario,
    }


@router.post("/stop")
async def stop_simulation():
    simulator.stop()

    return {
        "status": "simulation_stopped",
        "message": "Simulation stop signal sent.",
    }


@router.get("/status")
async def simulation_status():
    return {
        "is_running": simulator.is_running,
        "available_scenarios": [
            "mixed",
            "normal",
            "violations",
            "hostel",
            "restricted",
            "unknown",
        ],
    }