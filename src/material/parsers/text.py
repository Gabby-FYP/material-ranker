import pdfplumber
from src.material.parsers.base import BasePDFParser


class Parser(BasePDFParser):
    
    def parse(self) -> str:
        """Parse the given PDF file and extract text content."""

        content = ''

        # Open the PDF file and extract text from each page.
        with pdfplumber.open(self.file) as pdf:
            for page in pdf.pages:
                content += page.extract_text(layout=False)

        return content
