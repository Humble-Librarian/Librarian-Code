from pathlib import Path
from librarian.utils.ui import print_header, print_warning, print_panel, print_muted
from librarian.utils.token_tracker import tracker
from librarian.orchestrator.core import ask as ask_llm
from librarian.memory.retriever import retrieve


def run(task: str):
    if not Path(".librarian").exists():
        print_header("librarian ask")
        print_warning("project not initialised — run 'librarian init' first")
        return

    print_header("librarian ask")

    try:
        chunks = retrieve(task, n_results=5)
        sources = []
        for c in chunks:
            meta = c["metadata"]
            sources.append(f"{meta['file_path']}:{meta.get('start_line', '?')}-{meta.get('end_line', '?')}")

        response, provider, tokens = ask_llm(task)
        tracker.add(provider, tokens)
        print_panel(response, title="answer")
        if sources:
            print_muted(f"  sources   {', '.join(sources[:3])}")
        print_muted(f"  tokens    {tokens}  provider  {provider}")
    except Exception as e:
        print_warning(f"error: {e}")
