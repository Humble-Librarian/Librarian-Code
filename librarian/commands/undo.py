import json
from pathlib import Path
from librarian.utils.ui import (
    print_header, print_warning, print_success, print_muted, confirm_action,
)
from librarian.memory.decision_log import get_last, mark_undone
from librarian.memory import capsule
from librarian.actions.file_ops import read_file, write_file


def _undo_edit_file(action: dict):
    path = action.get("file")
    new_code = action.get("new_code", "")
    old_code = action.get("old_code", "")
    if not path or not old_code:
        return False
    try:
        content = read_file(path)
        if new_code in content:
            content = content.replace(new_code, old_code, 1)
            write_file(path, content)
            return True
    except Exception:
        pass
    return False


def _undo_create_file(action: dict):
    path = action.get("file")
    if not path:
        return False
    p = Path(path)
    if p.exists():
        if confirm_action(f"delete {path}?"):
            p.unlink()
            return True
    return False


def run():
    if not Path(".librarian").exists():
        print_header("librarian undo")
        print_warning("project not initialised — run 'librarian init' first")
        return

    print_header("librarian undo")

    entries = get_last(10)
    undone = [e for e in entries if e.get("outcome") != "undone"]
    if not undone:
        print_muted("  nothing to undo")
        return

    last = undone[-1]
    task = last.get("task", "—")
    print_muted(f"  last action: {task}")

    if not confirm_action(f"undo '{task}'?"):
        print_muted("  cancelled")
        return

    reverted = 0
    for action in last.get("actions_taken", []):
        action_type = action.get("type")
        if action_type == "edit_file":
            if _undo_edit_file(action):
                reverted += 1
                print_success(f"reverted: {action.get('file', '?')}")
        elif action_type == "create_file":
            if _undo_create_file(action):
                reverted += 1
                print_success(f"deleted: {action.get('file', '?')}")
        elif action_type == "shell_command":
            print_warning(f"cannot auto-undo shell command: {action.get('command', '?')}")

    mark_undone(last["id"])

    capsules = capsule.get_all()
    for c in capsules:
        if c.get("decision") == task:
            capsule.undo(c["id"])
            print_muted(f"  capsule confidence updated: {c['confidence']:.2f} → {c['confidence'] * 0.6:.2f}")
            break

    print_success(f"undo complete — {reverted} actions reverted")
