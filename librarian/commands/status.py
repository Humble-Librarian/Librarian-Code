import os
import json
from pathlib import Path
from librarian.utils.ui import print_header, print_panel, print_muted


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
        print_muted("  providers    groq (primary) · openrouter (fallback)")
        return

    indexed = "not yet"
    chunk_count = 0
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        indexed = f"{meta.get('file_count', '?')} files, {meta.get('chunk_count', '?')} chunks"

    capsule_count = 0
    if capsules_file.exists():
        capsules = json.loads(capsules_file.read_text())
        capsule_count = len(capsules)

    decision_count = 0
    last_action = "—"
    if decisions_file.exists():
        lines = decisions_file.read_text().strip().splitlines()
        decision_count = len(lines)
        if lines:
            last = json.loads(lines[-1])
            last_action = last.get("task", "—")

    print_header("librarian status")
    content = (
        f"  project      {project_name}\n"
        f"  indexed      {indexed}\n"
        f"  memory       {capsule_count} capsules\n"
        f"  last action  {last_action}\n"
        f"  log entries  {decision_count}\n"
        f"  providers    groq (primary) · openrouter (fallback)"
    )
    print_panel(content, title="project")
