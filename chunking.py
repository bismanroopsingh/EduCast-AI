import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_chunk_text(
    text,
    similarity_threshold=0.45,
    min_chunk_size=5,
    max_chunk_size=12
):
    """
    Semantic Chunking V2

    Parameters:
        text (str)
        similarity_threshold (float)
        min_chunk_size (int)
        max_chunk_size (int)

    Returns:
        list of semantic chunks
    """

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= min_chunk_size:
        return [" ".join(sentences)]

    # Generate sentence embeddings
    embeddings = model.encode(sentences)

    chunks = []

    current_chunk = [sentences[0]]
    current_embeddings = [embeddings[0]]

    for i in range(1, len(sentences)):

        sentence_embedding = embeddings[i]

        # Average embedding of current chunk
        chunk_centroid = np.mean(
            current_embeddings,
            axis=0
        ).reshape(1, -1)

        similarity = cosine_similarity(
            chunk_centroid,
            sentence_embedding.reshape(1, -1)
        )[0][0]

        # Decide whether to split
        should_split = (
            similarity < similarity_threshold
            and len(current_chunk) >= min_chunk_size
        )

        # Force split if chunk gets too large
        force_split = (
            len(current_chunk) >= max_chunk_size
        )

        if should_split or force_split:

            chunks.append(
                " ".join(current_chunk)
            )

            current_chunk = [sentences[i]]
            current_embeddings = [sentence_embedding]

        else:

            current_chunk.append(sentences[i])
            current_embeddings.append(sentence_embedding)

    # Add remaining chunk
    if current_chunk:
        chunks.append(
            " ".join(current_chunk)
        )

    return chunks
