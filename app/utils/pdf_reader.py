"""PDF reading and text extraction utilities."""

import logging
from typing import Optional
from pypdf import PdfReader
from io import BytesIO

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Processes PDF files and extracts text content."""
    
    @staticmethod
    async def extract_text_from_pdf(pdf_content: bytes) -> str:
        """
        Extract text from PDF file content.
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Extracted text from all pages
            
        Raises:
            ValueError: If PDF processing fails
        """
        try:
            # Create a BytesIO object from the PDF content
            pdf_file = BytesIO(pdf_content)
            
            # Create PDF reader
            pdf_reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            if not text_content:
                raise ValueError("No text could be extracted from the PDF")
            
            full_text = "\n\n".join(text_content)
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            
            return full_text
            
        except Exception as e:
            logger.error(f"PDF processing error: {e}")
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned = '\n'.join(lines)
        
        return cleaned
    
    @staticmethod
    async def process_pdf(pdf_content: bytes) -> str:
        """
        Complete PDF processing pipeline.
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Cleaned, extracted text
        """
        raw_text = await PDFProcessor.extract_text_from_pdf(pdf_content)
        cleaned_text = PDFProcessor.clean_text(raw_text)
        
        return cleaned_text
