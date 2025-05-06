from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import pytesseract
from backend.utils.video_recommendation import get_video_links_for_mistakes

router = APIRouter()

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    original: str = Form(...)
):
    try:
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes))

        extracted_text = pytesseract.image_to_string(image, lang='tur').strip()

        wrong_letters = []
        for a, b in zip(extracted_text, original):
            if a != b:
                wrong_letters.append(b)

        unique_wrong_letters = sorted(set(wrong_letters), key=wrong_letters.index)

        video_links = get_video_links_for_mistakes(unique_wrong_letters)

        return {
            "extracted_text": extracted_text,
            "wrong_letters": unique_wrong_letters,
            "video_links": video_links
        }

    except Exception as e:
        print("Hata:", str(e))
        return JSONResponse(status_code=500, content={"error": f"Analiz hatası: {str(e)}"})
