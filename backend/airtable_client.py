"""
Airtable integration — creates one invoice record.
Credentials come from environment variables (never hardcoded).
"""

import os

import requests

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE = os.getenv("AIRTABLE_TABLE")


def save_invoice(data):
    """Create an Airtable record from invoice data.

    Returns (True, record_id) on success or (False, error_message) on failure.
    """
    if not all([AIRTABLE_TOKEN, BASE_ID, TABLE]):
        return False, "Airtable credentials are not configured on the server."

    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    fields = {
        "Invoice Number": data.get("invoice_number"),
        "Vendor": data.get("vendor"),
        "Invoice Date": data.get("invoice_date"),
        "Due Date": data.get("due_date"),
        "Amount": data.get("amount"),
        "Status": "Received",
        "Notes": "Submitted via Invoice Upload web app.",
    }
    # Airtable rejects null values — drop anything blank.
    fields = {k: v for k, v in fields.items() if v not in (None, "")}

    try:
        r = requests.post(url, headers=headers, json={"fields": fields}, timeout=30)
        if r.status_code == 200:
            return True, r.json().get("id")
        return False, f"Airtable error {r.status_code}: {r.text}"
    except Exception as e:
        return False, str(e)
