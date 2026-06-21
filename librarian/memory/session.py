import json
from pathlib import Path
from datetime import datetime, timezone

SESSION_FILE = ".librarian/session.json"


def _load() -> dict:
    path = Path(SESSION_FILE)
    if not path.exists():
        return {"history": [], "created_at": datetime.now(timezone.utc).isoformat()}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(session: dict):
    Path(SESSION_FILE).write_text(json.dumps(session, indent=2), encoding="utf-8")


def add_message(role: str, content: str):
    session = _load()
    session["history"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    if len(session["history"]) > 20:
        session["history"] = session["history"][-20:]
    _save(session)


def get_history(max_messages: int = 10) -> list[dict]:
    session = _load()
    return session["history"][-max_messages:]


def clear_history():
    _save({"history": [], "created_at": datetime.now(timezone.utc).isoformat()})


def format_history(max_messages: int = 10) -> str:
    history = get_history(max_messages)
    if not history:
        return ""
    parts = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "assistant"
        parts.append(f"[{role}]: {msg['content'][:500]}")
    return "\n\n".join(parts)
