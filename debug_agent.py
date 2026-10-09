#!/usr/bin/env python3
"""
Autonomous Invoice Processor Agent - Debug Version
"""

import os
import json
import time
from playwright.sync_api import sync_playwright

def debug_page():
    """Debug: see what Playwright actually loads"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page()
        
        print("🔍 Loading page...")
        page.goto("http://localhost:5001", timeout=20000, wait_until="load")
        print("✅ Page loaded")
        
        # Get full HTML content
        html = page.content()
        print(f"\n📄 Page HTML length: {len(html)} chars")
        
        # Check if form exists in raw HTML
        if '<form' in html.lower():
            print("✅ 'form' tag found in HTML")
        else:
            print("❌ 'form' tag NOT found in HTML")
        
        # Check input fields
        inputs = page.locator('input')
        count = inputs.count()
        print(f"🔍 Found {count} input elements on page")
        
        # List all input attributes
        for i in range(count):
            input_elem = inputs.nth(i)
            name = input_elem.get_attribute('name')
            type_ = input_elem.get_attribute('type')
            id_ = input_elem.get_attribute('id')
            print(f"   Input {i+1}: name={name}, type={type_}, id={id_}")
        
        # Screenshot
        page.screenshot(path='screenshots/debug_page.png')
        print("📷 Saved: screenshots/debug_page.png")
        
        browser.close()

if __name__ == "__main__":
    debug_page()
