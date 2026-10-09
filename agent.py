#!/usr/bin/env python3
"""
Autonomous Invoice Processor Agent
Uses ReAct loop with self-healing recovery and visual evidence logging.
"""

import os
import json
import time
import glob
from playwright.sync_api import sync_playwright, TimeoutError

# LLM call simulation - in real implementation this would call OpenClaw/Mercury API
def call_llm(prompt):
    """
    Calls the LLM for text extraction.
    In production: use OpenClaw's LLM interface.
    """
    # Simulating LLM response for demo
    mock_response = {
        "vendor": "Acme Corp",
        "amount": 1500.00,
        "due_date": "2026-10-20"
    }
    return mock_response

def find_latest_invoice(invoice_dir="./invoices"):
    """Search for the latest invoice file in the directory."""
    invoices = [f for f in os.listdir(invoice_dir) if f.endswith(('.txt', '.pdf', '.docx'))]
    if not invoices:
        raise FileNotFoundError("No invoice files found in ./invoices/")
    # Return first/latest (sorted by name for simplicity)
    return os.path.join(invoice_dir, sorted(invoices)[-1])

def read_invoice_text(filepath):
    """Read text content from invoice file."""
    with open(filepath, 'r') as f:
        return f.read()

def extract_invoice_data(text):
    """Use LLM to extract structured data from invoice text."""
    prompt = f"""
Extract the following fields from this invoice text:
- vendor: the company name sending the invoice
- amount: the total amount in dollars (numeric only)
- due_date: the payment due date in YYYY-MM-DD format

Invoice text:
{text}

Return JSON only.
"""
    result = call_llm(prompt)
    return result

def fill_field_with_retry(page, value, selectors, name, max_attempts=3):
    """
    Self-healing field fill: tries multiple selectors if one fails.
    Returns (success: bool, selector_used: str)
    """
    for attempt in range(max_attempts):
        for selector in selectors:
            try:
                page.fill(selector, str(value))
                return True, selector
            except Exception:
                continue
    return False, None

def log_invoice_to_portal(vendor, amount, due_date, url="http://localhost:5000"):
    """
    Enhanced: self-healing fill, screenshots for evidence, and structured report.
    Returns (success: bool, evidence: dict)
    """
    os.makedirs('screenshots', exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate
            page.goto(url, timeout=15000)
            
            # Self-healing fill with multiple selector strategies
            vendor_opts = ['input[name="vendor"]', '#vendor', 'input[type="text"][aria-label*="vendor"]']
            amount_opts = ['input[name="amount"]', '#amount', 'input[type="number"]']
            date_opts = ['input[name="due_date"]', '#due_date', 'input[type="date"]']
            
            # Fill vendor
            success, sel = fill_field_with_retry(page, vendor, vendor_opts, 'vendor')
            if not success:
                raise Exception("Could not fill vendor field")
            page.screenshot(path='screenshots/fill_1.png')
            
            # Fill amount
            success, sel = fill_field_with_retry(page, amount, amount_opts, 'amount')
            if not success:
                raise Exception("Could not fill amount field")
            page.screenshot(path='screenshots/fill_2.png')
            
            # Fill date
            success, sel = fill_field_with_retry(page, due_date, date_opts, 'date')
            if not success:
                raise Exception("Could not fill date field")
            
            # Submit
            page.click('button[type="submit"]')
            
            # Wait for success banner
            page.wait_for_selector('#success-banner', timeout=10000)
            
            if page.is_visible('#success-banner'):
                page.screenshot(path='screenshots/success.png')
                return True, {
                    "screenshot": "screenshots/success.png",
                    "fields_filled": {"vendor": vendor, "amount": amount, "date": due_date},
                    "status": "success"
                }
            else:
                page.screenshot(path='screenshots/fail.png')
                return False, {"screenshot": "screenshots/fail.png", "status": "verification_failed"}
                
        except Exception as e:
            print(f"Portal Error: {e}")
            return False, {"error": str(e), "status": "failed"}
        finally:
            browser.close()

def agent_loop(prompt):
    """Main agent loop: Find -> Extract -> Act -> Verify -> Report"""
    print(f"🤖 Agent received: {prompt}")
    
    try:
        # Step 1: Find invoice
        print("🔍 Finding latest invoice...")
        invoice_path = find_latest_invoice()
        print(f"   Found: {invoice_path}")
        
        # Step 2: Read and extract
        print("📄 Reading invoice...")
        text = read_invoice_text(invoice_path)
        print(f"   Content preview: {text[:100]}...")
        
        print("🧠 Extracting data with LLM...")
        data = extract_invoice_data(text)
        print(f"   Extracted: {json.dumps(data, indent=2)}")
        
        # Step 3: Log to portal
        print("🌐 Submitting to portal...")
        success, evidence = log_invoice_to_portal(
            vendor=data["vendor"],
            amount=data["amount"],
            due_date=data["due_date"]
        )
        
        # Step 4: Generate structured report
        report = {
            "task": prompt,
            "invoice_file": invoice_path,
            "extracted_data": data,
            "success": success,
            "evidence": evidence,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save report
        with open('task_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        if success:
            print("✅ Invoice logged successfully!")
            print(f"📁 Report saved: task_report.json")
            print(f"🖼️ Evidence: {evidence.get('screenshot', 'N/A')}")
        else:
            print("❌ Verification failed. Check portal.")
            print(f"📁 Report saved: task_report.json")
        
        return success
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Default prompt for sprint demo
    prompt = "Find the latest invoice from Acme Corp, extract the amount and due date, and log it into the internal system."
    agent_loop(prompt)
