import ast
import os
import re
from datetime import datetime, timezone


def chunk_file(path: str) -> list[dict]:
    ext = os.path.splitext(path)[1].lower()
    try:
        content = open(path, encoding="utf-8").read()
    except UnicodeDecodeError:
        content = open(path, encoding="latin-1").read()

    if ext == ".py":
        return _chunk_python(path, content)
    elif ext in (".js", ".ts", ".jsx", ".tsx"):
        return _chunk_js(path, content)
    elif ext in (".md", ".txt"):
        return _chunk_text(path, content)
    else:
        return _chunk_generic(path, content)


def _chunk_python(path: str, content: str) -> list[dict]:
    chunks = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return _chunk_generic(path, content)

    lines = content.splitlines()
    mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).isoformat()

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno - 1
            end = node.end_lineno or start + 1
            chunk_text = "\n".join(lines[start:end])
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    "file_path": path,
                    "chunk_type": "function",
                    "name": node.name,
                    "language": "python",
                    "start_line": start + 1,
                    "end_line": end,
                    "last_modified": mtime,
                },
            })
        elif isinstance(node, ast.ClassDef):
            start = node.lineno - 1
            end = node.end_lineno or start + 1
            chunk_text = "\n".join(lines[start:end])
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    "file_path": path,
                    "chunk_type": "class",
                    "name": node.name,
                    "language": "python",
                    "start_line": start + 1,
                    "end_line": end,
                    "last_modified": mtime,
                },
            })

    if not chunks:
        chunks.append({
            "content": content,
            "metadata": {
                "file_path": path,
                "chunk_type": "module",
                "name": os.path.basename(path),
                "language": "python",
                "start_line": 1,
                "end_line": len(lines),
                "last_modified": mtime,
            },
        })
    return chunks


def _chunk_js(path: str, content: str) -> list[dict]:
    pattern = r"^(?:export\s+)?(?:async\s+)?(?:function\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?(?:\([^)]*\)\s*=>|function)|class\s+\w+)"
    lines = content.splitlines()
    mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).isoformat()
    lang = "javascript" if os.path.splitext(path)[1] in (".js", ".jsx") else "typescript"

    chunks = []
    for i, line in enumerate(lines):
        if re.match(pattern, line.strip()):
            end = min(i + 50, len(lines))
            chunk_text = "\n".join(lines[i:end])
            name_match = re.search(r"(?:function|class|const)\s+(\w+)", line)
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    "file_path": path,
                    "chunk_type": "function",
                    "name": name_match.group(1) if name_match else "unknown",
                    "language": lang,
                    "start_line": i + 1,
                    "end_line": end,
                    "last_modified": mtime,
                },
            })

    if not chunks:
        chunks.append({
            "content": content,
            "metadata": {
                "file_path": path,
                "chunk_type": "module",
                "name": os.path.basename(path),
                "language": lang,
                "start_line": 1,
                "end_line": len(lines),
                "last_modified": mtime,
            },
        })
    return chunks


def _chunk_text(path: str, content: str) -> list[dict]:
    mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).isoformat()
    chunks = []
    sections = re.split(r"\n(?=#{1,3}\s)", content)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        heading_match = re.match(r"^#{1,3}\s+(.*)", section)
        chunks.append({
            "content": section,
            "metadata": {
                "file_path": path,
                "chunk_type": "text",
                "name": heading_match.group(1) if heading_match else os.path.basename(path),
                "language": "markdown",
                "start_line": 1,
                "end_line": content[:content.find(section)].count("\n") + section.count("\n") + 1,
                "last_modified": mtime,
            },
        })
    if not chunks:
        chunks.append({
            "content": content,
            "metadata": {
                "file_path": path,
                "chunk_type": "text",
                "name": os.path.basename(path),
                "language": "text",
                "start_line": 1,
                "end_line": content.count("\n") + 1,
                "last_modified": mtime,
            },
        })
    return chunks


def _chunk_generic(path: str, content: str) -> list[dict]:
    mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).isoformat()
    chunk_size = 500
    overlap = 50
    chunks = []
    for i in range(0, len(content), chunk_size - overlap):
        chunk_text = content[i:i + chunk_size]
        chunks.append({
            "content": chunk_text,
            "metadata": {
                "file_path": path,
                "chunk_type": "module",
                "name": os.path.basename(path),
                "language": os.path.splitext(path)[1].lstrip("."),
                "start_line": content[:i].count("\n") + 1,
                "end_line": content[:i + len(chunk_text)].count("\n") + 1,
                "last_modified": mtime,
            },
        })
    return chunks
