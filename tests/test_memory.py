import json
import os
import tempfile

import pytest
from pathlib import Path
from librarian.memory.chunker import chunk_file
from librarian.memory.capsule import create, get_all, undo, approve
from librarian.memory.decision_log import append, get_last
import tempfile
import os


class TestChunker:
    def test_chunk_python(self, tmp_path):
        code = """
def hello():
    pass

def world():
    pass
"""
        path = str(tmp_path / "test.py")
        with open(path, "w") as f:
            f.write(code)
        chunks = chunk_file(path)
        assert len(chunks) >= 2
        assert all(c["metadata"]["language"] == "python" for c in chunks)

    def test_chunk_text(self, tmp_path):
        content = "# Heading 1\nSome text\n\n## Heading 2\nMore text"
        path = str(tmp_path / "test.md")
        with open(path, "w") as f:
            f.write(content)
        chunks = chunk_file(path)
        assert len(chunks) >= 1


class TestCapsule:
    def test_create_and_get(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian", exist_ok=True)
        capsule = create("test task", "test reason", ["test.py"])
        assert capsule["decision"] == "test task"
        assert capsule["confidence"] == 0.5

    def test_undo_reduces_confidence(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian/archive", exist_ok=True)
        capsule_entry = create("task", "reason")
        capsule_id = capsule_entry["id"]
        undo(capsule_id)
        archive_file = Path(".librarian/archive/archived_capsules.json")
        assert archive_file.exists()
        archived = json.loads(archive_file.read_text())
        undone = [c for c in archived if c["id"] == capsule_id]
        assert len(undone) == 1
        assert undone[0]["outcome"] == "undone"
        assert undone[0]["confidence"] < 0.5


class TestDecisionLog:
    def test_append_and_get(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian", exist_ok=True)
        append({"task": "test", "command": "do"})
        entries = get_last(5)
        assert len(entries) == 1
        assert entries[0]["task"] == "test"
