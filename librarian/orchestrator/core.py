from pathlib import Path
from librarian.orchestrator.router import get_response
from librarian.memory.retriever import retrieve


def build_system_prompt(project_conventions: str) -> str:
    return f"""You are Librarian, a CLI coding agent with memory of this project.

Project conventions:
{project_conventions}

Rules:
- Always explain what you are about to do before doing it
- Never delete files without explicit confirmation
- Prefer editing existing code over rewriting from scratch
- When uncertain, ask rather than assume
- Be concise and direct in your answers
- Cite source files when referencing code (e.g. "in auth.py line 42")
"""


def read_librarian_md() -> str:
    path = Path("LIBRARIAN.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "No project conventions file found."


def ask(question: str) -> tuple[str, str, int]:
    conventions = read_librarian_md()
    system = build_system_prompt(conventions)

    chunks = retrieve(question, n_results=5)
    context = ""
    if chunks:
        parts = []
        for c in chunks:
            meta = c["metadata"]
            parts.append(f"--- {meta['file_path']}:{meta.get('start_line', '?')}-{meta.get('end_line', '?')} ---\n{c['content']}")
        context = "\n\n".join(parts)

    prompt = f"Relevant code context:\n{context}\n\nQuestion: {question}" if context else question
    return get_response(system, prompt)
