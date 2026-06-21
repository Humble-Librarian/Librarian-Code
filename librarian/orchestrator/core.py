from pathlib import Path
from librarian.orchestrator.router import get_response
from librarian.memory.retriever import retrieve
from librarian.memory import session
from librarian.skills.loader import build_skill_context


def build_system_prompt(project_conventions: str, skill_context: str = "") -> str:
    parts = [
        "You are Librarian, a CLI coding agent with memory of this project.",
        f"Project conventions:\n{project_conventions}",
    ]
    if skill_context:
        parts.append(f"Domain-specific best practices:\n{skill_context}")
    parts.append("""Rules:
- Always explain what you are about to do before doing it
- Never delete files without explicit confirmation
- Prefer editing existing code over rewriting from scratch
- When uncertain, ask rather than assume
- Be concise and direct in your answers
- Cite source files when referencing code (e.g. "in auth.py line 42")
""")
    return "\n\n".join(parts)


def read_librarian_md() -> str:
    path = Path("LIBRARIAN.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "No project conventions file found."


def ask(question: str) -> tuple[str, str, int]:
    conventions = read_librarian_md()
    skill_ctx = build_skill_context()
    system = build_system_prompt(conventions, skill_ctx)

    chunks = retrieve(question, n_results=5)
    context = ""
    if chunks:
        parts = []
        for c in chunks:
            meta = c["metadata"]
            parts.append(f"--- {meta['file_path']}:{meta.get('start_line', '?')}-{meta.get('end_line', '?')} ---\n{c['content']}")
        context = "\n\n".join(parts)

    history = session.format_history(max_messages=6)
    prompt_parts = []
    if context:
        prompt_parts.append(f"Relevant code context:\n{context}")
    if history:
        prompt_parts.append(f"Previous conversation:\n{history}")
    prompt_parts.append(f"Question: {question}")
    prompt = "\n\n".join(prompt_parts)

    session.add_message("user", question)
    response, provider, tokens = get_response(system, prompt)
    session.add_message("assistant", response)
    return response, provider, tokens
