# Invoice Upload Tool — User Guide

A self-service tool for the Finance team. Upload a PDF invoice, the tool reads
the key details for you, you check them, and it saves the invoice to Airtable —
all from your browser. No software to install.

## What it does

Instead of typing invoice details into Airtable by hand, you upload the PDF and
the tool extracts the **Invoice Number, Vendor, Invoice Date, Due Date, and
Amount** automatically. You review what it found, fix anything that's off, and
save. It typically takes a few seconds per invoice.

## How to use it

1. **Open the tool:** https://invoice-webapp-git-main-sdearaujo-6674s-projects.vercel.app
2. Click **Choose File** and select your invoice PDF.
3. Click **Process Invoice**.
4. **Review the extracted data** in the five boxes.
   - A green **✓** means the tool is confident — but still glance at it.
   - A yellow **⚠️** means *please double-check* — it will name which fields look
     missing or wrong.
5. **Edit any field** that's blank or incorrect — just click in the box and type.
   Whatever is in the boxes when you save is what gets saved.
6. Click **Save to Airtable**.
7. You'll see a green confirmation with a record ID. Done — the invoice is now
   in Airtable.

## Troubleshooting

- **"Please upload a PDF file."** — The file isn't a PDF (e.g. a Word doc, image,
  or screenshot). Save or export it as a PDF and try again.
- **"File too large. Please upload a PDF under 5 MB."** — The PDF is too big.
  Most invoices are well under 5 MB; a large file is usually a high-resolution
  scan. Re-save it at a smaller size, or ask the vendor for a standard PDF.
- **All the boxes came back blank (⚠️ 0% confidence).** — The PDF is most likely a
  **scanned image** (a photo of an invoice with no real text underneath). The
  tool can't read text from an image. Either type the five fields in by hand and
  save, or request a text-based PDF from the vendor.
- **A field is wrong or missing.** — Normal — extraction isn't perfect on every
  vendor's format. Just correct the box before saving. Never save without
  eyeballing the fields against the actual invoice.
- **"Could not reach the server."** — The tool isn't running or your connection
  dropped. Refresh the page; if it persists, contact the owner below.

## Works best with

- Standard text-based invoices with a clear invoice number
- Dates in MM/DD/YYYY format
- Dollar amounts written with cents (e.g. `1,242.00`)

## May need manual review

- Scanned or photographed invoices (images, not text)
- Handwritten invoices
- Unusual or non-English formats

## Questions?

Contact: [your name / email]
