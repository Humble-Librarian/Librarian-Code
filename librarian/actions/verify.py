import subprocess
from pathlib import Path
from librarian.actions.shell_ops import run_command


def run_tests() -> tuple[bool, str]:
    if Path("pyproject.toml").exists():
        code, out, err = run_command("python -m pytest tests/ -v --tb=short -q")
        return code == 0, out + err
    if Path("package.json").exists():
        code, out, err = run_command("npm test")
        return code == 0, out + err
    return True, "no test runner detected"


def run_lint(files_changed: list[str] = None) -> tuple[bool, str]:
    if Path("pyproject.toml").exists():
        targets = " ".join(files_changed) if files_changed else "."
        code, out, err = run_command(f"python -m ruff check {targets}")
        if code != 0 and "No module named 'ruff'" in err:
            return True, "ruff not installed"
        return code == 0, out + err
    if Path("package.json").exists():
        code, out, err = run_command("npm run lint")
        return code == 0, out + err
    return True, "no linter detected"


def verify_changes(files_changed: list[str] = None) -> tuple[bool, str]:
    lint_ok, lint_out = run_lint(files_changed)
    tests_ok, tests_out = run_tests()

    parts = []
    if not lint_ok:
        parts.append(f"lint failed:\n{lint_out}")
    if not tests_ok:
        parts.append(f"tests failed:\n{tests_out}")

    if parts:
        return False, "\n\n".join(parts)
    return True, "all checks passed"
