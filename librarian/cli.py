import typer
from librarian.commands import init, ask, do, why, undo, status
from librarian.utils.ui import print_banner, print_muted, print_warning

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

if __name__ == "__main__":
    app()
