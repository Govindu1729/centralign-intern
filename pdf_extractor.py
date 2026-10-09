"""
PDF Text Extractor - Multi-engine support
"""

import os


def extract_text_from_pdf(filepath):
    """
    Extract text from PDF file.
    Tries multiple backends in order of preference.
    
    Returns:
        str: Extracted text content
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        RuntimeError: If no PDF backend available
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"PDF file not found: {filepath}")
    
    # Try PyMuPDF (fitz) first - fastest
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)
    except ImportError:
        pass
    
    # Try pdfplumber as fallback
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)
    except ImportError:
        pass
    
    # Try PyPDF2 as last resort
    try:
        import PyPDF2
        text_parts = []
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)
    except ImportError:
        pass
    
    raise RuntimeError(
        "No PDF library available. Install one of:\n"
        "  pip install pymupdf    (fastest)\n"
        "  pip install pdfplumber\n"
        "  pip install PyPDF2"
    )
