# doc_scan.py
import re

def scan_document_for_counts(question):
    with open("full_document.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # Count Figures
    if "figure" in question.lower():
        figures = re.findall(r'Figure\s+\d+(\.\d+)?', text, re.IGNORECASE)
        unique_figures = set(figures)
        return f"Total figures in the document: {len(unique_figures)}"

    # Count Tables
    if "table" in question.lower():
        tables = re.findall(r'Table\s+\d+(\.\d+)?', text, re.IGNORECASE)
        unique_tables = set(tables)
        return f"Total tables in the document: {len(unique_tables)}"

    return None