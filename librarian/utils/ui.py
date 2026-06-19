import sys
import io
import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.columns import Columns
from rich.text import Text

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
console = Console(force_terminal=True)

INDIGO = "#6366F1"
VIOLET = "#8B5CF6"
MUTED = "#6B7280"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
ERROR = "#EF4444"
CYAN = "#06B6D4"
PINK = "#EC4899"


def print_banner():
    ascii_art = pyfiglet.figlet_format("librarian", font="larry3d")
    styled_art = Text(ascii_art, style="bold white")
    tagline = Text("\n  a CLI coding agent with persistent project memory", style=f"italic {MUTED}")

    commands = Table(show_header=False, box=None, padding=(0, 2))
    commands.add_column(style=f"bold {CYAN}")
    commands.add_column(style=MUTED)
    commands.add_row("init", "index your project")
    commands.add_row("ask", "question your codebase")
    commands.add_row("do", "execute a task")
    commands.add_row("why", "see decision history")
    commands.add_row("undo", "revert last action")
    commands.add_row("status", "project overview")

    banner_content = Text()
    banner_content.append_text(styled_art)
    banner_content.append_text(tagline)

    panel = Panel(
        banner_content,
        border_style=INDIGO,
        padding=(1, 3),
    )
    console.print()
    console.print(panel)

    cmd_panel = Panel(
        commands,
        title=f"[bold {VIOLET}]commands[/bold {VIOLET}]",
        border_style=VIOLET,
        padding=(0, 1),
    )
    console.print(cmd_panel)
    console.print()


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
