# CentrAlign Intern Agent: Autonomous Invoice Processor

A working prototype demonstrating an autonomous agent that finds invoices, extracts data using an LLM, and logs them to an internal web portal using browser automation with **self-healing recovery** and **visual evidence logging**.

## The "Surprise" Factor

This implementation directly addresses the evaluation criteria:

| Requirement | Our Solution |
|-------------|--------------|
| **Recovery from failures** | `fill_field_with_retry()` - tries multiple selectors if CSS classes change |
| **Evidence of completion** | Captures screenshots at each step in `screenshots/` |
| **Verification** | Checks DOM for success banner + saves JSON report |
| **Structured output** | Returns `task_report.json` ready for logging/APIs |

## Architecture

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

## Setup

### Prerequisites

```bash
python3 -m venv venv
source venv/bin/activate

pip install flask playwright
playwright install chromium
```

### Quick Start

```bash
./run.sh
```

Or manually:

Terminal 1:
```bash
python app.py
```

This starts the mock internal portal at http://localhost:5000

Terminal 2:
```bash
python agent.py
```

The agent will:
1. Find `invoices/acme_invoice.txt`
2. Extract vendor, amount, and due date
3. Launch a browser with self-healing form fill
4. Capture screenshots at each step
5. Verify success banner appears
6. Generate `task_report.json`

## Sample Invoice

`invoices/acme_invoice.txt`:
```
INVOICE
Vendor: Acme Corp
Date: 2026-10-01
Amount: 1500.00
Due Date: 2026-10-20
```

## Output Artifacts

After successful execution:
- `screenshots/fill_1.png` - Vendor field filled
- `screenshots/fill_2.png` - Amount field filled  
- `screenshots/success.png` - Form submitted with success banner
- `task_report.json` - Structured JSON summary

## Limitations

- Uses mock LLM response (replace `call_llm()` with real API)
- Single vendor/sample invoice
- No database persistence
- Retry limit is 3 attempts per field

## Future Work

- Connect to real LLM provider (OpenClaw/Mercury API)
- Add PDF parsing library (PyMuPDF or pdfplumber)
- Implement exponential backoff for retries
- Add database storage for logged invoices
- Support multiple invoice formats
- Add human approval checkpoint for high-value invoices

## Technical Decisions

1. **Self-healing selectors**: Multiple fallback selectors (`input[name]`, `#id`, `aria-label`) to handle dynamic class names
2. **Screenshot evidence**: Captures at each step to prove execution, not just planning
3. **JSON report**: Machine-readable output for integration with other systems
4. **Single-file simplicity**: Flask + Playwright in minimal setup for easy debugging

## Submission Details

**GitHub Repository:** https://github.com/Govindu1729/centralign-intern

**Models Used:** Mock LLM (replace with OpenClaw/Mercury API)

**Frameworks:** Flask, Playwright

**Assumptions:**
- Invoice files are `.txt`, `.pdf`, or `.docx` in `./invoices/`
- Portal uses standard HTML form with `name` attributes
