# AGENTS.md — cli-art

## Commands

```
source .venv/bin/activate          # Activate virtual env
pip install -e ".[dev]"            # Install package + dev deps
cli_art                            # Run the CLI
python -m cli_art                  # Run via module
pytest -v                          # Run tests
```

## Git & Branching

- Every feature must be developed on a new branch with the prefix `feature/` (e.g. `feature/add-rainbow-theme`).
- Merges to `main` are done exclusively via GitHub Pull Request — never push directly to `main`.
- Before opening a PR, run `pytest -v` and ensure all tests pass.

## Available Subagents

- **`debugger`** — **MUST** use this when you encounter any error (runtime, test failure, type/lint error, unexpected behavior). Do NOT attempt to fix errors directly. It reproduces, diagnoses, and fixes the problem, asking for input when unsure.
- **`consultant`** — use this before committing changes or when you want a fresh code review. It reads code without context and reports on clarity, structure, and convention compliance.
- **`creative`** — use this when you want suggestions for new features or evolutions of existing features. It reads the project and presents ideas for you to validate — it never implements anything.
- **`feature-architect`** — use this after a feature is proposed but before implementation. It reads the project and produces structured implementation plans with technical trade-offs, pros/cons, and effort estimates.

## Project Architecture

```
cli-art/
├── pyproject.toml          # hatchling build, deps, entry point
├── README.md               # User-facing docs
├── AGENTS.md               # This file
├── opencode.json           # opencode config
├── .gitignore
├── .opencode/
│   └── agents/
│       ├── debugger.md     # Debugging subagent
│       ├── consultant.md   # Code review subagent
│       ├── creative.md           # Feature ideation subagent
│       └── feature-architect.md  # Implementation planning subagent
├── src/
│   └── cli_art/
│       ├── __init__.py
│       ├── __main__.py     # Enables `python -m cli_art`
│       ├── cli.py          # typer app + commands (thin)
│       ├── ascii.py        # Image-to-ASCII conversion logic
│       ├── download.py     # URL download + temp file management
│       └── themes.py       # Character ramp themes
└── tests/
    ├── __init__.py
    ├── test_cli.py         # CLI integration tests
    ├── test_download.py    # Download module unit tests
    └── test_themes.py      # Theme resolution unit tests
```

- **`cli.py`** — defines the `typer.Typer()` app and all commands. Keep this file thin — import logic from separate modules.
- **`ascii.py`** — image-to-ASCII conversion logic.
- **`download.py`** — URL detection, image download with size limits, temp file cleanup via context manager.
- **`themes.py`** — theme data and `resolve_chars()` helper.
- **`__main__.py`** — calls `app()` so `python -m cli_art` works.
- **Tests** — use `typer.testing.CliRunner` for integration tests and standard pytest for unit tests. Mock `urllib.request.urlopen` for download tests — never hit real networks.
- **`opencode.json`** + `.opencode/agents/` — opencode subagent definitions. These should be tracked in git so the whole team (and AI) gets the same agents.

## CLI Conventions

- Entry point: `cli_art` (defined in `[project.scripts]` in pyproject.toml).
- Built with **typer** and **rich** for --help output.
- Commands use `typer.Argument()` / `typer.Option()` for parameters.
- Use `typer.Exit()` for controlled exits, `typer.echo()` for output (over plain `print` for consistency).

### Command naming

- Short, lowercase, hyphen-separated for multi-word commands (e.g. `make-banner`).
- Each command has a docstring that serves as its help text.
- A single top-level command can be a bare callback without subcommands if the tool does one thing.

## Testing

- Use `typer.testing.CliRunner` to invoke the app in tests.
- Use `tmp_path` (pytest built-in) for file I/O in tests — never hardcode paths.
- Generate test fixtures on the fly (e.g. create a small test image with Pillow) instead of committing static files.

## Code Style

### Typing (strict — required everywhere)

```python
from collections.abc import Sequence
from pathlib import Path

def greet(name: str, count: int = 1) -> str: ...
```

- Every function signature must have type annotations for all parameters and return types.
- Prefer `list[X]` / `dict[K, V]` over `List[X]` / `Dict[K, V]`.
- Prefer `from collections.abc import ...` over `typing` equivalents.
- Use `Path` for file paths, not raw strings.

### Naming

- `snake_case` for functions, variables, methods.
- `PascalCase` for classes.
- `UPPER_SNAKE` for constants.
- Private helpers prefixed with `_`.

### Imports

- standard library → third-party → local, separated by blank lines.
- Use absolute imports within the package.

### Error handling

- Raise `typer.BadParameter` for invalid input.
- Raise standard exceptions for programmer errors; let typer convert exceptions to clean exit messages.

### Commit style

- Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- Present tense, lowercase after prefix.
