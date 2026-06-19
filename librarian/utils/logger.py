from rich.console import Console
from rich.theme import Theme

theme = Theme({
    "info": "bold #6366F1",
    "success": "bold #10B981",
    "warning": "bold #F59E0B",
    "error": "bold #EF4444",
    "muted": "#6B7280",
})

console = Console(theme=theme)


def log_info(msg):
    console.print(f"[info]→[/info] {msg}")


def log_success(msg):
    console.print(f"[success]✓[/success] {msg}")


def log_warning(msg):
    console.print(f"[warning]![/warning] {msg}")


def log_error(msg):
    console.print(f"[error]✗[/error] {msg}")


def log_muted(msg):
    console.print(f"[muted]{msg}[/muted]")
