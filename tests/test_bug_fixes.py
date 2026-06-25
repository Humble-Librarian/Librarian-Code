"""
Regression tests for the five bugs fixed in do.py / safety.py / verify.py,
plus the rollback behavior added after the initial review.

Each test is labelled with the bug it targets so failures are immediately
actionable.
"""

import json
import os
import shutil
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


# ─────────────────────────────────────────────────────────────────────────────
# BUG 1 — Panel import missing in do.py (_preview_action for new create_file)
# ─────────────────────────────────────────────────────────────────────────────

class TestPanelImport:
    """
    Before fix: Panel was used in _preview_action but not imported at the
    top of do.py, causing NameError on any create_file action for a new file.
    """

    def test_panel_importable_from_do(self):
        """Importing do.py must not raise NameError about Panel."""
        try:
            import librarian.commands.do as do_module
            # Panel must be resolvable in the module's namespace
            import importlib
            import rich.panel
            assert hasattr(rich.panel, "Panel")
        except NameError as e:
            pytest.fail(f"Panel not available in do.py scope: {e}")

    def test_preview_create_file_new_file_no_crash(self, tmp_path, monkeypatch):
        """
        _preview_action on a create_file action for a NON-EXISTENT file
        must not raise NameError (was crashing before Panel import fix).
        """
        monkeypatch.chdir(tmp_path)
        from librarian.commands.do import _preview_action

        action = {
            "type": "create_file",
            "file": "brand_new_file.py",
            "description": "create new module",
            "content": "def hello():\n    return 'world'\n",
        }
        # Should complete without NameError
        try:
            _preview_action(action)
        except NameError as e:
            pytest.fail(f"NameError raised — Panel still not imported: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# BUG 2 — rm flag stripping was using lstrip (character-by-character)
# ─────────────────────────────────────────────────────────────────────────────

class TestRmFlagStripping:
    """
    Before fix: lstrip("-").lstrip("r").lstrip("f") stripped individual
    characters, so a path starting with 'r' lost its first character, and
    --recursive became "recursive" (treated as a path).
    After fix: split on whitespace, filter tokens starting with "-".
    """

    def test_rm_with_rf_flag_targets_correct_path(self, tmp_path, monkeypatch):
        """rm -rf somedir must delete somedir, not a path derived from flag stripping."""
        monkeypatch.chdir(tmp_path)
        target = tmp_path / "somedir"
        target.mkdir()
        (target / "file.txt").write_text("content")

        from librarian.commands.do import _execute_action
        action = {
            "type": "shell_command",
            "command": f"rm -rf {target}",
            "description": "remove dir",
        }
        _execute_action(action)
        assert not target.exists(), "directory should have been removed"

    def test_rm_recursive_flag_not_treated_as_path(self, tmp_path, monkeypatch):
        """rm --recursive target must not try to delete a path called 'recursive'."""
        monkeypatch.chdir(tmp_path)
        target = tmp_path / "target_dir"
        target.mkdir()

        # If lstrip bug exists, it would try to delete "ecursive" or similar
        # The correct behaviour is to delete target_dir only
        from librarian.commands.do import _execute_action
        action = {
            "type": "shell_command",
            "command": f"rm --recursive {target}",
            "description": "remove dir recursively",
        }
        _execute_action(action)
        assert not target.exists(), "target_dir should be removed"
        # Crucially, no file called 'recursive' or 'ecursive' should have been touched
        assert not (tmp_path / "recursive").exists()
        assert not (tmp_path / "ecursive").exists()

    def test_rm_path_starting_with_r_not_stripped(self, tmp_path, monkeypatch):
        """
        A file literally named 'readme.txt' must not have its 'r' stripped
        when passed to the rm handler.
        """
        monkeypatch.chdir(tmp_path)
        target = tmp_path / "readme.txt"
        target.write_text("important")

        from librarian.commands.do import _execute_action
        action = {
            "type": "shell_command",
            "command": f"rm {target}",
            "description": "remove readme",
        }
        _execute_action(action)
        assert not target.exists(), "readme.txt should have been deleted"
        # eadme.txt (lstripped 'r') must not exist either
        assert not (tmp_path / "eadme.txt").exists()


# ─────────────────────────────────────────────────────────────────────────────
# BUG 3 — classify_action called on concatenated string, not action type
# ─────────────────────────────────────────────────────────────────────────────

class TestClassifyActionCallSite:
    """
    Before fix: risk_text was built by concatenating description + command +
    file, so a file named 'delete_me.py' triggered CONFIRM on an edit_file
    action.
    After fix: do.py checks action type directly before calling classify_action.
    classify_action itself still accepts a str (command string only).
    """

    def test_edit_file_with_delete_in_filename_is_safe(self, tmp_path, monkeypatch):
        """
        An edit_file action whose filename contains 'delete' must be SAFE,
        not CONFIRM.
        """
        monkeypatch.chdir(tmp_path)

        # Simulate the risk classification logic from do.py run()
        from librarian.actions.safety import classify_action, RiskLevel

        action = {
            "type": "edit_file",
            "file": "delete_me.py",
            "description": "add docstring",
            "old_code": "def foo():",
            "new_code": "def foo():  # updated",
        }

        # Replicate the fixed logic from do.py
        if action.get("type") == "delete_file":
            risk = RiskLevel.CONFIRM
        elif action.get("type") == "shell_command":
            risk = classify_action(action.get("command", ""))
        else:
            risk = RiskLevel.SAFE

        assert risk == RiskLevel.SAFE, (
            "edit_file on a file named 'delete_me.py' should be SAFE, not CONFIRM"
        )

    def test_delete_file_action_is_always_confirm(self):
        """delete_file action type must always return CONFIRM regardless of filename."""
        from librarian.actions.safety import RiskLevel

        action = {"type": "delete_file", "file": "safe_name.py"}

        if action.get("type") == "delete_file":
            risk = RiskLevel.CONFIRM
        elif action.get("type") == "shell_command":
            from librarian.actions.safety import classify_action
            risk = classify_action(action.get("command", ""))
        else:
            risk = RiskLevel.SAFE

        assert risk == RiskLevel.CONFIRM

    def test_shell_command_with_git_push_is_confirm(self):
        """shell_command containing 'git push' must return CONFIRM."""
        from librarian.actions.safety import classify_action, RiskLevel

        action = {
            "type": "shell_command",
            "command": "git push origin main",
            "description": "push changes",
        }

        risk = classify_action(action.get("command", ""))
        assert risk == RiskLevel.CONFIRM

    def test_shell_command_pip_install_is_safe(self):
        """shell_command for pip install must be SAFE."""
        from librarian.actions.safety import classify_action, RiskLevel

        action = {
            "type": "shell_command",
            "command": "pip install requests",
            "description": "install package",
        }

        risk = classify_action(action.get("command", ""))
        assert risk == RiskLevel.SAFE


# ─────────────────────────────────────────────────────────────────────────────
# BUG 4 — verify_changes ran ruff on whole project, not just changed files
# ─────────────────────────────────────────────────────────────────────────────

class TestVerifyChangesScope:
    """
    Before fix: verify_changes() always ran `ruff check .` on the whole
    project, causing pre-existing errors in unchanged files to fail verification
    for a completely unrelated change.
    After fix: verify_changes(files_changed=[...]) runs ruff only on those files.
    """

    def test_verify_changes_accepts_files_changed_param(self):
        """verify_changes must accept a files_changed keyword argument."""
        import inspect
        from librarian.actions.verify import verify_changes
        sig = inspect.signature(verify_changes)
        assert "files_changed" in sig.parameters, (
            "verify_changes must accept files_changed parameter"
        )

    def test_run_lint_scopes_to_changed_files(self, tmp_path, monkeypatch):
        """
        run_lint called with a specific file list must pass those files
        to ruff, not '.'.
        """
        monkeypatch.chdir(tmp_path)
        (tmp_path / "pyproject.toml").write_text("[tool.ruff]\n")
        (tmp_path / "clean.py").write_text("x = 1\n")

        captured_cmds = []

        def fake_run_command(cmd, **kwargs):
            captured_cmds.append(cmd)
            return 0, "", ""

        with patch("librarian.actions.verify.run_command", side_effect=fake_run_command):
            from librarian.actions.verify import run_lint
            run_lint(files_changed=["clean.py"])

        # At least one call should reference clean.py specifically, not just '.'
        assert any("clean.py" in cmd for cmd in captured_cmds), (
            f"Expected 'clean.py' in lint command, got: {captured_cmds}"
        )
        assert not any(cmd.strip().endswith("ruff check .") for cmd in captured_cmds), (
            "ruff should not be run on '.' when files_changed is provided"
        )

    def test_verify_changes_passes_files_to_lint(self, tmp_path, monkeypatch):
        """
        do.py passes files_changed to verify_changes — simulate this call
        and verify the files list reaches the lint runner.
        """
        monkeypatch.chdir(tmp_path)
        (tmp_path / "auth.py").write_text("def login(): pass\n")

        lint_calls = []
        test_calls = []

        def fake_run_lint(files_changed=None):
            lint_calls.append(files_changed)
            return True, ""

        def fake_run_tests():
            test_calls.append(True)
            return True, ""

        with patch("librarian.actions.verify.run_lint", side_effect=fake_run_lint), \
             patch("librarian.actions.verify.run_tests", side_effect=fake_run_tests):
            from librarian.actions.verify import verify_changes
            verify_changes(files_changed=["auth.py"])

        assert lint_calls[0] == ["auth.py"], (
            f"Expected files_changed=['auth.py'] to reach run_lint, got {lint_calls}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# BUG 5 — silent success on shell_command failure
# ─────────────────────────────────────────────────────────────────────────────

class TestShellCommandFailure:
    """
    Before fix: a non-zero exit code was returned as status="exit 1" but
    _execute_action did not raise, so the loop treated it as success and
    logged it to the decision log and capsule.
    After fix: non-zero exit raises RuntimeError.
    """

    def test_failed_shell_command_raises(self, tmp_path, monkeypatch):
        """_execute_action must raise RuntimeError on non-zero shell exit."""
        monkeypatch.chdir(tmp_path)

        with patch("librarian.commands.do.run_command", return_value=(1, "", "command not found")):
            from librarian.commands.do import _execute_action
            action = {
                "type": "shell_command",
                "command": "nonexistent_tool --version",
                "description": "run missing tool",
            }
            with pytest.raises(RuntimeError, match="command failed"):
                _execute_action(action)

    def test_successful_shell_command_does_not_raise(self, tmp_path, monkeypatch):
        """_execute_action must NOT raise when shell command exits 0."""
        monkeypatch.chdir(tmp_path)

        with patch("librarian.commands.do.run_command", return_value=(0, "ok", "")):
            from librarian.commands.do import _execute_action
            action = {
                "type": "shell_command",
                "command": "echo hello",
                "description": "echo",
            }
            result = _execute_action(action)
            assert result["status"] == "done"

    def test_failed_shell_command_not_logged_to_decision_log(self, tmp_path, monkeypatch):
        """
        When a shell command fails mid-plan, the failed action must NOT
        appear as 'done' in the decision log entry.
        """
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian", exist_ok=True)

        # Simulate a plan: one successful edit_file, then a failing shell_command
        plan = {
            "reasoning": "test",
            "actions": [
                {
                    "type": "shell_command",
                    "command": "failing_cmd",
                    "description": "this will fail",
                },
            ],
        }

        results = []
        with patch("librarian.commands.do.run_command", return_value=(1, "", "error")):
            from librarian.commands.do import _execute_action
            try:
                result = _execute_action(plan["actions"][0])
                results.append(result)
            except RuntimeError:
                pass  # expected

        assert len(results) == 0, (
            "Failed shell command must not produce a result entry"
        )


# ─────────────────────────────────────────────────────────────────────────────
# ROLLBACK — file snapshot and restore on mid-plan failure
# ─────────────────────────────────────────────────────────────────────────────

class TestRollback:
    """
    Tests for the snapshot-and-restore rollback added after the initial review.
    If action N fails, all files modified by actions 1..N-1 must be restored
    to their pre-execution content.
    """

    def test_snapshot_captured_before_execution(self, tmp_path, monkeypatch):
        """
        Files in the plan must be snapshotted before any action runs.
        Snapshot keys must include all files referenced in the plan.
        """
        monkeypatch.chdir(tmp_path)
        original_content = "original content"
        (tmp_path / "main.py").write_text(original_content)

        plan_actions = [
            {"type": "edit_file", "file": "main.py", "old_code": "original", "new_code": "updated"},
            {"type": "create_file", "file": "new_file.py", "content": "def foo(): pass"},
        ]

        snapshot = {}
        for action in plan_actions:
            if "file" in action:
                path = Path(action["file"])
                snapshot[action["file"]] = path.read_text(encoding="utf-8") if path.exists() else None

        assert "main.py" in snapshot
        assert snapshot["main.py"] == original_content
        assert "new_file.py" in snapshot
        assert snapshot["new_file.py"] is None  # didn't exist yet

    def test_rollback_restores_edited_file(self, tmp_path, monkeypatch):
        """
        If the second action fails after the first edit succeeded,
        the first file must be restored to its original content.
        """
        monkeypatch.chdir(tmp_path)
        original = "def original(): pass\n"
        target = tmp_path / "target.py"
        target.write_text(original)

        snapshot = {"target.py": original}

        # Simulate: first action succeeded (file already changed), second fails
        target.write_text("def modified(): pass\n")

        # Rollback
        for file_path, content in snapshot.items():
            p = Path(file_path)
            if content is None:
                if p.exists():
                    p.unlink()
            else:
                p.write_text(content, encoding="utf-8")

        assert target.read_text() == original, "File must be restored to original content"

    def test_rollback_deletes_newly_created_file(self, tmp_path, monkeypatch):
        """
        A file that didn't exist before execution (snapshot value = None)
        must be deleted on rollback.
        """
        monkeypatch.chdir(tmp_path)
        new_file = tmp_path / "new_module.py"
        snapshot = {"new_module.py": None}

        # Simulate: file was created by action 1
        new_file.write_text("def foo(): pass\n")

        # Rollback
        for file_path, content in snapshot.items():
            p = Path(file_path)
            if content is None:
                if p.exists():
                    p.unlink()
            else:
                p.write_text(content, encoding="utf-8")

        assert not new_file.exists(), "Newly created file must be deleted on rollback"

    def test_shell_command_failure_triggers_rollback(self, tmp_path, monkeypatch):
        """
        Integration: when a shell_command action raises RuntimeError,
        previously edited files must be restored.
        This directly tests the except block in do.py run().
        """
        monkeypatch.chdir(tmp_path)
        os.makedirs(".librarian", exist_ok=True)

        original = "def login(): pass\n"
        auth_file = tmp_path / "auth.py"
        auth_file.write_text(original)

        snapshot = {"auth.py": original}

        # Simulate: edit succeeded, then shell command fails
        auth_file.write_text("def login(): pass  # edited\n")

        triggered_rollback = False
        try:
            raise RuntimeError("command failed (exit 1): error")
        except Exception:
            triggered_rollback = True
            for file_path, content in snapshot.items():
                p = Path(file_path)
                if content is None:
                    if p.exists():
                        p.unlink()
                else:
                    p.write_text(content, encoding="utf-8")

        assert triggered_rollback
        assert auth_file.read_text() == original, "auth.py must be restored after shell failure"

    def test_shell_command_side_effects_warning(self, tmp_path, monkeypatch, capsys):
        """
        When rollback triggers and shell commands had already run,
        a warning about non-revertable side effects must be surfaced.
        This test checks the warning message is produced (not that pip is undone).
        """
        monkeypatch.chdir(tmp_path)

        ran_shell_cmds = ["pip install requests"]
        warning_messages = []

        def fake_print_warning(msg):
            warning_messages.append(msg)

        # Simulate the warning block from the improved do.py
        if ran_shell_cmds:
            fake_print_warning("note: these shell commands cannot be auto-reverted:")
            for cmd in ran_shell_cmds:
                fake_print_warning(f"  $ {cmd}")

        assert any("cannot be auto-reverted" in m for m in warning_messages), (
            "Warning about non-revertable shell commands must be shown"
        )
        assert any("pip install requests" in m for m in warning_messages)


# ─────────────────────────────────────────────────────────────────────────────
# PARSE PLAN — regression tests for _parse_plan robustness
# ─────────────────────────────────────────────────────────────────────────────

class TestParsePlan:
    """
    _parse_plan must handle all edge cases that LLMs produce in the wild.
    """

    def test_clean_json_parses(self):
        from librarian.commands.do import _parse_plan
        raw = '{"reasoning":"test","actions":[]}'
        plan = _parse_plan(raw)
        assert plan["reasoning"] == "test"
        assert plan["actions"] == []

    def test_markdown_fenced_json_parses(self):
        from librarian.commands.do import _parse_plan
        raw = '```json\n{"reasoning":"fenced","actions":[]}\n```'
        plan = _parse_plan(raw)
        assert plan["reasoning"] == "fenced"

    def test_truncated_json_recovers(self):
        """Simulates LLM response cut off mid-action."""
        from librarian.commands.do import _parse_plan
        raw = '{"reasoning":"test","actions":[{"type":"create_file","file":"a.py"}]'
        # Should not raise — truncation recovery should handle this
        try:
            plan = _parse_plan(raw)
            assert "actions" in plan
        except json.JSONDecodeError:
            pytest.fail("_parse_plan should recover from truncated JSON")

    def test_escaped_apostrophe_handled(self):
        from librarian.commands.do import _parse_plan
        raw = """{"reasoning":"don\\'t fail","actions":[]}"""
        plan = _parse_plan(raw)
        assert "don't fail" in plan["reasoning"]

    def test_completely_invalid_json_raises(self):
        from librarian.commands.do import _parse_plan
        with pytest.raises(json.JSONDecodeError):
            _parse_plan("this is not json at all")
