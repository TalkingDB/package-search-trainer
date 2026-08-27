DEFAULT_CHUNK_SIZE_WORDS = 200
DEFAULT_OVERLAP_WORDS = 20


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE_WORDS,
    overlap: int = DEFAULT_OVERLAP_WORDS,
) -> list[str]:
    """Split text into overlapping word-count chunks, for embedding text
    that exceeds a single embedding call's practical input size.

    Word-count based rather than character based, since embedding model
    limits are token based and word count is a much closer proxy for
    token count than character count is.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0:
        raise ValueError("overlap must not be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    if not words:
        return []

    stride = chunk_size - overlap
    chunks = []
    for start in range(0, len(words), stride):
        chunk_words = words[start : start + chunk_size]
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break

    return chunks
