import os
import chromadb
from sentence_transformers import SentenceTransformer
from librarian.utils.config import CHROMA_PERSIST_DIR, EMBED_MODEL
from librarian.memory.indexer import _sanitize_collection_name

_model = None
_client = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _client


def retrieve(query: str, n_results: int = 5) -> list[dict]:
    model = _get_model()
    client = _get_client()
    project_name = _sanitize_collection_name(os.path.basename(os.getcwd()))

    try:
        collection = client.get_collection(name=project_name)
    except Exception:
        return []

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    if not results.get("documents") or not results["documents"][0]:
        return []

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist > 2.5:
            continue
        chunks.append({
            "content": doc,
            "metadata": meta,
            "distance": dist,
        })

    if chunks and sum(c["distance"] for c in chunks) / len(chunks) > 2.0:
        return []

    return chunks
