import pytest
from typer.testing import CliRunner
from librarian.cli import app

runner = CliRunner()


class TestCommands:
    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "librarian" in result.output.lower() or "CLI coding agent" in result.output

    def test_status_no_init(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "not yet" in result.output.lower() or "run" in result.output.lower()

    def test_ask_no_init(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ask", "test"])
        assert result.exit_code == 0
        assert "not initialised" in result.output.lower() or "init" in result.output.lower()

    def test_do_no_init(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["do", "test task"])
        assert result.exit_code == 0
        assert "not initialised" in result.output.lower() or "init" in result.output.lower()

    def test_why_no_init(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["why"])
        assert result.exit_code == 0

    def test_undo_no_init(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["undo"])
        assert result.exit_code == 0
