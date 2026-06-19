from pathlib import Path
from librarian.utils.ui import print_header, print_warning


def run(task: str):
    if not Path(".librarian").exists():
        print_header("librarian do")
        print_warning("project not initialised — run 'librarian init' first")
        return
    print_header("librarian do")
    print(f"  task: {task}")
    print("  (agent loop coming in phase 4)")
