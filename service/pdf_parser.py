import pdfplumber


def extract_text_from_pdf(path):
    """Extract all text from a PDF file."""
    with pdfplumber.open(path) as pdf:
        full_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    return full_text