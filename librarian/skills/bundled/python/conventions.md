# Python Conventions

## Project Structure
- Use `src/` layout for libraries, flat layout for apps
- Package dirs: lowercase with underscores (`my_package`)
- Always include `__init__.py` in every package dir
- Include `py.typed` marker for PEP 561
- Config in `pyproject.toml` (never `setup.py` for new projects)
- Build backend: `hatchling` or `uv_build`
- Package manager: `uv` recommended, `poetry` acceptable

## Code Style (PEP 8)
- 4 spaces indentation, no tabs
- 88 char line length (Black/ruff default)
- 2 blank lines before top-level functions/classes
- 1 blank line between methods inside classes
- snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants

## Imports
- Order: stdlib → third-party → local (separate with blank lines)
- One import per line
- Prefer absolute imports over relative
- Never use `from x import *`

## Type Hints (Modern Python 3.10+)
- Use built-in generics: `list[int]` not `List[int]`, `dict[str, Any]` not `Dict`
- Use `X | None` not `Optional[X]`
- Use `X | Y` not `Union[X, Y]`
- Always annotate return types and parameters
- Use `type` keyword for type aliases (Python 3.12+)

## Patterns
- Use `pathlib.Path` over `os.path`
- Use f-strings over `.format()` or `%` formatting
- Use `with` context managers for file I/O (always specify `encoding="utf-8"`)
- Use `dataclasses` over manual `__init__`/`__repr__`/`__eq__`
- Use `match/case` (Python 3.10+) over long if/elif chains
- Use `@contextmanager` for custom context managers
- Check `is None` / `is not None`, never `== None`
- Check `if x:` not `if len(x) > 0:`

## Testing (pytest)
- Test files: `test_*.py`
- Test functions: `test_<description>`
- Fixtures in `conftest.py`
- Use `@pytest.mark.parametrize` for multiple test cases
- Use `tmp_path` fixture for file operations
- Use `monkeypatch` for mocking

## Anti-Patterns to Avoid
- Bare `except:` → use `except Exception:`
- Mutable default args `def f(x=[])` → use `None` + create inside
- `os.path` → use `pathlib.Path`
- `List[int]` → use `list[int]`
- `print()` in libraries → use `logging`
- `os.system()` → use `subprocess`
- `eval()`/`exec()` → use `ast.literal_eval()` if needed
- Missing `encoding=` on `open()` → always specify `encoding="utf-8"`
- String concatenation in loops → use `"".join()`
