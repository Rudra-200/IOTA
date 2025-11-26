import re
import json
import sqlite3
from pathlib import Path
import tiktoken

# Optional imports (only needed if running ingestion)
try:
    from pdfminer.high_level import extract_text
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    print("Warning: PDF libraries not found. Ingestion will not work.")

from .config import settings

class DocumentProcessor:
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.max_tokens = 1000
        self.overlap = 200

    def clean_text(self, text: str) -> str:
        """Standardizes whitespace and removes common artifacts."""
        text = re.sub(r'\n\s*\d+\s*\n', ' ', text) # Remove page numbers
        text = re.sub(r'\s+', ' ', text) # Normalize whitespace
        return text.strip()

    def extract_text(self, file_path: str) -> str:
        """Hybrid extraction: PDFMiner -> OCR Fallback"""
        try:
            # Method 1: Fast Text Extraction
            text = extract_text(file_path)
            if len(text.strip()) > 100:
                return self.clean_text(text)
        except:
            pass
        
        # Method 2: OCR Fallback (Slower but robust)
        try:
            images = convert_from_path(file_path, dpi=200)
            text = " ".join([pytesseract.image_to_string(img) for img in images])
            return self.clean_text(text)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return ""

    def extract_case_metadata(self, text: str) -> dict:
        """
        Heuristic to extract Case Title (Petitioner vs Respondent) 
        from the first 1500 characters.
        """
        first_page = text[:1500]
        lines = first_page.split(' ') # text is already single-spaced by clean_text
        
        # Since clean_text removes newlines, we look for patterns in the continuous stream
        # or we might need to adjust clean_text to preserve some structure for this step.
        # Ideally, extraction happens BEFORE aggressive cleaning, but let's try a regex approach.
        
        # Pattern: "Name ... versus ... Name"
        # This regex looks for the keyword "versus" or "vs" with words around it
        match = re.search(r'([A-Z][a-z\s\.]+?)\s+(?:VERSUS|VS\.?|V\.)\s+([A-Z][a-z\s\.]+)', first_page, re.IGNORECASE)
        
        title = "Unknown Case"
        if match:
            petitioner = match.group(1).strip()[-50:] # Take last 50 chars to avoid capturing garbage
            respondent = match.group(2).strip()[:50]  # Take first 50 chars
            title = f"{petitioner} vs {respondent}"
            
            # Cleanup title
            title = re.sub(r'\s+', ' ', title).strip()
        
        # Generate a safe ID
        safe_id = re.sub(r'[^a-zA-Z0-9]', '_', title)[:100]
        
        return {
            "doc_id": safe_id,
            "title": title
        }

    def chunk_text(self, text: str, meta: dict):
        """Generates chunks with overlap"""
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)
        
        chunks = []
        for i in range(0, total_tokens, self.max_tokens - self.overlap):
            chunk_tokens = tokens[i : i + self.max_tokens]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunks.append({
                "text": chunk_text,
                "meta": meta
            })
        return chunks