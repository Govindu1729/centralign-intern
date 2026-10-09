#!/usr/bin/env python3
"""
Autonomous Invoice Processor Agent
Uses ReAct loop with self-healing recovery, PDF support, and real LLM integration.
"""

import os
import json
import time
import glob
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError

from llm_service import extract_invoice_data
from pdf_extractor import extract_text_from_pdf


def find_latest_invoice(invoice_dir="./invoices", recursive=True):
    """
    Search for the latest invoice file in the directory.
    Supports recursive search through subdirectories.
    Handles .txt, .pdf, .docx files.
    """
    files = []
    invoice_dir = Path(invoice_dir)
    
    if not invoice_dir.exists():
        raise FileNotFoundError(f"Invoice directory not found: {invoice_dir}")
    
    if recursive:
        # Search recursively for all invoice files
        for pattern in ["**/*.txt", "**/*.pdf", "**/*.docx", "**/*.doc"]:
            files.extend(invoice_dir.glob(pattern))
    else:
        # Only check top-level directory
        for pattern in ["*.txt", "*.pdf", "*.docx", "*.doc"]:
            files.extend(invoice_dir.glob(pattern))
    
    # Filter out hidden files and directories
    files = [f for f in files if not any(part.startswith('.') for part in f.parts)]
    
    if not files:
        raise FileNotFoundError(f"No invoice files found in {invoice_dir}")
    
    # Sort by modification time (most recent first)
    return str(max(files, key=lambda f: f.stat().st_mtime))


def read_invoice_text(filepath):
    """
    Read text content from invoice file.
    Supports .txt, .pdf, .docx files with auto-detection.
    """
    filepath = Path(filepath)
    ext = filepath.suffix.lower()
    
    # Handle PDF files
    if ext == ".pdf":
        return extract_text_from_pdf(str(filepath))
    
    # Handle DOCX files (if python-docx is installed)
    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(str(filepath))
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            raise RuntimeError("python-docx not installed. Install with: pip install python-docx")
    
    # Handle TXT files
    if ext in [".txt", ".doc"]:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    # Default: try to read as text
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def fill_field_with_retry(page, value, selectors, name, timeout=10000):
    """
    Self-healing field fill: tries multiple selectors if one fails.
    Returns (success: bool, selector_used: str)
    """
    print(f"  🔄 Looking for '{name}' field...")
    for selector in selectors:
        try:
            print(f"     ⏳ Finding: {selector}")
            elem = page.wait_for_selector(selector, state="visible", timeout=timeout)
            print(f"  ✅ FOUND: {selector}")
            elem.evaluate("el => el.value = ''")
            elem.fill(str(value))
            print(f"  ✅ FILLED: {selector} with value: {value}")
            return True, selector
        except TimeoutError:
            print(f"     ❌ Timeout/not found: {selector}")
            continue
        except Exception as e:
            print(f"     ❌ Error filling: {type(e).__name__}: {e}")
            continue
    print(f"  ❌ FAILED to find/fill '{name}'")
    return False, None


