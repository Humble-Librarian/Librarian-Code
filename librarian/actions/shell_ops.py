def run_command(cmd: str, cwd: str = None):
    raise NotImplementedError


def git_stage(files: list[str]) -> bool:
    raise NotImplementedError


def git_commit(message: str) -> bool:
    raise NotImplementedError


def git_push() -> bool:
    raise NotImplementedError


def git_status() -> str:
    raise NotImplementedError
