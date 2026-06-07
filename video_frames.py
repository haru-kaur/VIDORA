# video_frames.py

import cv2
from PIL import Image
import pytesseract
from transformers import BlipProcessor, BlipForConditionalGeneration
import re
from validators import validate_text_content

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


def is_meaningful_visual(caption: str, ocr: str) -> bool:
    combined = (caption + " " + ocr).strip()

    if not combined or len(combined) < 30:
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


def extract_text_from_video_frames(video_path, frame_interval=60):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    collected_text = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            inputs = processor(pil_img, return_tensors="pt")
            out = model.generate(**inputs)
            caption = processor.decode(out[0], skip_special_tokens=True)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ocr_text = pytesseract.image_to_string(gray, config="--psm 6")
            ocr_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', ocr_text)
            ocr_text = re.sub(r'\b[a-zA-Z]{1,2}\b', ' ', ocr_text)
            ocr_text = re.sub(r'(.)\1{4,}', ' ', ocr_text)
            ocr_text = re.sub(r'\s+', ' ', ocr_text).strip()

            if is_meaningful_visual(caption, ocr_text):

                # Prefer OCR text
                if len(ocr_text.strip()) > 5:
                    collected_text += "\n" + ocr_text.strip() + "\n"

                # Use caption only when OCR fails
                elif len(caption.strip()) > 5:
                    collected_text += "\n" + caption.strip() + "\n"

        frame_count += 1

    cap.release()

    # ✅ THIS LINE FIXES EVERYTHING
    return validate_text_content(collected_text.strip(), "VIDEO")