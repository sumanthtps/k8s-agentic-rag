from bs4 import BeautifulSoup
import logfire

def parse_html(file_path: str):
    """
    Parses an HTML file and extracts the text content.

    Args:
        file_path (str): The path to the HTML file.
    """
    with logfire.span("📄 HTML Parsing", filename=file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
            
            soup = BeautifulSoup(content, "html.parser")

            # 1. Remove junk(script, style, and Metadata)
            for script in soup(["script", "style", "meta", "noscript"]):
                script.extract()
            
            # 2. Extract text
            text = soup.get_text(separator="\n")

            # 3. Clean whitespace (Collapse multiple newlines)
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            cleaned_text = "\n".join(chunk for chunk in chunks if chunk)

            return cleaned_text
        except Exception as e:
            logfire.error(f"❌ Error parsing HTML file {file_path}: {e}")
            raise e