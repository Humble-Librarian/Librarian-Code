from pathlib import Path
from librarian.utils.ui import print_header, print_warning


def run():
    if not Path(".librarian").exists():
        print_header("librarian why")
        print_warning("project not initialised — run 'librarian init' first")
        return
    print_header("librarian why")
    print("  (decision history coming in phase 5)")
