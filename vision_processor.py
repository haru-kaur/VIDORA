#vision_processor.py

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import pytesseract
import re
from validators import validate_text_content

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


def is_meaningful_image_text(caption: str, ocr: str) -> bool:
    combined = (caption + " " + ocr).strip()

    if not combined or len(combined) < 25:
        return False

    junk = [
        "a blurry image",
        "a picture of something",
        "an image",
        "a photo",
        "something"
    ]
    for j in junk:
        if j in combined.lower():
            return False

    words = re.findall(r"[a-zA-Z]{4,}", combined)
    if len(words) < 6:
        return False

    return True


def extract_text_from_image(image_path):
    image = Image.open(image_path).convert("RGB")

    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)

    ocr_text = pytesseract.image_to_string(image)

    # ✅ THE IMPORTANT LINE YOU MISSED
    # if not is_meaningful_image_text(caption, ocr_text):
    #     return validate_text_content("", "IMAGE")

    final_text = f"""
Image Description:
{caption}

Text Found In Image:
{ocr_text}
"""

    return validate_text_content(final_text, "IMAGE")