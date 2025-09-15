# backend/app/analysis.py
import os
import csv
import json
import datetime
import cv2
import numpy as np
from deepface import DeepFace
from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile

router = APIRouter()

# ensure logs folder exists
LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
CSV_PATH = os.path.join(LOGS_DIR, "predictions.csv")

EMOTION_LABELS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]


def _safe_get_dominant_from_dict(d):
    """If d is dict of {label:score}, return (label, score) else (str(d), None)."""
    if isinstance(d, dict) and d:
        label = max(d, key=d.get)
        return label, float(d[label])
    if isinstance(d, str):
        return d, None
    return None, None


def analyze_image(file_path: str) -> dict:
    """
    Run DeepFace analysis on an image file and return structured JSON.
    This function is synchronous and may be CPU-heavy — call it in a thread.
    """
    try:
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Could not read image file")

        # DeepFace.analyze may return list or dict
        res = DeepFace.analyze(
            img,
            actions=["age", "gender", "emotion"],
            detector_backend="opencv",
            enforce_detection=False
        )

        if isinstance(res, list) and len(res) > 0:
            res = res[0]

        # Age (DeepFace returns numeric)
        age = res.get("age", None)
        age = int(age) if age is not None else None

        # Gender
        gender = res.get("dominant_gender") or res.get("gender")
        if isinstance(gender, dict):   # {Male:0.8, Female:0.2}
            gender_label, gender_conf = _safe_get_dominant_from_dict(gender)
        else:
            gender_label = str(gender) if gender else None
            gender_conf = None

        # Emotion
        emotion_label = res.get("dominant_emotion")
        emotion_conf = None
        if not emotion_label:
            emotion_dict = res.get("emotion", {})
            emotion_label, emotion_conf = _safe_get_dominant_from_dict(emotion_dict)
        else:
            # check for confidence
            emotion_dict = res.get("emotion", {})
            if isinstance(emotion_dict, dict) and emotion_label in emotion_dict:
                emotion_conf = float(emotion_dict.get(emotion_label, 0.0))

        # all_emotions
        all_emotions = {}
        if "emotion" in res and isinstance(res["emotion"], dict):
            all_emotions = {k: float(v) for k, v in res["emotion"].items()}

        result = {
            "status": "success",
            "file_path": file_path,
            "age": age,
            "gender": gender_label,
            "gender_confidence": gender_conf,
            "emotion": emotion_label,
            "emotion_confidence": emotion_conf,
            "all_emotions": all_emotions,
            "raw_deepface": {k: v for k, v in res.items() if k in ("age", "gender", "emotion")}
        }

        # append to CSV log
        try:
            _append_to_csv(result)
        except Exception as e:
            print("Logging error:", e)

        return result

    except Exception as e:
        return {"status": "error", "error": str(e)}


def _append_to_csv(result: dict):
    """Append a one-line row to predictions.csv with basic columns."""
    header = [
        "timestamp", "file_path", "age",
        "gender", "gender_confidence",
        "emotion", "emotion_confidence", "all_emotions_json"
    ]
    write_header = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        row = [
            datetime.datetime.utcnow().isoformat(),
            result.get("file_path"),
            result.get("age"),
            result.get("gender"),
            result.get("gender_confidence"),
            result.get("emotion"),
            result.get("emotion_confidence"),
            json.dumps(result.get("all_emotions", {}))
        ]
        writer.writerow(row)


@router.post("/analyze/")
async def analyze_emotion(file: UploadFile = File(...)):
    """
    API endpoint: Upload an image and get emotion analysis.
    """
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        result = analyze_image(tmp_path)

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result["error"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
