IGNORED_PATHS = [".git", "node_modules", "__pycache__", ".librarian", "venv", ".env"]


def read_file(path: str) -> str:
    raise NotImplementedError


def write_file(path: str, content: str) -> bool:
    raise NotImplementedError


def edit_file(path: str, old: str, new: str) -> bool:
    raise NotImplementedError


def list_files(directory: str, extensions: list = None) -> list[str]:
    raise NotImplementedError


def get_ignored_paths() -> list[str]:
    return IGNORED_PATHS
