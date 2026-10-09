# CentrAlign AI Internship - Autonomous Agent Sprint

**Project:** Autonomous Invoice Processor Agent  
**Stack:** Python, Flask, Playwright  
**Date:** Oct 2026  
**Status:** ✅ FULLY COMPLETE
**Repo:** https://github.com/Govindu1729/centralign-intern

## 🎯 Objective
Build an autonomous agent that finds invoice files (txt, pdf, docx), extracts structured data using a configurable LLM interface, and logs them to an internal portal using browser automation, with **self-healing recovery**, **visual evidence**, and **recursive discovery**.

## 🏗️ Architecture
```
User Prompt → Agent Loop (ReAct + Retries)
    │
    ├─ Find → Recursive Scan of ./invoices/
    │
    ├─ Read → Text or PDF (via pdf_extractor)
    │
    ├─ Extract → LLM Interface (llm_service)
    │
    ├─ Act → Playwright → Self-Healing Form Fill
    │                └─ Screenshots for evidence
    │
    └─ Report → JSON summary (task_report.json)
```

## 🧠 Key Features

| Category | Feature | Description |
|----------|---------|-------------|
| **Autonomy** | Full ReAct Loop | Finds → Reads → Extracts → Submits → Verifies |
| **Recovery** | Self-Healing | Tries 3 selector strategies per field (name, id, type) |
| **Recovery** | Bounded Retries | Attempts task up to N times before failing |
| **Evidence** | Visual Audit Trail | Captures screenshots at every step |
| **Evidence** | Structured Report | Generates `task_report.json` with status & metadata |
| **Discovery** | Recursive Search | Scans subdirectories for invoices |
| **Discovery** | Multi-format | Supports .txt, .pdf, .docx |
| **Config** | LLM Interface | Configurable via environment variables (mock, ollama, openai) |

## 💻 Code Structure

| File | Purpose |
|------|---------|
| `agent.py` | Main ReAct loop with bounded retries |
| `app.py` | Flask internal portal (port 5001) |
| `llm_service.py` | Configurable LLM interface (mock default) |
| `pdf_extractor.py` | Multi-library PDF text extraction |
| `requirements.txt` | Dependencies (flask, playwright, optional pdf libs) |
| `task_report.json` | Generated completion record |
| `screenshots/` | Generated visual evidence |

## 🚀 Quick Start

**1. Install Dependencies**
```bash
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

**2. (Optional) Configure LLM**
*By default, `mock` is used for testing.*
```bash
# For Ollama
export LLM_PROVIDER=ollama
export LLM_BASE_URL=http://localhost:11434

# For OpenAI
export LLM_PROVIDER=openai
export LLM_API_KEY=sk-...
```

**3. Run Demo**
```bash
# Terminal 1
python app.py

# Terminal 2
python agent.py
```

## 📝 Interview Notes

- **Reliability:** Uses bounded retries (`max_retries=2`) so it doesn't hang forever.
- **Evidence:** Every step is captured in `task_report.json` and `screenshots/`.
- **Scalability:** Recursive search + PDF support allows processing folders of files.
- **LLM Flexibility:** Swaps between mock/ollama/openai via env vars (no code change).
- **Troubleshooting:** Fixed Flask binding (`0.0.0.0`) and Playwright sandbox (`--no-sandbox`) for macOS compatibility.
