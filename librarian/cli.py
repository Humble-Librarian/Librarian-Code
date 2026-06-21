import typer
from librarian.commands import init, ask, do, why, undo, status
from librarian.commands import git_cmd
from librarian.commands import repl
from librarian.skills.loader import add_skill, list_skills
from librarian.utils.ui import print_banner, print_muted, print_warning, print_panel, console, INDIGO

app = typer.Typer(
    name="librarian",
    help="A CLI coding agent with persistent project memory.",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        print_banner()


app.command(name="init")(init.run)
app.command(name="ask")(ask.run)
app.command(name="do")(do.run)
app.command(name="why")(why.run)
app.command(name="undo")(undo.run)
app.command(name="status")(status.run)
app.command(name="repl")(repl.run)

git_app = typer.Typer(help="git operations")
git_app.command(name="commit")(git_cmd.commit)
git_app.command(name="push")(git_cmd.push)
git_app.command(name="diff")(git_cmd.diff)
git_app.command(name="status")(git_cmd.status)
app.add_typer(git_app, name="git")


def _skill_add(name: str, file: str = None):
    from pathlib import Path
    if file:
        content = Path(file).read_text(encoding="utf-8")
    else:
        console.print(f"[bold {INDIGO}]enter skill conventions (Ctrl+D to finish):[/bold {INDIGO}]")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        content = "\n".join(lines)
    add_skill(name, content)
    print_muted(f"  skill '{name}' added")


def _skill_list():
    skills = list_skills()
    if not skills:
        print_muted("  no skills found")
        return
    from rich.table import Table
    table = Table(show_header=True, header_style=f"bold {INDIGO}")
    table.add_column("name")
    table.add_column("source")
    for s in skills:
        table.add_row(s["name"], s["source"])
    console.print(table)


skill_app = typer.Typer(help="manage custom skills")
skill_app.command(name="add")(_skill_add)
skill_app.command(name="list")(_skill_list)
app.add_typer(skill_app, name="skill")

if __name__ == "__main__":
    app()
