import os
from pathlib import Path

IGNORED_PATHS = [".git", "node_modules", "__pycache__", ".librarian", "venv", ".env"]


def read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return Path(path).read_text(encoding="latin-1")


def write_file(path: str, content: str) -> bool:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")
    return True


def edit_file(path: str, old: str, new: str) -> bool:
    content = read_file(path)
    count = content.count(old)
    if count == 0:
        raise ValueError(f"String not found in {path}")
    if count > 1:
        raise ValueError(f"Ambiguous edit: string appears {count} times in {path}")
    content = content.replace(old, new, 1)
    write_file(path, content)
    return True


def list_files(directory: str, extensions: list[str] = None) -> list[str]:
    ignored = get_ignored_paths()
    results = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignored]
        for f in files:
            if extensions:
                ext = os.path.splitext(f)[1].lower()
                if ext not in extensions:
                    continue
            results.append(os.path.join(root, f))
    return sorted(results)


def get_ignored_paths() -> list[str]:
    return IGNORED_PATHS
