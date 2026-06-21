"""Skill loader — auto-detects project type and loads relevant conventions."""

import os
import json
import functools
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "bundled"


@functools.lru_cache(maxsize=1)
def _detect_project_type() -> list[str]:
    cwd = Path.cwd()
    detected = []

    indicators = {
        "web-dev": {
            "files": ["index.html", "*.html"],
            "extensions": [".html", ".htm", ".css", ".scss", ".less"],
            "keywords": ["html", "css", "javascript", "website", "webpage", "landing page"],
        },
        "python": {
            "files": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "uv.lock"],
            "extensions": [".py", ".pyi", ".ipynb"],
            "keywords": ["python", "pip", "uv", "poetry", "pytest", "django", "flask", "fastapi"],
        },
        "react": {
            "files": ["next.config.ts", "next.config.js", "next.config.mjs"],
            "extensions": [".tsx", ".jsx"],
            "keywords": ["react", "next.js", "nextjs", "remix", "vite"],
            "package_deps": ["react", "next"],
        },
        "api-design": {
            "files": ["routes.py", "models.py", "schemas.py"],
            "extensions": [],
            "keywords": ["api", "endpoint", "rest", "graphql", "server", "backend", "fastapi", "express", "flask"],
        },
    }

    html_files = list(cwd.rglob("*.html"))
    py_files = list(cwd.rglob("*.py"))
    tsx_files = list(cwd.rglob("*.tsx")) + list(cwd.rglob("*.jsx"))

    for skill_name, config in indicators.items():
        score = 0

        for pattern in config["files"]:
            if list(cwd.glob(pattern)):
                score += 3

        for ext in config["extensions"]:
            if skill_name == "web-dev" and ext == ".html" and len(html_files) > 0:
                score += min(len(html_files), 3)
            elif skill_name == "python" and ext == ".py" and len(py_files) > 0:
                score += min(len(py_files), 3)
            elif skill_name in ("react",) and ext in (".tsx", ".jsx") and len(tsx_files) > 0:
                score += min(len(tsx_files), 3)

        if skill_name == "react":
            pkg_json = cwd / "package.json"
            if pkg_json.exists():
                try:
                    pkg = json.loads(pkg_json.read_text())
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                    for dep in config.get("package_deps", []):
                        if dep in deps:
                            score += 5
                except Exception:
                    pass

        if skill_name == "python":
            if (cwd / "pyproject.toml").exists():
                score += 5
            if any(cwd.rglob("fastapi")) or any((cwd / f).exists() for f in ["main.py", "app.py"]):
                score += 2

        if score >= 2:
            detected.append((skill_name, score))

    detected.sort(key=lambda x: x[1], reverse=True)
    return [name for name, _ in detected]


def load_skill(skill_name: str) -> str | None:
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.exists():
        return None
    conventions_file = skill_dir / "conventions.md"
    if conventions_file.exists():
        return conventions_file.read_text(encoding="utf-8")
    return None


def get_relevant_skills() -> list[str]:
    return _detect_project_type()


def build_skill_context() -> str:
    skills = get_relevant_skills()
    if not skills:
        return ""

    parts = []
    for skill_name in skills:
        content = load_skill(skill_name)
        if content:
            parts.append(f"## {skill_name} conventions\n{content}")

    return "\n\n".join(parts)
