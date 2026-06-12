def paragraph_chunk_text(text, min_length=50):
    """
    Split text into paragraph-based chunks.

    Parameters:
        text (str): Extracted PDF text
        min_length (int): Minimum characters required for a chunk

    Returns:
        list: List of paragraph chunks
    """

    # Split using blank lines
    paragraphs = text.split("\n\n")

    chunks = []

    for para in paragraphs:
        para = para.strip()

        # Ignore very short paragraphs
        if len(para) >= min_length:
            chunks.append(para)

    return chunks