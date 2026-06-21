import json
import uuid
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

CAPSULE_FILE = ".librarian/capsules.json"
ARCHIVE_FILE = ".librarian/archive/archived_capsules.json"


def _load() -> list[dict]:
    path = Path(CAPSULE_FILE)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _save(capsules: list[dict]):
    Path(CAPSULE_FILE).write_text(json.dumps(capsules, indent=2), encoding="utf-8")


def create(task: str, reasoning: str, files_changed: list[str] = None):
    capsules = _load()
    capsule = {
        "id": str(uuid.uuid4()),
        "project_id": hashlib.sha256(os.getcwd().encode()).hexdigest()[:16],
        "file": (files_changed or [""])[0],
        "decision": task,
        "reason": reasoning,
        "confidence": 0.5,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "embed_text": f"{task} because {reasoning}",
        "outcome": "approved",
    }
    capsules.append(capsule)
    _save(capsules)
    return capsule


def approve(capsule_id: str):
    capsules = _load()
    for c in capsules:
        if c["id"] == capsule_id:
            c["outcome"] = "approved"
            c["confidence"] = min(c["confidence"] * 1.15, 1.0)
            break
    _save(capsules)


def undo(capsule_id: str):
    capsules = _load()
    for c in capsules:
        if c["id"] == capsule_id:
            c["outcome"] = "undone"
            c["confidence"] *= 0.6
            break
    _save(capsules)
    _archive_low_confidence()


def decay():
    capsules = _load()
    now = datetime.now(timezone.utc)
    for c in capsules:
        if c["outcome"] == "ignored":
            ts = datetime.fromisoformat(c["timestamp"])
            days = (now - ts).days
            c["confidence"] *= 0.98 ** days
    _save(capsules)
    _archive_low_confidence()


def _archive_low_confidence():
    capsules = _load()
    keep = []
    archive = []
    for c in capsules:
        if c["confidence"] < 0.4:
            archive.append(c)
        else:
            keep.append(c)
    if archive:
        _save(keep)
        Path(".librarian/archive").mkdir(parents=True, exist_ok=True)
        existing = []
        if Path(ARCHIVE_FILE).exists():
            existing = json.loads(Path(ARCHIVE_FILE).read_text(encoding="utf-8"))
        existing.extend(archive)
        Path(ARCHIVE_FILE).write_text(json.dumps(existing, indent=2), encoding="utf-8")


def get_all() -> list[dict]:
    return _load()
