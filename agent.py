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

def fill_field_with_retry(page, value, selectors, name, timeout=10000):
    """
    Self-healing field fill: tries multiple selectors if one fails.
    Returns (success: bool, selector_used: str)
    """
    print(f"  🔄 Looking for '{name}' field...")
    for selector in selectors:
        try:
            print(f"     ⏳ Finding: {selector}")
            # Wait for element with state="visible" ensures it's actually shown
            elem = page.wait_for_selector(selector, state="visible", timeout=timeout)
            print(f"  ✅ FOUND: {selector}")
            
            # Clear and fill the element
            elem.clear()
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
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            page = browser.new_page()
            
            # Navigate with explicit wait for page load
            print(f"  🔗 Navigating to {url}...")
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            print("  ✅ Page loaded!")
            
            # Wait for the page to be fully ready
            print("  ⏳ Waiting for form to be ready...")
            page.wait_for_selector("form", timeout=5000)
            print("  ✅ Form found on page!")
            
            # Take a screenshot of the page to verify
            page.screenshot(path='screenshots/page_full.png')
            print("  ✅ Saved page screenshot: page_full.png")
            
            # Now try to fill fields
            vendor_opts = ['input[name="vendor"]', '#vendor', 'form input[type="text"]']
            amount_opts = ['input[name="amount"]', '#amount', 'form input[type="number"]']
            date_opts = ['input[name="due_date"]', '#due_date', 'form input[type="date"]']
            
            # Fill vendor
            print("  ⬆️ Filling vendor field...")
            success, sel = fill_field_with_retry(page, vendor, vendor_opts, 'vendor')
            if not success:
                raise Exception("Could not fill vendor field")
            page.screenshot(path='screenshots/fill_1.png')
            
            # Fill amount
            print("  ⬆️ Filling amount field...")
            success, sel = fill_field_with_retry(page, amount, amount_opts, 'amount')
            if not success:
                raise Exception("Could not fill amount field")
            page.screenshot(path='screenshots/fill_2.png')
            
            # Fill date
            print("  ⬆️ Filling date field...")
            success, sel = fill_field_with_retry(page, due_date, date_opts, 'date')
            if not success:
                raise Exception("Could not fill date field")
            page.screenshot(path='screenshots/fill_3.png')
            
            # Submit
            print("  ⚡ Submitting form...")
            page.click('button[type="submit"]', timeout=5000)
            page.wait_for_timeout(2000)
            
            # Check for success banner
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
            print(f"🖼️ Debug screenshots in: screenshots/")
        
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
