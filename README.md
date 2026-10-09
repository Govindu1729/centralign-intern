# CentrAlign Intern Agent: Autonomous Invoice Processor

A working prototype demonstrating an autonomous agent that finds invoices, extracts data using an LLM, and logs them to an internal web portal using browser automation.

## Architecture

```
User Prompt → Agent Loop (ReAct)
    │
    ├─ Find → Scan ./invoices/ directory
    │
    ├─ Extract → Read file + LLM parsing
    │
    └─ Act → Playwright → Flask Portal → Verify DOM
```

## Setup

### Prerequisites

```bash
python3 -m venv venv
source venv/bin/activate

pip install flask playwright
playwright install chromium
```

### Running the Portal

Terminal 1:
```bash
python app.py
```

This starts the mock internal portal at http://localhost:5000

### Running the Agent

Terminal 2:
```bash
python agent.py
```

The agent will:
1. Find `invoices/acme_invoice.txt`
2. Extract vendor, amount, and due date
3. Launch a browser, fill the form, and submit
4. Verify the success banner appears

## Sample Invoice

`invoices/acme_invoice.txt`:
```
INVOICE
Vendor: Acme Corp
Date: 2026-10-01
Amount: 1500.00
Due Date: 2026-10-20
```

## How It Works

1. **Find**: Scans `./invoices/` for PDF/TXT files
2. **Extract**: Uses an LLM to parse vendor, amount, due_date into JSON
3. **Act**: Playwright navigates to Flask app, fills form, submits
4. **Verify**: Checks DOM for success banner; logs status

## Limitations

- Uses mock LLM response (replace `call_llm()` with real API)
- Single vendor/sample invoice
- No database persistence
- No error handling for network failures

## Future Work

- Connect to real LLM provider (OpenClaw/Mercury API)
- Add PDF parsing library (PyMuPDF or pdfplumber)
- Implement retry logic with data correction
- Add database storage for logged invoices
- Support multiple invoice formats

## Development Notes

This prototype prioritizes working browser automation over complex architecture. The agent loop is a simple ReAct pattern suitable for extending with more capabilities.
