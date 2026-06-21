import json
import re
import shutil
from pathlib import Path
from librarian.utils.ui import (
    print_header, print_warning, print_success, print_muted,
    print_panel, confirm_action, console, INDIGO, WARNING, SUCCESS,
    print_diff,
)
from librarian.utils.token_tracker import tracker
from librarian.orchestrator.core import read_librarian_md, build_system_prompt
from librarian.orchestrator.router import get_response
from librarian.memory.retriever import retrieve
from librarian.memory import capsule, decision_log
from librarian.actions.file_ops import read_file, write_file, edit_file
from librarian.actions.shell_ops import run_command
from librarian.actions.safety import classify_action, RiskLevel
from librarian.skills.loader import build_skill_context

DO_SYSTEM_PROMPT = """You are Librarian, a CLI coding agent. Respond ONLY with a JSON plan.

ACTION TYPES:

1. create_file — for new files:
{"type":"create_file","file":"path","description":"what","content":"COMPLETE file"}

2. edit_file — modify existing files:
{"type":"edit_file","file":"path","description":"what","old_code":"EXACT text","new_code":"replacement"}

3. delete_file — remove files/folders:
{"type":"delete_file","file":"path","description":"why"}

4. shell_command — run terminal commands:
{"type":"shell_command","command":"cmd","description":"what"}

RESPONSE FORMAT:
{"reasoning":"approach","actions":[...]}

RULES:
- content in create_file MUST be the complete, working, FULL file — never a stub, placeholder, or comment
- NEVER generate content like "// add code here" or empty tags — always write real, functional code
- For web projects (HTML/CSS/JS): prefer a single index.html with inline <style> and <script>
- old_code in edit_file must match the file EXACTLY including whitespace — if unsure, use create_file instead
- Return ONLY valid JSON — no markdown fences, no explanation
- Keep file contents under 200 lines to avoid truncation
"""


