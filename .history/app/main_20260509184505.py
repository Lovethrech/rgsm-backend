from fa
from fastapi.middleware.cors import CORSMiddleware
from .routers import events
from .services.simulation import RGSMSimulator
import uvicorn
import asyncio

app=FastAPI(
    title="RGSM - RFID Geofence Security Model",
    description= "A Real-Time RFID-Based Genfence Security Model for University Campuses."
                "This system simulates student movement across campus zones using RFID readers,"
                "processes events in real-time, and applies security rules to detect unauthorized access.",
    version="1.0.0",
    contact={
        "name": "Olaonipekun Dolapo Rachael",
        "email": "rachealdolapo45@gmail.com
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(events.router, prefix='/api')

# Global simulator instance
simulator=RGSMSimulator()

@app.get('/')
async def root():
    return {
        "message" : "RGSM Backend is Running - Simulation Active ✅",
        "simulation_status": "Ready",
        "total_readers": len(simulator.readers),
        "total_zones": len(simulator.zones)
    }

@app.get("/start-simulation")
@app.post("/start-simulation")
async def start_simulation(num_students: int=1000, duration: int=3600):
    # Endpoint to start simulation from browser or Postman
    # Start the RGSM simulation with specified parameters
    asyncio.create_task(simulator.generate_events(num_students, duration))
    return {
        "status": "Simulation started",
        "num_students": num_students,
        "duration_seconds": duration,
        "message":"Check terminal for simulation logs and /api/events/stream for live events"
    }

if __name__=="__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
