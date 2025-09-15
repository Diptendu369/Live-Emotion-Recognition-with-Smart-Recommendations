# backend/app/main.py
import os
import uuid
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import router from analysis
from app.analysis import router as analysis_router
from app.recommend import get_recommendations  # keep this if you have recommendations

app = FastAPI(title="Live Emotion Recognition API")

# Allow frontend during development (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Emotion backend running"}

# ✅ Include analysis router
app.include_router(analysis_router, prefix="/api", tags=["analysis"])