def _parse_plan(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    raw = raw.replace("\\'", "'")

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    last_bracket = raw.rfind("]")
    if last_bracket == -1:
        raise json.JSONDecodeError("No JSON array found", raw, 0)
    truncated = raw[:last_bracket] + "]}"

    try:
        return json.loads(truncated)
    except json.JSONDecodeError:
        raise json.JSONDecodeError("Could not parse plan", raw, 0)


def _format_chunks(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        meta = c["metadata"]
        parts.append(f"--- {meta['file_path']}:{meta.get('start_line', '?')}-{meta.get('end_line', '?')} ---\n{c['content']}")
    return "\n\n".join(parts)


def _show_plan(plan: dict, task: str):
    print_panel(
        f"  task      {task}\n\n  reasoning {plan.get('reasoning', '—')}",
        title="execution plan",
    )
    from rich.table import Table
    table = Table(show_header=True, header_style=f"bold {INDIGO}")
    table.add_column("#", width=3)
    table.add_column("type", width=14)
    table.add_column("description", width=40)
    for i, action in enumerate(plan.get("actions", []), 1):
        table.add_row(
            str(i),
            action.get("type", "?"),
            action.get("description", "—"),
        )
    console.print(table)


def _preview_action(action: dict):
    action_type = action.get("type")
    if action_type == "edit_file":
        path = Path(action["file"])
        if path.exists():
            content = read_file(action["file"])
            if action["old_code"] in content:
                new_content = content.replace(action["old_code"], action["new_code"], 1)
                print_diff(action["file"], content, new_content)
    elif action_type == "create_file":
        path = Path(action["file"])
        if path.exists():
            old_content = read_file(action["file"])
            print_diff(action["file"], old_content, action.get("content", ""))
        else:
            console.print(f"\n[bold {INDIGO}]new file:[/bold {INDIGO}] {action['file']}")
            from rich.syntax import Syntax
            content = action.get("content", "")
            syntax = Syntax(content, Path(action["file"]).suffix.lstrip(".") or "text", theme="monokai")
            console.print(Panel(syntax, border_style=INDIGO, padding=(0, 1)))


def _execute_action(action: dict) -> dict:
    action_type = action.get("type")
    if action_type == "edit_file":
        path = Path(action["file"])
        if not path.exists():
            raise FileNotFoundError(f"File not found: {action['file']}")
        content = read_file(action["file"])
        if action["old_code"] not in content:
            raise ValueError(f"old_code not found in {action['file']} — file may have changed")
        edit_file(action["file"], action["old_code"], action["new_code"])
        return {"type": "edit_file", "file": action["file"], "status": "done"}
    elif action_type == "create_file":
        path = Path(action["file"])
        if path.exists() and path.stat().st_size > 0:
            content = action.get("content", "")
            if not content or len(content.strip()) < 20:
                raise ValueError(f"Refusing to overwrite {action['file']} with empty/stub content")
        write_file(action["file"], action["content"])
        return {"type": "create_file", "file": action["file"], "status": "done"}
    elif action_type == "delete_file":
        target = Path(action["file"])
        if target.is_dir():
            shutil.rmtree(target)
        elif target.is_file():
            target.unlink()
        else:
            raise FileNotFoundError(f"Not found: {action['file']}")
        return {"type": "delete_file", "file": action["file"], "status": "done"}
    elif action_type == "shell_command":
        cmd = action["command"]
        if cmd.strip().startswith("rm "):
            import re as _re
            paths = _re.findall(r"(?:^|\s)(\S+)", cmd.replace("rm ", "", 1))
            for p in paths:
                p = p.lstrip("-").lstrip("r").lstrip("f").strip()
                target = Path(p)
                if target.is_dir():
                    shutil.rmtree(target)
                elif target.is_file():
                    target.unlink()
            return {"type": "shell_command", "command": cmd, "status": "done"}
        code, out, err = run_command(cmd)
        return {"type": "shell_command", "command": cmd, "status": "done" if code == 0 else f"exit {code}"}
    return {"type": action_type, "status": "unknown"}


def _check_api_keys():
    from librarian.utils.config import GROQ_API_KEY, OPENROUTER_API_KEY
    if not GROQ_API_KEY and not OPENROUTER_API_KEY:
        print_warning("no API keys found")
        print_muted("  set at least one API key in .env file:")
        print_muted("")
        print_muted("  GROQ_API_KEY=gsk_...        (free at console.groq.com)")
        print_muted("  OPENROUTER_API_KEY=sk-or-... (free at openrouter.ai)")
        print_muted("")
        return False
    return True


def run(task: str):
    if not Path(".librarian").exists():
        print_header("librarian do")
        print_warning("project not initialised — run 'librarian init' first")
        return

    if not _check_api_keys():
        return

    print_header("librarian do")

    chunks = retrieve(task, n_results=7)
    conventions = read_librarian_md()
    skill_ctx = build_skill_context()

    parts = [f"Project conventions:\n{conventions}"]
    if skill_ctx:
        parts.append(f"Domain best practices:\n{skill_ctx}")
    if chunks:
        context = _format_chunks(chunks)
        parts.append(f"Relevant code:\n{context}")
    parts.append(f"Task: {task}")
    prompt = "\n\n".join(parts)

    try:
        raw_response, provider, tokens = get_response(DO_SYSTEM_PROMPT, prompt)
        tracker.add(provider, tokens)
        plan = _parse_plan(raw_response)
    except json.JSONDecodeError:
        print_warning("LLM returned invalid JSON — try rephrasing your task")
        return
    except Exception as e:
        print_warning(f"error: {e}")
        return

    _show_plan(plan, task)

    print_muted("\n  preview of changes:")
    for action in plan.get("actions", []):
        _preview_action(action)

    if not confirm_action("proceed with execution?"):
        print_muted("  cancelled")
        return

    results = []
    files_changed = []
    for action in plan.get("actions", []):
        risk_text = action.get("description", "") + " " + action.get("command", "") + " " + action.get("file", "")
        if action.get("type") in ("delete_file",):
            risk_text += " delete"
        risk = classify_action(risk_text)
        if risk == RiskLevel.CONFIRM:
            if not confirm_action(f"execute: {action.get('description', '?')}"):
                print_muted(f"  skipped: {action.get('description', '?')}")
                continue
        try:
            result = _execute_action(action)
            results.append(result)
            if "file" in action:
                files_changed.append(action["file"])
            print_success(f"done: {action.get('description', '?')}")
        except Exception as e:
            print_warning(f"failed: {action.get('description', '?')} — {e}")

    decision_log.append({
        "command": "do",
        "task": task,
        "actions_taken": results,
        "files_changed": files_changed,
        "llm_provider": provider,
        "tokens_used": tokens,
        "reasoning": plan.get("reasoning", ""),
    })

    if results:
        capsule.create(task, plan.get("reasoning", ""), files_changed)
        print_success(f"{len(results)} actions completed")
    print_muted(f"  tokens: {tokens}  provider: {provider}")
