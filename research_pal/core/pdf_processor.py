"""
PDF Processor for ResearchPal - handles extraction and chunking of text from PDFs.
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple

from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTFigure, LTTextBox

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Processes PDF files to extract text and metadata."""
    
    def __init__(self, chunk_size: int = 8000, chunk_overlap: int = 200):
        """
        Initialize the PDF processor.
        
        Args:
            chunk_size: Maximum size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_and_chunk(self, filepath: str) -> Dict[str, Any]:
        """
        Extract text and metadata from a PDF file and chunk it.
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            Dictionary with extracted content:
                - metadata: PDF metadata
                - chunks: List of text chunks
                - highlighted_text: List of highlighted sections (if any)
                - figures_tables: List of detected figures/tables (if any)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"PDF file not found: {filepath}")
        
        logger.info(f"Processing PDF: {filepath}")
        
        # Extract text and metadata
        raw_text = extract_text(filepath)
        metadata = self._extract_metadata(filepath, raw_text)
        
        # Process figures and tables (basic detection)
        figures_tables = self._detect_figures_tables(filepath)
        
        # Process any highlighted text
        highlighted_text = self._extract_highlighted_text(filepath)
        
        # Chunk the text
        chunks = self._chunk_text(raw_text)
        
        return {
            "metadata": metadata,
            "chunks": chunks,
            "highlighted_text": highlighted_text,
            "figures_tables": figures_tables,
            "chunk_count": len(chunks)
        }
    
    def _extract_metadata(self, filepath: str, text: str) -> Dict[str, str]:
        """Extract metadata from the PDF file and content."""
        # Basic metadata from filename
        filename = os.path.basename(filepath)
        base_name = os.path.splitext(filename)[0]
        
        # Try to extract title and authors from the first page
        title = base_name
        author = ""
        
        # First few hundred characters likely contain title/authors
        first_page = text[:2000]
        
        # Simple title extraction - first line of reasonable length
        lines = first_page.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            # Title candidates are typically 5+ words but not too long
            if 20 < len(line) < 200 and len(line.split()) >= 3:
                title = line
                break
        
        # Simple author extraction - look for patterns
        author_patterns = [
            r"(?:authors?|by)[:;]\s*([\w\s,\.]+)",
            r"([\w\s]+(?:,\s*[\w\s]+)+)\s*(?:\n|$)",
        ]
        
        for pattern in author_patterns:
            author_match = re.search(pattern, first_page, re.IGNORECASE)
            if author_match:
                author = author_match.group(1).strip()
                break
        
        # Extract date - look for year
        date = ""
        year_match = re.search(r"(19|20)\d{2}", first_page)
        if year_match:
            date = year_match.group(0)
        
        # Extract abstract if present
        abstract = ""
        abstract_match = re.search(
            r"abstract[:\.\n](.*?)(?:introduction|keywords|$)",
            text[:5000], 
            re.IGNORECASE | re.DOTALL
        )
        if abstract_match:
            abstract = abstract_match.group(1).strip()
        
        return {
            "title": title,
            "author": author,
            "date": date,
            "abstract": abstract,
            "filename": filename,
            "filepath": filepath
        }
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            # Determine end of chunk
            end = min(start + self.chunk_size, len(text))
            
            # If we're not at the end, try to find a good break point
            if end < len(text):
                # Look for paragraph break
                next_para = text.find('\n\n', end - 100, end + 100)
                if next_para != -1 and next_para < end + 100:
                    end = next_para
                else:
                    # Look for sentence end
                    next_sentence = text.find('. ', end - 100, end + 100)
                    if next_sentence != -1 and next_sentence < end + 100:
                        end = next_sentence + 1  # Include the period
            
            # Add the chunk
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move start position for next chunk (with overlap)
            start = end - self.chunk_overlap if end < len(text) else len(text)
        
        return chunks
    
    def _detect_figures_tables(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Detect figures and tables in the PDF.
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            List of dictionaries with figure/table information
        """
        figures_tables = []
        
        try:
            # Basic detection of figures - this is a simplified approach
            # A production system would use more sophisticated methods
            page_num = 0
            for page_layout in extract_pages(filepath):
                page_num += 1
                
                for element in page_layout:
                    # Check for figures
                    if isinstance(element, LTFigure):
                        figures_tables.append({
                            "type": "figure",
                            "page": page_num,
                            "bbox": (element.x0, element.y0, element.x1, element.y1),
                            "size": (element.width, element.height)
                        })
                    
                    # Basic table detection (looking for text containing "Table")
                    if isinstance(element, LTTextBox):
                        text = element.get_text().strip()
                        if text.lower().startswith("table") or "table " in text.lower():
                            figures_tables.append({
                                "type": "table",
                                "page": page_num,
                                "text": text,
                                "bbox": (element.x0, element.y0, element.x1, element.y1)
                            })
        except Exception as e:
            logger.warning(f"Error detecting figures/tables: {e}")
        
        return figures_tables
    
    def _extract_highlighted_text(self, filepath: str) -> List[str]:
        """
        Extract highlighted text from the PDF.
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            List of highlighted text sections
        """
        highlighted_sections = []
        
        try:
            # Basic detection of highlighted text - this is a simplified approach
            # A production system would use more sophisticated methods
            page_num = 0
            for page_layout in extract_pages(filepath):
                page_num += 1
                
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        highlighted_chars = []
                        
                        for text_line in element:
                            for char in text_line:
                                if isinstance(char, LTChar):
                                    # Check for highlighting (non-black text color or background color)
                                    # This is a heuristic and may need adjustment for different PDFs
                                    if hasattr(char, 'ncs') and char.ncs and char.ncs.name != 'DeviceGray':
                                        highlighted_chars.append(char.get_text())
                        
                        if highlighted_chars:
                            highlighted_text = ''.join(highlighted_chars)
                            if len(highlighted_text.strip()) > 5:  # Ignore very short highlights
                                highlighted_sections.append({
                                    "text": highlighted_text,
                                    "page": page_num
                                })
        except Exception as e:
            logger.warning(f"Error extracting highlighted text: {e}")
        
        return highlighted_sections