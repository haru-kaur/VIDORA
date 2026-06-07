# audio_processor.py

import whisper
import tempfile
import os
import re
from validators import validate_text_content

model = whisper.load_model("tiny")


def is_meaningful_text(text: str) -> bool:
    """
    Decide if Whisper output contains real speech
    """
    if not text:
        return False

    text = text.strip()

    if len(text) < 20:
        return False

    junk_patterns = ["♪", "[Music]", "(music)", "[Applause]", "(applause)"]
    for j in junk_patterns:
        if j.lower() in text.lower():
            return False

    words = re.findall(r"[a-zA-Z]{3,}", text)
    if len(words) < 5:
        return False

    return True


def extract_text_from_audio(audio_input):
    """
    Returns meaningful speech text
    If no speech → returns proper validator message
    """

    temp_created = False

    # ---- Handle input ----
    if isinstance(audio_input, str):
        audio_path = audio_input
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_input.read())
            audio_path = tmp.name
            temp_created = True

    # ---- Transcribe (Protected) ----
    try:
        result = model.transcribe(audio_path)
        text = result["text"].strip()
    except Exception:
        text = ""

    # ---- Cleanup ----
    if temp_created and os.path.exists(audio_path):
        os.remove(audio_path)

    # ---- Meaningful check ----
    if not is_meaningful_text(text):
        text = ""

    return validate_text_content(text, "AUDIO")