from pypdf import PdfReader
import docx
from typing import Dict, List
import re

class ResumeParser:
    """Service to extract text and information from resume files"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    @staticmethod
    def parse_resume(file_path: str, file_extension: str) -> str:
        """Parse resume based on file type"""
        if file_extension.lower() == '.pdf':
            return ResumeParser.extract_text_from_pdf(file_path)
        elif file_extension.lower() in ['.docx', '.doc']:
            return ResumeParser.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    @staticmethod
    def extract_email(text: str) -> str:
        """Extract email from resume text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""
    
    @staticmethod
    def extract_phone(text: str) -> str:
        """Extract phone number from resume text"""
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        matches = re.findall(phone_pattern, text)
        return matches[0] if matches else ""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)\@\+]', '', text)
        return text.strip()