def log_invoice_to_portal(vendor, amount, due_date, url="http://localhost:5001"):
    """
    Enhanced: self-healing fill, screenshots for evidence, and structured report.
    Returns (success: bool, evidence: dict)
    """
    os.makedirs('screenshots', exist_ok=True)
    browser = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            page = browser.new_page()
            
            print(f"  🔗 Navigating to {url}...")
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            print("  ✅ Page loaded!")
            
            print("  ⏳ Waiting for form to be ready...")
            page.wait_for_selector("form", timeout=5000)
            print("  ✅ Form found on page!")
            
            page.screenshot(path='screenshots/page_full.png')
            print("  ✅ Saved page screenshot: page_full.png")
            
            vendor_opts = ['input[name="vendor"]', '#vendor', 'form input[type="text"]']
            amount_opts = ['input[name="amount"]', '#amount', 'form input[type="number"]']
            date_opts = ['input[name="due_date"]', '#due_date', 'form input[type="date"]']
            
            print("  ⬆️ Filling vendor field...")
            success, sel = fill_field_with_retry(page, vendor, vendor_opts, 'vendor')
            if not success:
                raise Exception("Could not fill vendor field")
            page.screenshot(path='screenshots/fill_1.png')
            
            print("  ⬆️ Filling amount field...")
            success, sel = fill_field_with_retry(page, amount, amount_opts, 'amount')
            if not success:
                raise Exception("Could not fill amount field")
            page.screenshot(path='screenshots/fill_2.png')
            
            print("  ⬆️ Filling date field...")
            success, sel = fill_field_with_retry(page, due_date, date_opts, 'date')
            if not success:
                raise Exception("Could not fill date field")
            page.screenshot(path='screenshots/fill_3.png')
            
            print("  ⚡ Submitting form...")
            page.click('button[type="submit"]', timeout=5000)
            page.wait_for_timeout(2000)
            
            print("  ⏳ Waiting for success confirmation...")
            try:
                page.wait_for_selector('#success-banner', timeout=10000)
                if page.is_visible('#success-banner'):
                    page.screenshot(path='screenshots/success.png')
                    print("  ✅ Success banner detected!")
                    return True, {
                        "screenshot": "screenshots/success.png",
                        "fields_filled": {"vendor": vendor, "amount": amount, "date": due_date},
                        "status": "success"
                    }
                else:
                    page.screenshot(path='screenshots/fail.png')
                    return False, {"screenshot": "screenshots/fail.png", "status": "verification_failed"}
            except TimeoutError:
                page.screenshot(path='screenshots/fail.png')
                return False, {"screenshot": "screenshots/fail.png", "status": "no_banner"}
                
    except TimeoutError as e:
        print(f"  ❌ Timeout: {e}")
        return False, {"error": "Timeout", "status": "failed"}
    except Exception as e:
        print(f"  ❌ Portal Error: {type(e).__name__}: {e}")
        return False, {"error": str(e), "status": "failed"}


def agent_loop(prompt, invoice_dir="./invoices", max_retries=2, recursive=True):
    """
    Main agent loop with bounded retries for recovery.
    
    Args:
        prompt: User request describing the task
        invoice_dir: Directory to search for invoices (auto-discovered if not specified)
        max_retries: Maximum number of retry attempts
        recursive: Whether to search subdirectories
    """
    print(f"🤖 Agent received: {prompt}")
    print(f"📋 Invoice directory: {invoice_dir}")
    print(f"📋 Recursive search: {recursive}")
    print(f"📋 Max retries: {max_retries}")
    print()
    
    for attempt in range(max_retries + 1):
        print(f"🔄 Attempt {attempt + 1}/{max_retries + 1}")
        print()
        
        try:
            print("🔍 Finding latest invoice (auto-discovery)...")
            invoice_path = find_latest_invoice(invoice_dir, recursive)
            print(f"   Found: {invoice_path}")
            
            print("📄 Reading invoice...")
            text = read_invoice_text(invoice_path)
            print(f"   Content preview: {text[:100]}...")
            
            print("🧠 Extracting data with LLM...")
            data = extract_invoice_data(text)
            print(f"   Extracted: {json.dumps(data, indent=2)}")
            
            print("🌐 Submitting to portal...")
            success, evidence = log_invoice_to_portal(
                vendor=data["vendor"],
                amount=data["amount"],
                due_date=data["due_date"]
            )
            
            report = {
                "task": prompt,
                "invoice_file": invoice_path,
                "extracted_data": data,
                "success": success,
                "evidence": evidence,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "attempt": attempt + 1,
                "max_retries": max_retries
            }
            
            with open('task_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            if success:
                print("✅ Invoice logged successfully!")
                print(f"📁 Report saved: task_report.json")
                print(f"🖼️ Evidence: {evidence.get('screenshot', 'N/A')}")
                return True
            else:
                print("❌ Verification failed. Check portal.")
                print(f"📁 Report saved: task_report.json")
                if attempt < max_retries:
                    print("🔄 Retrying after 2 seconds...")
                    time.sleep(2)
                else:
                    break
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            report = {"task": prompt, "success": False, "error": str(e), "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "attempt": attempt + 1}
            with open('task_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            report = {"task": prompt, "success": False, "error": str(e), "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "attempt": attempt + 1}
            with open('task_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            if attempt < max_retries:
                time.sleep(2)
            else:
                return False
    
    print("❌ Max retries reached. Aborting.")
    return False


if __name__ == "__main__":
    prompt = "Find the latest invoice from Acme Corp, extract the amount and due date, and log it into the internal system."
    agent_loop(prompt)
