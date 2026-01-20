"""
Word document (.docx) converter for AI-Ready File Converter.
Extracts text, headings, paragraphs, and tables from Word documents.
"""

from pathlib import Path
from docx import Document
from docx.table import Table
from .base import BaseConverter


class DocxConverter(BaseConverter):
    """Converter for Microsoft Word documents."""
    
    def _get_file_type(self) -> str:
        return "word_document"
    
    def _extract_content(self) -> dict:
        """Extract content from Word document."""
        doc = Document(self.file_path)
        
        content = {
            "text": "",
            "paragraphs": [],
            "tables": [],
            "headings": []
        }
        
        full_text_parts = []
        
        for element in doc.element.body:
            # Check if it's a paragraph
            if element.tag.endswith('p'):
                for para in doc.paragraphs:
                    if para._element == element:
                        text = para.text.strip()
                        if text:
                            try:
                                style_name = para.style.name if para.style else ""
                            except AttributeError:
                                style_name = ""
                            
                            # Check if it's a heading
                            if style_name.startswith('Heading'):
                                try:
                                    level = int(style_name.replace('Heading ', ''))
                                except ValueError:
                                    level = 1
                                content["headings"].append({
                                    "level": level,
                                    "text": text
                                })
                            
                            content["paragraphs"].append({
                                "text": text,
                                "style": style_name
                            })
                            full_text_parts.append(text)
                        break
            
            # Check if it's a table
            elif element.tag.endswith('tbl'):
                for table in doc.tables:
                    if table._element == element:
                        try:
                            table_data = self._extract_table(table)
                            content["tables"].append(table_data)
                        except Exception:
                            pass  # Skip tables that fail to extract
                        break
        
        content["text"] = "\n\n".join(full_text_parts)
        
        # Update metadata
        self._metadata = {
            "paragraph_count": len(content["paragraphs"]),
            "table_count": len(content["tables"]),
            "heading_count": len(content["headings"]),
            "word_count": len(content["text"].split())
        }
        
        return content
    
    def _extract_table(self, table: Table) -> dict:
        """Extract data from a Word table."""
        rows = []
        headers = []
        
        for i, row in enumerate(table.rows):
            row_data = [cell.text.strip() for cell in row.cells]
            if i == 0:
                headers = row_data
            rows.append(row_data)
        
        return {
            "headers": headers,
            "rows": rows
        }
    
    def _format_as_markdown(self, content: dict) -> str:
        """Format Word document content as Markdown."""
        md_parts = []
        
        # Process paragraphs with proper heading formatting
        for para in content["paragraphs"]:
            text = para["text"]
            style = para.get("style", "")
            
            if style.startswith("Heading"):
                try:
                    level = int(style.replace("Heading ", ""))
                    level = min(level, 6)  # Markdown supports h1-h6
                except ValueError:
                    level = 1
                md_parts.append(f"{'#' * level} {text}")
            else:
                md_parts.append(text)
        
        # Add tables
        for i, table in enumerate(content["tables"]):
            if table["rows"]:
                md_parts.append("")  # Empty line before table
                
                # Header row
                if table["headers"]:
                    md_parts.append("| " + " | ".join(table["headers"]) + " |")
                    md_parts.append("| " + " | ".join(["---"] * len(table["headers"])) + " |")
                
                # Data rows (skip first if it was headers)
                start_idx = 1 if table["headers"] else 0
                for row in table["rows"][start_idx:]:
                    md_parts.append("| " + " | ".join(row) + " |")
                
                md_parts.append("")  # Empty line after table
        
        return "\n\n".join(md_parts)
