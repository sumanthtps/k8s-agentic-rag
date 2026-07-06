from typing import List
import logfire

def chunk_text(text: str, chunk_size: int = 1500) -> List[str]:
    """
    Simple semantic-ish chunker that splits by paragraphs.
    Ensures chunks do not exceed the specified size.

    Args:
        text (str): The input text to be chunked.
        chunk_size (int): The maximum size of each chunk. Default is 1500 characters.

    Returns:
        List[str]: A list of text chunks.
    """
    with logfire.span("✂️ Text Chunking", text_length=len(text)):
        if not text.strip():
            logfire.warning("⚠️ Input text is empty. Returning an empty list of chunks.")
            return []
        
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
    valid_chunks = [chunk for chunk in chunks if chunk.strip()]
    logfire.info(f"✅ Generated {len(valid_chunks)} chunks")
    return valid_chunks