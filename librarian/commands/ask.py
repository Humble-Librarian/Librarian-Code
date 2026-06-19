from pathlib import Path
from librarian.utils.ui import print_header, print_warning, print_panel, print_muted
from librarian.utils.token_tracker import tracker
from librarian.orchestrator.core import ask as ask_llm


def run(task: str):
    if not Path(".librarian").exists():
        print_header("librarian ask")
        print_warning("project not initialised — run 'librarian init' first")
        return

    print_header("librarian ask")

    try:
        response, provider, tokens = ask_llm(task)
        tracker.add(provider, tokens)
        print_panel(response, title="answer")
        print_muted(f"  tokens    {tokens}  provider  {provider}")
    except Exception as e:
        print_warning(f"error: {e}")
