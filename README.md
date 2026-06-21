# librarian

> a CLI coding agent that remembers your project

## what it does differently

Librarian is a local-first CLI coding agent with persistent project memory. Unlike tools that call an LLM on every request regardless of confidence, Librarian builds a capsule-based memory of your project's decisions — remembering why edits were made, adjusting confidence over time, and routing between Groq and OpenRouter intelligently when rate limits hit.

Built without LangChain — pure Python, owned stack. Every file operation, every LLM call, every decision is transparent and logged.

## install

```bash
pip install -e .
```

Set up your API keys:

```bash
cp .env.example .env
# edit .env with your keys
```

## quick start

```bash
librarian init                    # index your project
librarian ask "what does this project do?"
librarian do "add input validation to login()"
librarian why                     # see decision history
librarian undo                    # revert last action
librarian status                  # project overview
```

## commands

| command | what it does |
|---------|-------------|
| `librarian init` | indexes project files, generates LIBRARIAN.md conventions |
| `librarian ask` | asks a question about your codebase, returns answer with sources |
| `librarian do` | gives librarian a task, shows plan preview, executes with your approval |
| `librarian why` | shows last decisions with reasoning |
| `librarian undo` | reverts the last agent action |
| `librarian status` | shows project info, memory stats, token usage |

## how memory works

Librarian uses a **capsule-based memory system**:

- Every action creates a **capsule** with a confidence score (starts at 0.5)
- When you approve an action: confidence × 1.15
- When you undo an action: confidence × 0.6
- Unused capsules decay: × 0.98 per day
- Capsules below 0.4 confidence are archived

This means Librarian learns from your feedback over time — actions you approve become more confident, actions you undo become less likely to be repeated.

## skills

Librarian auto-detects your project type and loads relevant conventions:

- **python**: pyproject.toml, setup.py, requirements.txt
- **react**: next.config.*, .tsx/.jsx files
- **web-dev**: .html files, CSS/SCSS
- **api-design**: routes.py, models.py, schemas.py

Skills provide domain-specific best practices that are injected into the LLM context for more relevant suggestions.

## architecture

```
librarian/
├── adapter/          # LLM adapters (Groq primary, OpenRouter fallback)
│   ├── base.py       # abstract adapter interface
│   ├── groq_adapter.py
│   └── openrouter_adapter.py
├── orchestrator/     # routing and system prompt building
│   ├── router.py     # Groq → OpenRouter fallback
│   └── core.py       # prompt construction
├── memory/           # persistent project memory
│   ├── chunker.py    # AST-based code splitting
│   ├── indexer.py    # ChromaDB + sentence-transformers
│   ├── retriever.py  # semantic search (cached model)
│   ├── capsule.py    # decision memory with confidence
│   └── decision_log.py  # append-only action log
├── skills/           # auto-detected project conventions
│   ├── loader.py     # project type detection with caching
│   └── bundled/      # skill convention files
├── actions/          # file and shell operations
│   ├── file_ops.py   # read, write, edit files
│   ├── shell_ops.py  # git and shell commands (shell=False)
│   └── safety.py     # risk classification
├── commands/         # CLI commands
│   ├── init.py
│   ├── ask.py
│   ├── do.py
│   ├── why.py
│   ├── undo.py
│   └── status.py
├── utils/            # shared utilities
│   ├── config.py     # env var loading
│   ├── ui.py         # Terminal Luxury output
│   ├── logger.py     # structured logging
│   └── token_tracker.py
├── cli.py            # typer entry point
└── exceptions.py     # custom exception types
```

## providers

- **Groq** (primary): `llama-3.3-70b-versatile`, fast inference
- **OpenRouter** (fallback): `qwen/qwen3-coder:free`, automatic on rate limit

## security

- Shell commands use `shell=False` with argument lists to prevent injection
- File operations use proper context managers to prevent handle leaks
- API responses validated before access
- LLM-generated delete operations require confirmation

## performance

- SentenceTransformer model cached as singleton (~2-3s saved per invocation)
- ChromaDB client reused across calls
- Project type detection cached with `@lru_cache`
- Heavy dependencies lazy-loaded at function call time

## testing

```bash
python -m pytest tests/ -v
```

## license

MIT
