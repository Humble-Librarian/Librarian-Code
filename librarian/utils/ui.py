import sys
import io
import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
console = Console(force_terminal=True)

INDIGO = "#6366F1"
VIOLET = "#8B5CF6"
MUTED = "#6B7280"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
ERROR = "#EF4444"


def print_banner():
    ascii_art = pyfiglet.figlet_format("librarian", font="block")
    console.print(f"[bold {INDIGO}]{ascii_art}[/bold {INDIGO}]")
    console.print(f"[{MUTED}]  a CLI coding agent with persistent project memory[/{MUTED}]\n")


def print_header(title: str):
    console.print(f"\n[bold {INDIGO}]>[/bold {INDIGO}] [bold]{title}[/bold]")
    console.rule(style=INDIGO)


def print_success(msg: str):
    console.print(f"[bold {SUCCESS}]checkmark[/bold {SUCCESS}] {msg}")


def print_warning(msg: str):
    console.print(f"[bold {WARNING}]![/bold {WARNING}] {msg}")


def print_error(msg: str):
    console.print(f"[bold {ERROR}]x[/bold {ERROR}] {msg}")


def print_muted(msg: str):
    console.print(f"[{MUTED}]{msg}[/{MUTED}]")


def print_panel(content: str, title: str = "", style: str = INDIGO):
    console.print(Panel(content, title=title, border_style=style, padding=(1, 2)))


def confirm_action(description: str) -> bool:
    console.print(f"\n[bold {WARNING}]safety check[/bold {WARNING}]")
    return Confirm.ask(f"  [{WARNING}]{description}[/{WARNING}]")


def spinner(description: str):
    return Progress(
        SpinnerColumn(style=INDIGO),
        TextColumn(f"[{MUTED}]{description}[/{MUTED}]"),
        transient=True,
    )
