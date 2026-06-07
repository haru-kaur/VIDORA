# validators.py

def validate_text_content(text, source_type):
    """
    Only validates.
    Does NOT return user messages.
    Returns:
        text  -> if valid
        None  -> if invalid
    """

    if not text or len(text.strip()) == 0:
        return None

    if len(text.strip()) < 30:
        return None

    return text