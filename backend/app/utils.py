# utils.py

from fastapi import HTTPException
import io
from PIL import Image
import numpy as np
import cv2

def read_image_from_file(file_bytes) -> np.ndarray:
    """
    Convert uploaded file bytes into OpenCV image (BGR).
    """
    try:
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        np_image = np.array(image)
        # Convert RGB to BGR
        return cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file")

