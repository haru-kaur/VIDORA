# pdf_processor.py

import fitz
import docx
from validators import validate_text_content

def extract_text_from_document(file_path):
    file_type = file_path.split(".")[-1].lower()
    text = ""

    if file_type == "pdf":
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()

    elif file_type == "docx":
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif file_type == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    return validate_text_content(text, "DOCUMENT")