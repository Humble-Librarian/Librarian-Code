import typer
from librarian.commands import init, ask, do, why, undo, status
from librarian.commands import git_cmd
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

git_app = typer.Typer(help="git operations")
git_app.command(name="commit")(git_cmd.commit)
git_app.command(name="push")(git_cmd.push)
git_app.command(name="diff")(git_cmd.diff)
git_app.command(name="status")(git_cmd.status)
app.add_typer(git_app, name="git")

if __name__ == "__main__":
    app()
