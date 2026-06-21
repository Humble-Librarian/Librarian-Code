import os
import chromadb
from sentence_transformers import SentenceTransformer
from librarian.utils.config import CHROMA_PERSIST_DIR, EMBED_MODEL
from librarian.memory.indexer import _sanitize_collection_name
from librarian.memory import capsule

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


def retrieve(query: str, n_results: int = 5, file_filter: str = None) -> list[dict]:
    model = _get_model()
    client = _get_client()
    project_name = _sanitize_collection_name(os.path.basename(os.getcwd()))

    try:
        collection = client.get_collection(name=project_name)
    except Exception:
        return []

    query_embedding = model.encode([query]).tolist()

    where_filter = None
    if file_filter:
        where_filter = {"file_path": {"$contains": file_filter}}

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
        where=where_filter,
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
        file_conf = capsule.get_file_confidence(meta.get("file_path", ""))
        adjusted_dist = dist / file_conf
        chunks.append({
            "content": doc,
            "metadata": meta,
            "distance": adjusted_dist,
        })

    if chunks and sum(c["distance"] for c in chunks) / len(chunks) > 2.0:
        return []

    return chunks
