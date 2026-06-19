from pathlib import Path
from librarian.orchestrator.router import get_response


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
"""


def read_librarian_md() -> str:
    path = Path("LIBRARIAN.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "No project conventions file found."


def ask(question: str) -> tuple[str, str, int]:
    conventions = read_librarian_md()
    system = build_system_prompt(conventions)
    return get_response(system, question)
