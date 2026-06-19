import typer
from librarian.commands import init, ask, do, why, undo, status

app = typer.Typer(
    name="librarian",
    help="A CLI coding agent with persistent project memory.",
    add_completion=False,
)

app.command(name="init")(init.run)
app.command(name="ask")(ask.run)
app.command(name="do")(do.run)
app.command(name="why")(why.run)
app.command(name="undo")(undo.run)
app.command(name="status")(status.run)

if __name__ == "__main__":
    app()
