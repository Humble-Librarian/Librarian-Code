import json
import os
import pytest
from pathlib import Path
from typer.testing import CliRunner

from librarian.cli import app
from librarian.memory.session import add_message, get_history, clear_history, format_history
from librarian.memory.capsule import create, get_file_confidence
from librarian.utils.toml_config import load_config, get_config_value
from librarian.skills.loader import add_skill, list_skills, load_skill

runner = CliRunner()


class TestSession:
    def test_add_and_get_history(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian", exist_ok=True)
        add_message("user", "hello")
        add_message("assistant", "hi there")
        history = get_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_clear_history(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian", exist_ok=True)
        add_message("user", "test")
        clear_history()
        history = get_history()
        assert len(history) == 0

    def test_format_history(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian", exist_ok=True)
        add_message("user", "question")
        add_message("assistant", "answer")
        formatted = format_history()
        assert "user" in formatted
        assert "question" in formatted

    def test_history_limit(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian", exist_ok=True)
        for i in range(25):
            add_message("user", f"msg {i}")
        history = get_history()
        assert len(history) <= 20


class TestTomlConfig:
    def test_load_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = load_config()
        assert "model" in config
        assert "max_results" in config

    def test_custom_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        Path("librarian.toml").write_text('[librarian]\nmax_results = 10\n')
        config = load_config()
        assert config["max_results"] == 10

    def test_get_config_value(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        Path("librarian.toml").write_text('[librarian]\ncustom_key = "custom_value"\n')
        value = get_config_value("custom_key")
        assert value == "custom_value"

    def test_get_config_default(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        value = get_config_value("nonexistent", "default")
        assert value == "default"


class TestCustomSkills:
    def test_add_and_load_skill(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        add_skill("test-skill", "Test conventions content")
        content = load_skill("test-skill")
        assert content == "Test conventions content"

    def test_list_skills(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        add_skill("my-skill", "content")
        skills = list_skills()
        names = [s["name"] for s in skills]
        assert "my-skill" in names

    def test_skill_source_custom(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        add_skill("custom-one", "content")
        skills = list_skills()
        custom = [s for s in skills if s["name"] == "custom-one"]
        assert len(custom) == 1
        assert custom[0]["source"] == "custom"


class TestCapsuleFeedback:
    def test_get_file_confidence(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian", exist_ok=True)
        create("task1", "reason1", ["auth.py"])
        create("task2", "reason2", ["auth.py"])
        conf = get_file_confidence("auth.py")
        assert 0 < conf <= 1.0

    def test_unknown_file_confidence(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian", exist_ok=True)
        conf = get_file_confidence("unknown.py")
        assert conf == 1.0


class TestNewCommands:
    def test_repl_help(self):
        result = runner.invoke(app, ["repl", "--help"])
        assert result.exit_code == 0

    def test_git_help(self):
        result = runner.invoke(app, ["git", "--help"])
        assert result.exit_code == 0
        assert "git" in result.output.lower()

    def test_skill_help(self):
        result = runner.invoke(app, ["skill", "--help"])
        assert result.exit_code == 0
        assert "skill" in result.output.lower()

    def test_skill_list(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["skill", "list"])
        assert result.exit_code == 0
