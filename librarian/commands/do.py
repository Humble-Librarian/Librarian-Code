import json
import re
import shutil
from pathlib import Path
from librarian.utils.ui import (
    print_header, print_warning, print_success, print_muted,
    print_panel, confirm_action, console, INDIGO, WARNING, SUCCESS,
)
from librarian.utils.token_tracker import tracker
from librarian.orchestrator.core import read_librarian_md, build_system_prompt
from librarian.orchestrator.router import get_response
from librarian.memory.retriever import retrieve
from librarian.memory import capsule, decision_log
from librarian.actions.file_ops import read_file, write_file, edit_file
from librarian.actions.shell_ops import run_command
from librarian.actions.safety import classify_action, RiskLevel

DO_SYSTEM_PROMPT = """You are Librarian, a CLI coding agent. When given a task, respond ONLY with a JSON plan in this format:

{
  "reasoning": "why you are taking this approach",
  "actions": [
    {
      "type": "edit_file",
      "file": "path/to/file.py",
      "description": "what this edit does",
      "old_code": "exact string to find (must exist in the file)",
      "new_code": "replacement string"
    },
    {
      "type": "create_file",
      "file": "path/to/new_file.py",
      "description": "what this file does",
      "content": "full file content"
    },
    {
      "type": "delete_file",
      "file": "path/to/file_or_folder",
      "description": "what is being deleted and why"
    },
    {
      "type": "shell_command",
      "command": "pip install something",
      "description": "install required package"
    }
  ]
}

Rules:
- Only use edit_file when modifying existing code — read the actual file content first before editing
- old_code in edit_file must be the EXACT string from the file, including whitespace
- Use create_file for new files
- Use delete_file to remove files or entire folders
- Use shell_command for terminal commands
- Return ONLY the JSON, no markdown fences, no explanation
"""


def _parse_plan(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)


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


def _execute_action(action: dict) -> dict:
    action_type = action.get("type")
    if action_type == "edit_file":
        edit_file(action["file"], action["old_code"], action["new_code"])
        return {"type": "edit_file", "file": action["file"], "status": "done"}
    elif action_type == "create_file":
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
                p = p.strip("-rf").strip()
                target = Path(p)
                if target.is_dir():
                    shutil.rmtree(target)
                elif target.is_file():
                    target.unlink()
            return {"type": "shell_command", "command": cmd, "status": "done"}
        code, out, err = run_command(cmd)
        return {"type": "shell_command", "command": cmd, "status": "done" if code == 0 else f"exit {code}"}
    return {"type": action_type, "status": "unknown"}


def run(task: str):
    if not Path(".librarian").exists():
        print_header("librarian do")
        print_warning("project not initialised — run 'librarian init' first")
        return

    print_header("librarian do")

    chunks = retrieve(task, n_results=7)
    context = _format_chunks(chunks)
    conventions = read_librarian_md()
    prompt = f"Project conventions:\n{conventions}\n\nRelevant code:\n{context}\n\nTask: {task}"

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
