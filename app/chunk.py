def chunk_text(text: str, chunk_size: int = 900, chunk_overlap: int = 150):
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = end - chunk_overlap
        if start < 0:
            start = 0
    return chunks

from sentence_transformers import CrossEncoder

def rerank_chunks(query: str, chunks: list[dict], top_k: int = 5):
    """
    Rerank chunks based on their relevance to the query using a cross-encoder model.

    Args:
        query (str): The query string to compare against.
        chunks (list[dict]): A list of chunks, each chunk is a dictionary containing at least a 'text' key.
        top_k (int): The number of top relevant chunks to return.

    Returns:
        list[dict]: The top_k chunks sorted by relevance score in descending order.
    """
    # Initialize the cross-encoder model for scoring relevance
    model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    # Prepare pairs of (query, chunk_text) for scoring
    pairs = [(query, chunk['text']) for chunk in chunks]

    # Compute relevance scores for each pair
    scores = model.predict(pairs)

    # Combine chunks with their scores
    scored_chunks = list(zip(chunks, scores))

    # Sort chunks by score in descending order (higher score means more relevant)
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    # Select the top_k chunks
    top_chunks = [chunk for chunk, score in scored_chunks[:top_k]]

    return top_chunks
