import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from librarian.actions.file_ops import list_files
from librarian.memory.chunker import chunk_file
from librarian.utils.config import CHROMA_PERSIST_DIR, EMBED_MODEL
from librarian.utils.ui import spinner, print_success, print_muted

CHUNK_EXTENSIONS = [
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".md", ".txt", ".yaml", ".yml", ".toml",
    ".json", ".html", ".css", ".sh", ".sql",
]

META_FILE = ".librarian/index_meta.json"


def index_project():
    model = SentenceTransformer(EMBED_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    project_name = os.path.basename(os.getcwd())
    collection = client.get_or_create_collection(name=project_name)

    files = list_files(".", CHUNK_EXTENSIONS)
    all_chunks = []
    for f in files:
        all_chunks.extend(chunk_file(f))

    existing = collection.get()
    existing_ids = set(existing["ids"]) if existing["ids"] else set()

    to_add = []
    for chunk in all_chunks:
        chunk_id = f"{chunk['metadata']['file_path']}:{chunk['metadata']['start_line']}"
        if chunk_id in existing_ids:
            continue
        to_add.append((chunk_id, chunk))

    with spinner("indexing files...") as prog:
        task = prog.add_task("indexing", total=len(to_add))
        batch_size = 100
        for i in range(0, len(to_add), batch_size):
            batch = to_add[i:i + batch_size]
            ids = [c[0] for c in batch]
            documents = [c[1]["content"] for c in batch]
            metadatas = [c[1]["metadata"] for c in batch]
            embeddings = model.encode(documents).tolist()
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
            prog.update(task, advance=len(batch))

    meta = {
        "project": project_name,
        "file_count": len(files),
        "chunk_count": collection.count(),
        "indexed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    }
    Path(".librarian").mkdir(exist_ok=True)
    Path(META_FILE).write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print_success(f"{len(files)} files, {collection.count()} chunks indexed")
    return meta
