import os
import json
from datetime import datetime, timezone
from pathlib import Path
from librarian.utils.ui import print_header, print_panel, print_muted, INDIGO, SUCCESS
from librarian.utils.token_tracker import tracker


def run():
    project_name = os.path.basename(os.getcwd())
    librarian_dir = Path(".librarian")
    meta_file = librarian_dir / "index_meta.json"
    decisions_file = librarian_dir / "decisions.jsonl"
    capsules_file = librarian_dir / "capsules.json"

    if not librarian_dir.exists():
        print_header("librarian status")
        print_muted(f"  project      {project_name}")
        print_muted("  indexed      not yet (run librarian init)")
        print_muted("  memory       0 capsules")
        print_muted("  last action  —")
        print_muted("  tokens       0")
        print_muted("  providers    groq (primary) · openrouter (fallback)")
        return

    indexed = "not yet"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        indexed = f"{meta.get('file_count', '?')} files · {meta.get('chunk_count', '?')} chunks"

    capsule_count = 0
    avg_confidence = 0
    if capsules_file.exists():
        capsules = json.loads(capsules_file.read_text())
        capsule_count = len(capsules)
        if capsules:
            avg_confidence = sum(c.get("confidence", 0) for c in capsules) / len(capsules)

    decision_count = 0
    last_action = "—"
    if decisions_file.exists():
        lines = decisions_file.read_text().strip().splitlines()
        decision_count = len(lines)
        if lines:
            last = json.loads(lines[-1])
            task = last.get("task", "—")
            ts = last.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(ts)
                diff = datetime.now(timezone.utc) - dt
                hours = int(diff.total_seconds() // 3600)
                if hours < 1:
                    last_action = f"{task} (just now)"
                elif hours < 24:
                    last_action = f"{task} ({hours}h ago)"
                else:
                    last_action = f"{task} ({hours // 24}d ago)"
            except Exception:
                last_action = task

    print_header("librarian status")
    content = (
        f"  project      {project_name}\n"
        f"  indexed      {indexed}\n"
        f"  memory       {capsule_count} capsules · avg confidence {avg_confidence:.2f}\n"
        f"  last action  {last_action}\n"
        f"  tokens       {tracker.total()} this session\n"
        f"  providers    groq (primary) · openrouter (fallback)\n"
        f"  log entries  {decision_count}"
    )
    print_panel(content, title="project")
