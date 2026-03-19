"""
File Processor - Handle PDF and image attachments
"""

import base64
import logging
from typing import Dict, Any, List
from pathlib import Path
import PyPDF2
import pdfplumber
from PIL import Image

logger = logging.getLogger(__name__)


class FileProcessor:
    """Process PDF and image files attached to tasks"""
    
    def process_files(self, files: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Process list of base64-encoded files
        
        Args:
            files: List of file dictionaries with filename, content_base64, mime_type
            
        Returns:
            List of processed files with extracted data
        """
        processed = []
        
        for file_data in files:
            try:
                processed_file = self._process_single_file(file_data)
                processed.append(processed_file)
            except Exception as e:
                logger.error(f"Failed to process file {file_data.get('filename')}: {str(e)}")
                processed.append({
                    "filename": file_data.get("filename"),
                    "error": str(e)
                })
        
        return processed
    
    def _process_single_file(self, file_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Process a single file
        
        Args:
            file_data: File dictionary with filename, content_base64, mime_type
            
        Returns:
            Processed file with extracted data
        """
        filename = file_data["filename"]
        content_base64 = file_data["content_base64"]
        mime_type = file_data["mime_type"]
        
        # Decode base64 content
        content = base64.b64decode(content_base64)
        
        # Save to temp file
        temp_path = Path(f"/tmp/{filename}")
        temp_path.write_bytes(content)
        
        result = {
            "filename": filename,
            "mime_type": mime_type,
            "path": str(temp_path),
            "size": len(content)
        }
        
        # Process based on mime type
        if mime_type == "application/pdf":
            result.update(self._process_pdf(temp_path))
        elif mime_type.startswith("image/"):
            result.update(self._process_image(temp_path))
        
        return result
    
    def _process_pdf(self, path: Path) -> Dict[str, Any]:
        """
        Extract text and data from PDF
        
        Args:
            path: Path to PDF file
            
        Returns:
            Extracted data
        """
        try:
            # Try pdfplumber first (better for tables and structured data)
            with pdfplumber.open(path) as pdf:
                text = ""
                tables = []
                
                for page in pdf.pages:
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
                
                result = {
                    "extracted_text": text.strip(),
                    "page_count": len(pdf.pages)
                }
                
                if tables:
                    result["tables"] = tables
                    result["extracted_data"] = self._parse_tables(tables)
                
                return result
                
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {str(e)}")
            
            # Fallback to PyPDF2
            try:
                with open(path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    
                    return {
                        "extracted_text": text.strip(),
                        "page_count": len(reader.pages)
                    }
            except Exception as e2:
                logger.error(f"PDF processing failed: {str(e2)}")
                return {"error": f"PDF processing failed: {str(e2)}"}
    
    def _process_image(self, path: Path) -> Dict[str, Any]:
        """
        Process image file
        
        Args:
            path: Path to image file
            
        Returns:
            Image metadata
        """
        try:
            with Image.open(path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode
                }
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return {"error": f"Image processing failed: {str(e)}"}
    
    def _parse_tables(self, tables: List[List[List[str]]]) -> Dict[str, Any]:
        """
        Parse tables to extract structured data (invoices, expenses, etc.)
        
        Args:
            tables: List of tables from PDF
            
        Returns:
            Parsed structured data
        """
        parsed = {
            "line_items": [],
            "totals": {},
            "metadata": {}
        }
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # Try to identify table type and parse accordingly
            headers = [str(cell).lower() if cell else "" for cell in table[0]]
            
            # Look for invoice line items
            if any(keyword in " ".join(headers) for keyword in ["product", "description", "amount", "quantity", "price"]):
                for row in table[1:]:
                    if row and any(row):
                        item = {}
                        for i, header in enumerate(headers):
                            if i < len(row) and row[i]:
                                item[header] = row[i]
                        if item:
                            parsed["line_items"].append(item)
            
            # Look for totals
            for row in table:
                if row and len(row) >= 2:
                    key = str(row[0]).lower() if row[0] else ""
                    value = str(row[1]) if len(row) > 1 and row[1] else ""
                    
                    if any(keyword in key for keyword in ["total", "sum", "amount", "subtotal"]):
                        parsed["totals"][key] = value
        
        return parsed

# Made with Bob
