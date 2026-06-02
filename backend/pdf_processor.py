"""
PDF invoice extraction (adapted from the Lesson 2.2 processor).

Pure functions: give it a PDF path, get back a dict of extracted fields.
No logging, no Airtable, no .env — this module just reads PDFs. That keeps the
web app self-contained so it can be deployed without the original 2.2 project.
"""

import re
from datetime import datetime

import pdfplumber

REQUIRED_FIELDS = ["invoice_number", "vendor", "invoice_date", "due_date", "amount"]


def read_pdf_text(path):
    """Extract text from every page, then strip leftover HTML-ish tags."""
    with pdfplumber.open(path) as pdf:
        text = "\n".join((page.extract_text() or "") for page in pdf.pages)
    return re.sub(r"<[^>]+>", " ", text)


def _normalize_date(s):
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _money(s):
    return float(s.replace(",", ""))


def _invoice_number(text):
    m = re.search(r"invoice\s*(?:number|no\.?|#)\s*:?\s*([A-Z]{2,4}-?\d[\w-]+)", text, re.I)
    return m.group(1).strip() if m else None


def _vendor(text):
    for line in text.splitlines():
        line = line.strip()
        if len(line) >= 3 and line.upper() != "INVOICE":
            return line.title() if line.isupper() else line
    return None


def _date(text, kind):
    if kind == "due":
        m = re.search(r"due\s*date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.I)
    else:
        m = re.search(r"(?<!due\s)invoice\s*date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.I)
        if not m:
            m = re.search(r"(?<!due\s)\bdate\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.I)
    return _normalize_date(m.group(1)) if m else None


def _amount_after(label, text):
    m = re.search(rf"{label}\s*(?:\([^)]*\))?\s*:?\s*\$?\s*([\d,]+\.\d{{2}})", text, re.I)
    return _money(m.group(1)) if m else None


def _total(text):
    candidates = re.findall(
        r"(?<!sub)(?:total due|amount due|total)\s*:?\s*[>\s]*\$?\s*([\d,]+\.\d{2})", text, re.I
    )
    amounts = [_money(c) for c in candidates]
    return max(amounts) if amounts else None


def _confidence(data):
    found = sum(1 for f in REQUIRED_FIELDS if data.get(f) is not None)
    return round(found / len(REQUIRED_FIELDS), 2)


def _validation_notes(data):
    notes = []
    for f in REQUIRED_FIELDS:
        if not data.get(f):
            notes.append(f"missing {f}")
    if data.get("invoice_date") and data.get("due_date"):
        if data["due_date"] < data["invoice_date"]:
            notes.append("due date before invoice date")
    if data.get("amount") is not None and data["amount"] <= 0:
        notes.append("amount not positive")
    return "; ".join(notes)


def process_pdf(path):
    """Read a PDF and return extracted invoice fields + a confidence score."""
    text = read_pdf_text(path)
    data = {
        "invoice_number": _invoice_number(text),
        "vendor": _vendor(text),
        "invoice_date": _date(text, "invoice"),
        "due_date": _date(text, "due"),
        "amount": _total(text),
    }
    data["confidence"] = _confidence(data)
    data["notes"] = _validation_notes(data)
    # Low confidence or any validation problem -> ask the human to double-check.
    data["flagged"] = data["confidence"] < 0.90 or bool(data["notes"])
    return data
