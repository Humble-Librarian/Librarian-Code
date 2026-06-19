import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = ".librarian/decisions.jsonl"


def append(entry: dict):
    entry["id"] = str(uuid.uuid4())
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def get_last(n: int = 5) -> list[dict]:
    path = Path(LOG_FILE)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    entries = [json.loads(line) for line in lines if line.strip()]
    return entries[-n:]


def mark_undone(entry_id: str):
    path = Path(LOG_FILE)
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    updated = []
    for line in lines:
        entry = json.loads(line)
        if entry.get("id") == entry_id:
            entry["outcome"] = "undone"
        updated.append(json.dumps(entry))
    path.write_text("\n".join(updated) + "\n", encoding="utf-8")
