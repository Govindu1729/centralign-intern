# CentrAlign Intern Agent: Autonomous Invoice Processor

A working prototype demonstrating an autonomous agent that finds invoices, extracts data using an LLM, and logs them to an internal web portal using browser automation with **self-healing recovery** and **visual evidence logging**.

## 🚀 Quick Test (Live Demo)

**1. Install Dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```

**2. Start Portal (Terminal 1)**
```bash
python app.py
```
*Server starts at http://localhost:5000*

**3. Run Agent (Terminal 2)**
```bash
python agent.py
```

**4. Verify Artifacts**
```bash
ls -la screenshots/
cat task_report.json
```

## ✅ Submission Checklist

| Criteria | Implementation | Status |
|----------|----------------|--------|
| **Autonomy** | ReAct loop (Find → Extract → Act → Verify) | ✅ |
| **Execution** | Actual Playwright + file ops (not just plans) | ✅ |
| **Failure Recovery** | `fill_field_with_retry()` - tries 3 alternate selectors per field | ✅ |
| **Evidence** | Screenshots at each step (`screenshots/`) + JSON report | ✅ |
| **Verification** | DOM check for success banner | ✅ |
| **Generalization** | Fallback selectors (id, name, aria-label) handle DOM changes | ✅ |
| **Quality** | Modular, documented, error handling, GitHub hosted | ✅ |

## 🧠 The "Surprise" Factor

This implementation directly addresses the evaluation criteria with **Self-Healing Recovery & Visual Evidence**:

| Requirement | Our Solution |
|-------------|--------------|
| **Recovery from failures** | `fill_field_with_retry()` - tries multiple selectors if CSS classes change |
| **Evidence of completion** | Captures screenshots at each step in `screenshots/` |
| **Verification** | Checks DOM for success banner + saves JSON report |
| **Structured output** | Returns `task_report.json` ready for logging/APIs |

## 🏗️ Architecture

```
User Prompt → Agent Loop (ReAct)
    │
    ├─ Find → Scan ./invoices/ directory
    │
    ├─ Extract → Read file + LLM parsing
    │
    ├─ Act → Playwright → Self-Healing Form Fill
    │                └─ Screenshots for evidence
    │
    └─ Report → JSON summary
```

## 📁 Project Structure

```
centralign-intern/
├── app.py              # Flask internal portal
├── agent.py            # ReAct agent with self-healing logic
├── requirements.txt    # Dependencies
├── run.sh              # Quick start script
├── invoices/           # Sample invoice data
├── screenshots/        # Visual evidence (generated)
└── task_report.json    # Structured completion report (generated)
```

## 🧪 Sample Invoice

`invoices/acme_invoice.txt`:
```
INVOICE
Vendor: Acme Corp
Date: 2026-10-01
Amount: 1500.00
Due Date: 2026-10-20
```

## 📊 Output Artifacts

After successful execution:
- `screenshots/fill_1.png` - Vendor field filled
- `screenshots/fill_2.png` - Amount field filled  
- `screenshots/success.png` - Form submitted with success banner
- `task_report.json` - Structured JSON summary

## 🛠️ Technical Details

- **Mock LLM:** `agent.py` includes a `call_llm()` function with mock data. Replace with real OpenClaw/Mercury API for production.
- **Self-Healing Selectors:** If the primary CSS selector fails (e.g., dynamic classes), the agent tries 3 alternate strategies (`input[name]`, `#id`, `aria-label`).
- **Visual Evidence:** Captures screenshots at each step to prove execution, not just planning.
- **Retry Limit:** 3 attempts per field.
- **Error Handling:** Catches `FileNotFoundError` and generic exceptions, logging them to terminal and report.

## 🔮 Future Work

- Connect to real LLM provider (OpenClaw/Mercury API)
- Add PDF parsing library (PyMuPDF or pdfplumber)
- Implement exponential backoff for retries
- Add database storage for logged invoices
- Support multiple invoice formats
- Add human approval checkpoint for high-value invoices

## 🔗 Submission Details

**GitHub Repository:** https://github.com/Govindu1729/centralign-intern

**Status:** ✅ Code committed and pushed to `main` branch

**Models Used:** Mock LLM (replace with OpenClaw/Mercury API)

**Frameworks:** Flask, Playwright
