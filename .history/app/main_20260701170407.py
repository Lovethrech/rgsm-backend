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
    total_readers = (
        len(simulator.normal_readers)
        + len(simulator.hostel_readers)
        + len(simulator.restricted_readers)
    )

    return {
        "message": "RGSM - RFID Geofence Security Model API is running",
        "status": "ok",
        "total_simulation_readers": total_readers,
        "available_endpoints": {
            "events_health": "/api/events/health",
            "simulation_status": "/api/simulation/status",
            "start_simulation": "/api/simulation/start",
            "stop_simulation": "/api/simulation/stop",
        },
    }



if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
    )