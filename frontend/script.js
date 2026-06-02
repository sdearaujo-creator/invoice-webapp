// Frontend logic for the Invoice Upload Tool.
// Uses relative URLs (/api/...) so it works both locally and once deployed.

const fileInput = document.getElementById("fileInput");
const processBtn = document.getElementById("processBtn");
const saveBtn = document.getElementById("saveBtn");
const results = document.getElementById("results");
const statusEl = document.getElementById("status");
const confidenceEl = document.getElementById("confidence");

const FIELDS = ["invoice_number", "vendor", "invoice_date", "due_date", "amount"];

function showStatus(message, kind) {
  statusEl.textContent = message;
  statusEl.className = "status " + kind; // kind = info | error | success
  statusEl.classList.remove("hidden");
}

// Step 1: send the PDF to the backend for extraction.
processBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    showStatus("Please choose a PDF file first.", "error");
    return;
  }

  processBtn.disabled = true;
  results.classList.add("hidden");
  showStatus("Processing…", "info");

  try {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/api/process", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) {
      showStatus(data.error || "Something went wrong while processing.", "error");
      return;
    }

    // Fill the editable fields with whatever was extracted.
    FIELDS.forEach((f) => {
      document.getElementById(f).value = data[f] == null ? "" : data[f];
    });

    const pct = Math.round((data.confidence || 0) * 100);
    if (data.flagged) {
      confidenceEl.textContent = `⚠️ Confidence ${pct}% — please double-check the fields below. ${data.notes || ""}`;
      confidenceEl.className = "confidence flagged";
    } else {
      confidenceEl.textContent = `✓ Confidence ${pct}% — looks good, but you can still edit.`;
      confidenceEl.className = "confidence";
    }

    results.classList.remove("hidden");
    showStatus("Extracted! Review the data, then save.", "success");
  } catch (err) {
    showStatus("Could not reach the server. Is it running?", "error");
  } finally {
    processBtn.disabled = false;
  }
});

// Step 2: send the (possibly edited) data to Airtable.
saveBtn.addEventListener("click", async () => {
  const payload = {};
  FIELDS.forEach((f) => {
    const value = document.getElementById(f).value.trim();
    payload[f] = f === "amount" ? parseFloat(value) || null : value || null;
  });

  saveBtn.disabled = true;
  showStatus("Saving to Airtable…", "info");

  try {
    const res = await fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (res.ok && data.success) {
      showStatus(`Saved to Airtable! Record ${data.airtable_record_id}`, "success");
    } else {
      showStatus(data.error || "Save failed.", "error");
    }
  } catch (err) {
    showStatus("Could not reach the server while saving.", "error");
  } finally {
    saveBtn.disabled = false;
  }
});
