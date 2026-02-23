from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from paddleocr import PaddleOCR
import uvicorn
import io
import cv2
import numpy as np

app = FastAPI(title="PaddleOCR HA Addon")

# Konfiguration: Sprache, angle, use_gpu optional via ENV
ocr = PaddleOCR(use_angle_cls=True, lang='en')

class OCRResult(BaseModel):
    text: str
    confidence: float
    box: list

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    result = ocr.ocr(img, cls=True)
    # vereinfachte Ausgabe
    out = []
    for line in result:
        box, (txt, conf) = line
        out.append({"text": txt, "confidence": float(conf), "box": box})
    return {"lines": out}
