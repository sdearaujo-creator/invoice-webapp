# Invoice Upload Web App

A self-service web tool: upload a PDF invoice, review the data the app extracts,
edit anything that's off, and save it to Airtable — all from a browser.

Built on the PDF extraction logic from the Lesson 2.2 invoice processor, wrapped
in a Flask backend and a simple HTML/CSS/JS frontend.

## How it works

```
Browser (frontend)                    Flask (backend)
  upload PDF        ── POST /api/process ──►  extract fields from the PDF
  show + edit data  ◄──── JSON ──────────────
  click Save        ── POST /api/save ─────►  create a record in Airtable
  show confirmation ◄──── record id ─────────
```

## Run it locally

```powershell
cd backend
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000** in your browser.

## Environment variables

The backend reads these from `backend/.env` (not committed):

```
AIRTABLE_TOKEN=...
AIRTABLE_BASE_ID=...
AIRTABLE_TABLE=...
```

## Project layout

```
invoice-upload-webapp/
├── backend/
│   ├── app.py             Flask server + API routes
│   ├── pdf_processor.py   PDF extraction (from Lesson 2.2)
│   ├── airtable_client.py Saves a record to Airtable
│   ├── requirements.txt
│   └── .env               Airtable keys (gitignored)
└── frontend/
    ├── index.html         Upload page
    ├── style.css          Styling
    └── script.js          Upload → process → edit → save logic
```

## Notes

- Only PDF files are accepted; uploads over 5 MB are rejected.
- Low-confidence extractions are flagged so the user double-checks before saving.
- Deployment (a public URL) is covered in Lesson 2.5.
