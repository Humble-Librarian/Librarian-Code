# librarian

> a CLI coding agent that remembers your project

## what it does differently

Librarian is a local-first CLI coding agent with persistent project memory. Unlike tools that call an LLM on every request regardless of confidence, Librarian builds a capsule-based memory of your project's decisions — remembering why edits were made, adjusting confidence over time, and routing between Groq and OpenRouter intelligently when rate limits hit.

Built without LangChain — pure Python, owned stack. Every file operation, every LLM call, every decision is transparent and logged.

## install

```bash
pip install -g librarian-code
```

## setup

You need at least one free API key:

| Provider | Get Key | Cost |
|----------|---------|------|
| **Groq** | https://console.groq.com | Free tier available |
| **OpenRouter** | https://openrouter.ai | Free models available |

Create `.env` in your project root:

```bash
# option 1: groq (fast)
echo "GROQ_API_KEY=gsk_..." > .env

# option 2: openrouter
echo "OPENROUTER_API_KEY=sk-or-..." > .env

# or both (openrouter used as fallback)
```

## quick start

```bash
librarian init                         # index your project
librarian ask "what does this project do?"
librarian do "add input validation to login()"
librarian repl                         # interactive session
librarian why                          # see decision history
librarian undo                         # revert last action
librarian status                       # project overview
```

## commands

| command | what it does |
|---------|-------------|
| `librarian init` | indexes project files, generates LIBRARIAN.md conventions |
| `librarian ask` | asks a question about your codebase, returns answer with sources |
| `librarian do` | gives librarian a task, shows plan + diff preview, executes with your approval |
| `librarian repl` | interactive REPL with persistent session history |
| `librarian why` | shows last decisions with reasoning |
| `librarian undo` | reverts the last agent action |
| `librarian status` | shows project info, memory stats, token usage |

### git commands

| command | what it does |
|---------|-------------|
| `librarian git commit` | stage all changes and commit |
| `librarian git push` | push to remote |
| `librarian git diff` | show current diff |
| `librarian git status` | show git status |

### skill commands

| command | what it does |
|---------|-------------|
| `librarian skill list` | list bundled and custom skills |
| `librarian skill add <name>` | add a custom skill from stdin or file |

### options

| flag | works with | what it does |
|------|------------|-------------|
| `--file` | `ask`, `do` | scope retrieval to a specific file |

## features

### streaming output

LLM responses stream token-by-token — no more waiting for the full response.

### diff preview

Before executing changes, see a syntax-highlighted diff of exactly what will change.

### multi-turn conversation

Ask follow-up questions — Librarian remembers context within a session.

### file targeting

Scope your query to a specific file for more precise results:

```bash
librarian ask "what does this function do?" --file src/auth.py
librarian do "fix the bug" --file src/user.py
```

### auto verification

After executing changes, Librarian automatically runs tests and linting to catch regressions.

### capsule feedback

Your approve/undo signals feed back into retrieval ranking — files you approve get boosted, files you undo get penalized.

### custom skills

Add your own project-specific conventions:

```bash
librarian skill add my-stack
# type your conventions, then Ctrl+D
```

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

## configuration

Create `librarian.toml` in your project root to customize behavior:

```toml
[librarian]
model = "all-MiniLM-L6-v2"
max_results = 5
distance_threshold = 2.5
auto_verify = true
```

## architecture

```
librarian/
├── adapter/          # LLM adapters (Groq primary, OpenRouter fallback)
│   ├── base.py       # abstract adapter interface + streaming
│   ├── groq_adapter.py
│   └── openrouter_adapter.py
├── orchestrator/     # routing and system prompt building
│   ├── router.py     # Groq → OpenRouter fallback + streaming
│   └── core.py       # prompt construction + session history
├── memory/           # persistent project memory
│   ├── chunker.py    # AST-based code splitting
│   ├── indexer.py    # ChromaDB + sentence-transformers
│   ├── retriever.py  # semantic search (cached model + capsule feedback)
│   ├── capsule.py    # decision memory with confidence
│   ├── session.py    # multi-turn conversation history
│   └── decision_log.py  # append-only action log
├── skills/           # auto-detected project conventions
│   ├── loader.py     # project type detection + custom skills
│   └── bundled/      # skill convention files
├── actions/          # file and shell operations
│   ├── file_ops.py   # read, write, edit files
│   ├── shell_ops.py  # git and shell commands (shell=False)
│   ├── safety.py     # risk classification
│   └── verify.py     # post-change test/lint verification
├── commands/         # CLI commands
│   ├── init.py
│   ├── ask.py        # with --file flag
│   ├── do.py         # with diff preview + verify
│   ├── repl.py       # interactive REPL
│   ├── git_cmd.py    # git commit/push/diff/status
│   ├── why.py
│   ├── undo.py
│   └── status.py
├── utils/            # shared utilities
│   ├── config.py     # env var + TOML loading
│   ├── toml_config.py
│   ├── ui.py         # Terminal Luxury output + streaming + diffs
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
