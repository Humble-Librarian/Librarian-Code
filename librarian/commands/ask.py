from pathlib import Path
from librarian.utils.ui import print_header, print_warning, print_panel, print_muted
from librarian.utils.token_tracker import tracker
from librarian.orchestrator.core import ask as ask_llm
from librarian.memory.retriever import retrieve


def _check_api_keys():
    from librarian.utils.config import GROQ_API_KEY, OPENROUTER_API_KEY
    if not GROQ_API_KEY and not OPENROUTER_API_KEY:
        print_warning("no API keys found")
        print_muted("  set at least one API key in .env file:")
        print_muted("")
        print_muted("  GROQ_API_KEY=gsk_...        (free at console.groq.com)")
        print_muted("  OPENROUTER_API_KEY=sk-or-... (free at openrouter.ai)")
        print_muted("")
        return False
    return True


def run(task: str):
    if not Path(".librarian").exists():
        print_header("librarian ask")
        print_warning("project not initialised — run 'librarian init' first")
        return

    if not _check_api_keys():
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
