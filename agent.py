#!/usr/bin/env python3
"""
Autonomous Invoice Processor Agent
Uses ReAct loop to find, extract, and log invoices.
"""

import os
import json
import time
from playwright.sync_api import sync_playwright

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

def log_invoice_to_portal(vendor, amount, due_date, url="http://localhost:5000"):
    """Use Playwright to submit invoice data to the Flask portal."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to portal
        page.goto(url)
        
        # Fill form
        page.fill('input[name="vendor"]', vendor)
        page.fill('input[name="amount"]', str(amount))
        page.fill('input[name="due_date"]', due_date)
        
        # Submit
        page.click('button[type="submit"]')
        
        # Wait for and verify success banner
        page.wait_for_selector('#success-banner')
        success_visible = page.is_visible('#success-banner')
        
        browser.close()
        return success_visible

def agent_loop(prompt):
    """Main agent loop: Find -> Extract -> Act -> Verify"""
    print(f"🤖 Agent received: {prompt}")
    
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
    success = log_invoice_to_portal(
        vendor=data["vendor"],
        amount=data["amount"],
        due_date=data["due_date"]
    )
    
    if success:
        print("✅ Invoice logged successfully!")
    else:
        print("❌ Verification failed. Check portal.")
    
    return success

if __name__ == "__main__":
    # Default prompt for sprint demo
    prompt = "Find the latest invoice from Acme Corp, extract the amount and due date, and log it into the internal system."
    agent_loop(prompt)
