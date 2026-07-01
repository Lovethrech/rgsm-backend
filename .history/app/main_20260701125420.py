import asyncio
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import events
from app.routers import simulation
from app.services.simulation import RGSMSimulator

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = FastAPI(
    title="RGSM - RFID Geofence Security Model",
    description=(
        "A real-time RFID-based geofence security model for university campuses. "
        "The backend simulates RFID reader events, processes geofence rules, "
        "stores decisions in Supabase PostgreSQL, and powers a live Nuxt dashboard."
    ),
    version="1.0.0",
    contact={
        "name": "Olaonipekun Dolapo Rachael",
        "email": "rachealdolapo45@gmail.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://chel-rgsm.netlify.app",
        FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api")
app.include_router(simulation.router, prefix="/api")

simulator = RGSMSimulator()


@app.get("/")
async def root():
    return {
        "message": "RGSM Backend is running",
        "simulation_status": "ready",
        "total_readers": len(simulator.readers),
    }


@app.post("/start-simulation")
@app.get("/start-simulation")
async def start_simulation(num_students: int = 100, duration: int = 300):
    asyncio.create_task(simulator.generate_events(num_students, duration))

    return {
        "status": "simulation_started",
        "num_students": num_students,
        "duration_seconds": duration,
        "message": "Simulation is sending RFID events to Supabase through FastAPI.",
    }

@app.post("/api/simulation/start")
async def start_simulation(num_students: int = 20, duration: int = 120):
    asyncio.create_task(simulator.generate_events(num_students, duration))

    return {
        "status": "simulation_started",
        "num_students": num_students,
        "duration_seconds": duration
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
    )