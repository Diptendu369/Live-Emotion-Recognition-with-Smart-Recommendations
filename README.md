# EMOTION

Day 1-2: Build notebook with DeepFace + OpenCV (real-time age/gender/emotion).

Day 3-4: Wrap backend with FastAPI. Endpoint: POST /analyze (image upload), GET /health.

Day 5-6: Frontend React/Vite placeholders included. Wire webcam + overlays.

Day 7: Deploy backend (Render/Railway) and frontend (Vercel).

## Backend quickstart

python -m venv .venv
. .venv/Scripts/Activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload

## Frontend quickstart (after you init Vite)

npm install
npm run dev
