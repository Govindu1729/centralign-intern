"""
LLM Service - Configurable extraction interface
Supports multiple providers via environment variables
"""

import os
import json
from typing import Dict, Any, Optional


def call_llm(prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract structured data from text using LLM.
    
    Providers (set via environment variable, LLM_PROVIDER):
    - openai: Uses OpenAI API
    - ollama: Uses local Ollama server
    - anthropic: Uses Anthropic API
    - mock: Returns demo data (for testing only)
    
    Args:
        prompt: Full prompt with text and instructions
        model: Override model name
        
    Returns:
        Dict with extracted fields (vendor, amount, due_date)
    """
    provider = os.getenv("LLM_PROVIDER", "mock")
    api_key = os.getenv("LLM_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL", "")
    
    # Fallback to mock if no provider configured
    if provider == "mock" and not api_key:
        return _mock_extraction()
    
    if provider == "openai":
        return _call_openai(prompt, api_key, model)
    elif provider == "ollama":
        return _call_ollama(prompt, base_url, model)
    elif provider == "anthropic":
        return _call_anthropic(prompt, api_key, model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _mock_extraction() -> Dict[str, Any]:
    """Return demo data for testing purposes only."""
    return {
        "vendor": "Acme Corp",
        "amount": 1500.00,
        "due_date": "2026-10-20"
    }


def _call_openai(prompt: str, api_key: str, model: Optional[str]) -> Dict[str, Any]:
    """Call OpenAI API with JSON mode for structured output."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract invoice data as JSON with fields: vendor (string), amount (number), due_date (YYYY-MM-DD string)."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        # Validate and normalize
        return _normalize_invoice_data(data)
    except Exception as e:
        raise RuntimeError(f"OpenAI API failed: {e}")


def _call_ollama(prompt: str, base_url: str, model: Optional[str]) -> Dict[str, Any]:
    """Call local Ollama server."""
    try:
        import requests
        response = requests.post(
            f"{base_url}/api/generate" or "http://localhost:11434/api/generate",
            json={
                "model": model or "llama3.2",
                "prompt": f"""You are a helpful assistant. Extract invoice data and respond with ONLY a JSON object with these fields:\n- vendor: string (company name)\n- amount: number (total amount)\n- due_date: string (YYYY-MM-DD format)\n\nInvoice text: {prompt}""",
                "format": "json"
            }
        )
        response.raise_for_status()
        data = json.loads(response.json()["response"])
        return _normalize_invoice_data(data)
    except Exception as e:
        raise RuntimeError(f"Ollama API failed: {e}")


def _call_anthropic(prompt: str, api_key: str, model: Optional[str]) -> Dict[str, Any]:
    """Call Anthropic API with JSON mode."""
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model or "claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(response.content[0].text)
        return _normalize_invoice_data(data)
    except Exception as e:
        raise RuntimeError(f"Anthropic API failed: {e}")


def _normalize_invoice_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize extraction results to expected schema."""
    return {
        "vendor": data.get("vendor", data.get("company", "Unknown")),
        "amount": float(data.get("amount", data.get("total", 0))),
        "due_date": data.get("due_date", data.get("due", "2026-10-20"))
    }


def extract_invoice_data(text: str) -> Dict[str, Any]:
    """
    Public interface for invoice data extraction.
    
    Args:
        text: Raw invoice text content
        
    Returns:
        Dict with vendor, amount, due_date
    """
    prompt = f"""Extract the following fields from this invoice text:
- vendor: the company name sending the invoice
- amount: the total amount in dollars (numeric only)
- due_date: the payment due date in YYYY-MM-DD format

Invoice text:
{text}

Return JSON only with fields: vendor, amount, due_date"""
    
    return call_llm(prompt)
