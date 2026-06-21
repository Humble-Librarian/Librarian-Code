from pathlib import Path
from typing import Optional
from librarian.utils.ui import print_header, print_warning, print_success, print_muted, print_panel
from librarian.actions.shell_ops import run_command, git_stage, git_commit, git_push
from librarian.actions.safety import classify_action, RiskLevel


def _check_api_keys():
    return True


def commit(message: str, files: Optional[list[str]] = None):
    if not Path(".git").exists():
        print_header("librarian commit")
        print_warning("not a git repository")
        return

    print_header("librarian commit")

    if files:
        git_stage(files)
    else:
        code, out, err = run_command("git add -A")
        if code != 0:
            print_warning(f"git add failed: {err}")
            return

    try:
        git_commit(message)
        print_success(f"committed: {message}")
    except Exception as e:
        print_warning(f"commit failed: {e}")


def push():
    if not Path(".git").exists():
        print_header("librarian push")
        print_warning("not a git repository")
        return

    print_header("librarian push")

    code, out, err = run_command("git status --short")
    if out.strip():
        print_warning("uncommitted changes — commit first")
        print_muted(out)
        return

    try:
        git_push()
        print_success("pushed to remote")
    except Exception as e:
        print_warning(f"push failed: {e}")


def diff(file: Optional[str] = None):
    if not Path(".git").exists():
        print_header("librarian diff")
        print_warning("not a git repository")
        return

    print_header("librarian diff")

    cmd = "git diff"
    if file:
        cmd += f" -- {file}"

    code, out, err = run_command(cmd)
    if code != 0:
        print_warning(f"git diff failed: {err}")
        return

    if not out.strip():
        print_muted("  no changes")
        return

    from rich.syntax import Syntax
    from rich.panel import Panel
    from librarian.utils.ui import console, INDIGO

    syntax = Syntax(out, "diff", theme="monokai")
    console.print(Panel(syntax, title="diff", border_style=INDIGO, padding=(0, 1)))


def status():
    if not Path(".git").exists():
        print_header("librarian status")
        print_warning("not a git repository")
        return

    print_header("librarian git status")

    code, out, err = run_command("git status")
    if code != 0:
        print_warning(f"git status failed: {err}")
        return

    print_panel(out, title="git status")
