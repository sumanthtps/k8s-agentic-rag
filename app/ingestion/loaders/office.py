import logfire
from unstructured.partition.auto import partition

def parse_office(file_path: str):
    """
    Parses an Office file (e.g., Word, Excel, PowerPoint) and extracts the text content.

    Args:
        file_path (str): The path to the Office file.
    """
    with logfire.span("📄 Office Document Parsing", filename=file_path):
        try:
            # Unstructured library's partition function automatically detects the file type and extracts text accordingly
            # Partition: It reads the Office file at file_path
            # Auto-detects the format (.docx, .pptx, etc.)
            # Parses the document into structured elements (paragraphs, headings, slides, text blocks, etc.)
            # Returns a list of parsed elements
            elements = partition(file_path)
            full_text = "\n".join([str(element) for element in elements])

            if not full_text:
                logfire.warning(f"⚠️ No text content found in Office file {file_path}")
            else:
                logfire.info(f"✅ Successfully parsed {len(full_text)} characters from Office file {file_path}")
            return full_text
        except Exception as e:
            logfire.error(f"❌ Error parsing Office file {file_path}: {e}")
            raise e