from fastapi import FASTAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import events
from .services.simulation import RGSM_Simulator
import uvicrorn

app=FASTAPI(title="RGSM - RFID Genfence Security Model| by Olaonipekun Dolapo Rachael")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(events.router, prefix='/api')

@app.get('/')
def root():
    return {
        "message" : "RGSM Backend is Running - Simulation Active"
    }