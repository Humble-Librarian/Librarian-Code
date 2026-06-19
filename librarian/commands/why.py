from pathlib import Path
from datetime import datetime, timezone
from librarian.utils.ui import print_header, print_warning, print_muted, console, INDIGO
from librarian.memory.decision_log import get_last


def _time_ago(timestamp: str) -> str:
    try:
        ts = datetime.fromisoformat(timestamp)
        now = datetime.now(timezone.utc)
        diff = now - ts
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            return f"{seconds // 60} min ago"
        if seconds < 86400:
            return f"{seconds // 3600} hours ago"
        return f"{seconds // 86400} days ago"
    except Exception:
        return "—"


def run():
    if not Path(".librarian").exists():
        print_header("librarian why")
        print_warning("project not initialised — run 'librarian init' first")
        return

    print_header("decision history")

    entries = get_last(10)
    if not entries:
        print_muted("  no decisions logged yet")
        return

    for i, entry in enumerate(reversed(entries), 1):
        time_str = _time_ago(entry.get("timestamp", ""))
        task = entry.get("task", "—")
        reasoning = entry.get("reasoning", "—")
        provider = entry.get("llm_provider", "—")
        outcome = entry.get("outcome", "approved")
        tokens = entry.get("tokens_used", 0)

        console.print(f"\n  [bold {INDIGO}]{i}[/bold {INDIGO}]  [{time_str}]  {task}")
        console.print(f"      reasoning: {reasoning[:80]}{'...' if len(reasoning) > 80 else ''}")
        console.print(f"      provider: {provider}  tokens: {tokens}  outcome: {outcome}")
