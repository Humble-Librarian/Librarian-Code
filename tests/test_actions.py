import os
import json
import tempfile
import pytest
from pathlib import Path
from librarian.actions.file_ops import read_file, write_file, edit_file, list_files, get_ignored_paths
from librarian.actions.safety import classify_action, RiskLevel


class TestFileOps:
    def test_read_write_file(self, tmp_path):
        path = str(tmp_path / "test.txt")
        write_file(path, "hello world")
        assert read_file(path) == "hello world"

    def test_edit_file(self, tmp_path):
        path = str(tmp_path / "test.txt")
        write_file(path, "foo bar baz")
        edit_file(path, "bar", "qux")
        assert read_file(path) == "foo qux baz"

    def test_edit_file_not_found(self, tmp_path):
        path = str(tmp_path / "test.txt")
        write_file(path, "foo bar")
        with pytest.raises(ValueError, match="String not found"):
            edit_file(path, "nope", "replace")

    def test_edit_file_ambiguous(self, tmp_path):
        path = str(tmp_path / "test.txt")
        write_file(path, "foo foo foo")
        with pytest.raises(ValueError, match="Ambiguous"):
            edit_file(path, "foo", "bar")

    def test_list_files(self, tmp_path):
        (tmp_path / "a.py").write_text("x")
        (tmp_path / "b.js").write_text("y")
        (tmp_path / "c.txt").write_text("z")
        files = list_files(str(tmp_path), [".py"])
        assert len(files) == 1
        assert files[0].endswith("a.py")

    def test_get_ignored_paths(self):
        ignored = get_ignored_paths()
        assert ".git" in ignored
        assert "node_modules" in ignored


class TestSafety:
    def test_classify_safe(self):
        assert classify_action("edit file") == RiskLevel.SAFE
        assert classify_action("create file") == RiskLevel.SAFE

    def test_classify_confirm(self):
        assert classify_action("git push") == RiskLevel.CONFIRM
        assert classify_action("rm -rf /") == RiskLevel.CONFIRM
        assert classify_action("drop table users") == RiskLevel.CONFIRM
