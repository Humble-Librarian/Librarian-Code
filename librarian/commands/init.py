import os
from pathlib import Path
from librarian.utils.ui import print_header, print_success, print_warning, print_muted
from librarian.memory.indexer import index_project


def _detect_languages() -> list[str]:
    from librarian.actions.file_ops import list_files
    files = list_files(".", None)
    exts = set()
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext:
            exts.add(ext)
    lang_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".jsx": "React JSX", ".tsx": "React TSX", ".go": "Go",
        ".rs": "Rust", ".java": "Java", ".rb": "Ruby",
        ".md": "Markdown", ".txt": "Text",
    }
    return [lang_map.get(e, e) for e in sorted(exts) if e in lang_map]


def _detect_package_manager() -> str:
    if Path("pyproject.toml").exists():
        return "uv / pip"
    if Path("setup.py").exists():
        return "pip"
    if Path("package.json").exists():
        return "npm"
    if Path("Cargo.toml").exists():
        return "cargo"
    return "unknown"


def _generate_librarian_md(languages: list[str], package_manager: str):
    content = f"""# LIBRARIAN.md — project conventions

## language
{', '.join(languages) if languages else 'unknown'}

## package manager
{package_manager}

## style
- follow existing code conventions in the project
- use type hints where applicable
- keep functions focused and small

## structure
(add project structure notes here)

## things to avoid
- importing specific adapters directly (always use base.LLMAdapter)
- hardcoding API keys
- deleting files without confirmation

## notes
(add project-specific notes here — librarian reads this on every run)
"""
    Path("LIBRARIAN.md").write_text(content, encoding="utf-8")


def run():
    print_header("initialising project")

    cwd = os.getcwd()
    basename = os.path.basename(cwd)
    if not basename or len(basename) < 2:
        print_warning("cannot initialise from a root or drive directory")
        print_muted("  cd into your project folder first, then run: librarian init")
        return

    librarian_dir = Path(".librarian")
    if librarian_dir.exists():
        print_warning(".librarian/ already exists — re-indexing")

    librarian_dir.mkdir(exist_ok=True)

    if not Path("LIBRARIAN.md").exists():
        languages = _detect_languages()
        pkg = _detect_package_manager()
        _generate_librarian_md(languages, pkg)
        print_success("LIBRARIAN.md created")
    else:
        print_muted("  LIBRARIAN.md already exists — skipping")

    try:
        meta = index_project()
        print_success(f"{meta['file_count']} files, {meta['chunk_count']} chunks")
    except Exception as e:
        print_warning(f"indexing error: {e}")
        return

    print_success(".librarian/ initialised")
    print_muted("\n  ready. run: librarian ask \"what does this project do?\"")
