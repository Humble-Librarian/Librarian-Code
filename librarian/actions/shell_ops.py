import subprocess
from librarian.actions.safety import classify_action, RiskLevel, request_confirm


def run_command(cmd: str, cwd: str = None) -> tuple[int, str, str]:
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout, result.stderr


def git_stage(files: list[str]) -> bool:
    cmd = f"git add {' '.join(files)}"
    code, _, err = run_command(cmd)
    if code != 0:
        raise RuntimeError(f"git add failed: {err}")
    return True


def git_commit(message: str) -> bool:
    cmd = f'git commit -m "{message}"'
    code, _, err = run_command(cmd)
    if code != 0:
        raise RuntimeError(f"git commit failed: {err}")
    return True


def git_push() -> bool:
    risk = classify_action("git push")
    if risk == RiskLevel.CONFIRM:
        if not request_confirm("push to remote?"):
            return False
    code, _, err = run_command("git push")
    if code != 0:
        raise RuntimeError(f"git push failed: {err}")
    return True


def git_status() -> str:
    code, out, err = run_command("git status --short")
    if code != 0:
        return err
    return out.strip()
