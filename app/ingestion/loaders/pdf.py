import logfire
from pypdf import PdfReader

def parse_pdf(file_path: str):
    """
    Extract text from a PDF locally using pypdf.
    Falls back to pdfplumber for pages that yield no text (e.g. image-heavy pages).

    Args:
        file_path (str): The path to the PDF file.
    """
    with logfire.span("📄 PDF Parsing (local)", filename=file_path):
        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            logfire.info(f"📄 PDF file has {total_pages} pages.")

            text_parts: list[str] = []
            blank_pages: list[int] = []

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text:
                    text_parts.append(page_text)
                else:
                    blank_pages.append(i + 1)  # Store 1-based page number
            
            # Fallback: use pdfplumber for any pages pypdf returned blank
            if blank_pages:
                logfire.info(f"pypdf returned blank pages {blank_pages} - retrying with pdfplumber!")
                try:
                    import pdfplumber
                    with pdfplumber.open(file_path) as pdf:
                        for page_number in blank_pages:
                            page = pdf.pages[page_number - 1]
                            fallback_text = page.extract_text() or ""
                            if fallback_text.strip():
                                text_parts.append(fallback_text)
                except Exception as plumber_error:
                    logfire.warning(f"pdfplumber fallback failed: {plumber_error}")

            full_text = "\n".join(text_parts)

            if not full_text.strip():
                logfire.warning(f"No text extracted from {file_path}. File may be fully image-based 😂")
            else:
                logfire.info(f"Extracted {len(full_text)} characters from {file_path}")
            
            return full_text
        
        except Exception as e:
            logfire.error(f"❌ Error parsing PDF file {file_path}: {e}")
            raise e