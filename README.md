# CentrAlign AI Internship - Autonomous Invoice Processor

## Project Overview
I am building a Python-based invoice-processing agent that discovers invoice files, extracts structured data through a configurable LLM interface, and submits the results to a local web portal using Playwright.

**Repository:** https://github.com/Govindu1729/centralign-intern

---

## 🏗️ Implementation Status

### ✅ Implemented Features

| Component | Details |
|-----------|---------|
| **File Discovery** | Recursive search across `./invoices/` directory; selects file by modification time |
| **Text Extraction** | Native support for `.txt` and `.doc` files |
| **PDF Extraction** | Modular `pdf_extractor.py` with fallback libraries (PyMuPDF, pdfplumber, PyPDF2) |
| **DOCX Extraction** | `python-docx` integration for Word documents |
| **LLM Interface** | Configurable provider interface (`llm_service.py`) supporting mock, Ollama, OpenAI, Anthropic |
| **Browser Automation** | Playwright fills and submits the local portal form |
| **Self-Healing Recovery** | Tries 3 selector strategies (name, id, type) if primary selector fails |
| **Bounded Retries** | Configurable retry attempts (`max_retries=2` by default) |
| **Visual Evidence** | Screenshots captured at every step (`screenshots/` directory) |
| **Structured Reporting** | JSON completion report generated (`task_report.json`) |

### ⏳ In Progress / Pending

| Component | Notes |
|-----------|-------|
| **Real LLM Integration** | Provider interface exists; mock provider is default for testing. Active work: connect and validate real extraction. |
| **Persistent Storage** | Portal does not save submitted records to database; uses URL parameters for demo |
| **Duplicate Detection** | Not yet implemented |
| **End-to-End Testing** | Fresh pipeline validation with real LLM provider pending |

---

## 🚀 Quick Start

**1. Install Dependencies**
```bash
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

**2. (Optional) Configure LLM Provider**
```bash
# Default: mock provider (deterministic testing)

# For Ollama
export LLM_PROVIDER=ollama
export LLM_BASE_URL=http://localhost:11434

# For OpenAI
export LLM_PROVIDER=openai
export LLM_API_KEY=***

# For Anthropic
export LLM_PROVIDER=anthropic
export LLM_API_KEY=***
```

**3. Run the Agent**
```bash
# Terminal 1: Start portal
python app.py

# Terminal 2: Run agent
python agent.py
```

---

## 🧠 Architecture

```
User Prompt
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│              Agent Loop (ReAct + Retries)               │
└─────────────────────────────────────────────────────────┘
         │                    │
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│  Discovery      │  │  Verification   │
│  - Recursive    │  │  - DOM Check    │
│  - By mtime     │  │  - Screenshots  │
└─────────────────┘  └─────────────────┘
         │                    │
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│  Reading        │  │  Reporting      │
│  - TXT/DOC      │  │  - JSON (task_  │
│  - PDF          │  │    report.json) │
│  - DOCX         │  │  - Timestamp    │
└─────────────────┘  └─────────────────┘
         │
         │
         ▼
┌─────────────────┐
│  LLM Extract    │
│  - Configurable │
│  - Validate     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Playwright     │
│  - Self-healing │
│  - Retries      │
└─────────────────┘
```

---

## 🔧 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Modular LLM Interface** | Allows swapping providers (mock/ollama/openai) without code changes |
| **Bounded Retries** | Prevents infinite loops while still recovering from transient failures |
| **Selector Fallbacks** | Handles minor HTML changes (e.g., dynamic class names) |
| **Recursive Search** | Finds invoices in subdirectories without manual path specification |
| **Screenshot Evidence** | Provides visual proof of execution, not just logs |

---

## 📝 Testing Checklist

- [x] **Discovery**: Recursive search finds latest file by modification time
- [x] **TXT Extraction**: Reads text files successfully
- [x] **PDF Module**: Library available (needs `pymupdf` for actual parsing)
- [x] **Selector Recovery**: Tries alternative selectors when primary fails
- [x] **Portability**: Fixed port 5001; Flask binds to `0.0.0.0`
- [ ] **Live LLM Extraction**: Pending provider connection
- [ ] **End-to-End Pipeline**: Needs verification with real invoice

---

## 🔮 Next Steps

1. **Connect LLM Provider**: Integrate OpenAI/Ollama/Anthropic API
2. **Add Validation**: Ensure extracted fields match expected formats
3. **Implement Persistence**: Store results in database
4. **Add Duplicate Detection**: Prevent re-processing same invoice

---

## 📦 Dependencies

**Required:**
- Flask
- Playwright

**Optional:**
- PyMuPDF (PDF extraction)
- pdfplumber (PDF extraction fallback)
- PyPDF2 (PDF extraction fallback)
- python-docx (Word document extraction)
- openai (for OpenAI provider)
- anthropic (for Anthropic provider)

**Note:** The agent runs out-of-the-box with mock LLM for demonstration.

---

## ⚠️ Limitations

- Uses mock LLM responses by default (requires provider configuration for real extraction)
- PDF parsing requires additional library installation (`pymupdf`, `pdfplumber`, or `PyPDF2`)
- No database persistence; portal stores data temporarily in session
- Form selector recovery limited to 3 alternatives
