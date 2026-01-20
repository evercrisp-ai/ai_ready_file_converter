"""
PDF converter for Human-to-AI Format Converter.
Extracts text and tables from PDF documents using pdfplumber.
"""

from pathlib import Path
import pdfplumber
from .base import BaseConverter


class PdfConverter(BaseConverter):
    """Converter for PDF documents."""
    
    def _get_file_type(self) -> str:
        return "pdf_document"
    
    def _extract_content(self) -> dict:
        """Extract content from PDF document."""
        content = {
            "text": "",
            "pages": [],
            "tables": []
        }
        
        full_text_parts = []
        
        with pdfplumber.open(self.file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text from page
                page_text = page.extract_text() or ""
                
                page_data = {
                    "page_number": page_num,
                    "text": page_text,
                    "tables": []
                }
                
                if page_text:
                    full_text_parts.append(page_text)
                
                # Extract tables from page
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 0:
                        # First row as headers
                        headers = [str(cell) if cell else "" for cell in table[0]]
                        rows = []
                        for row in table:
                            rows.append([str(cell) if cell else "" for cell in row])
                        
                        table_data = {
                            "page": page_num,
                            "headers": headers,
                            "rows": rows
                        }
                        page_data["tables"].append(table_data)
                        content["tables"].append(table_data)
                
                content["pages"].append(page_data)
            
            # Update metadata
            self._metadata = {
                "page_count": len(pdf.pages),
                "table_count": len(content["tables"]),
                "word_count": len(" ".join(full_text_parts).split())
            }
        
        content["text"] = "\n\n".join(full_text_parts)
        
        return content
    
    def _format_as_markdown(self, content: dict) -> str:
        """Format PDF content as Markdown."""
        md_parts = []
        
        for page in content["pages"]:
            # Page header
            md_parts.append(f"## Page {page['page_number']}")
            md_parts.append("")
            
            # Page text
            if page["text"]:
                # Clean up the text - preserve paragraphs
                text = page["text"].strip()
                md_parts.append(text)
            
            # Page tables
            for table in page["tables"]:
                if table["rows"]:
                    md_parts.append("")
                    
                    # Header row
                    if table["headers"]:
                        md_parts.append("| " + " | ".join(table["headers"]) + " |")
                        md_parts.append("| " + " | ".join(["---"] * len(table["headers"])) + " |")
                    
                    # Data rows
                    start_idx = 1 if table["headers"] else 0
                    for row in table["rows"][start_idx:]:
                        md_parts.append("| " + " | ".join(row) + " |")
                    
                    md_parts.append("")
            
            md_parts.append("")
            md_parts.append("---")
            md_parts.append("")
        
        return "\n".join(md_parts)
