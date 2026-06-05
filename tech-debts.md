# Technical Debt & Improvements

## Performance

### String concatenation in render loops → `''.join()`
`render_ansi`, `render_html`, and `render_svg` build lines via `line += f'...'` inside a loop. Use `''.join(...)` with a generator expression for each row, then `'\n'.join()` for all rows.

**Benefit:** ~10–20% faster rendering for large outputs.

---

## Dependencies & Python Version

### Consider bumping to `requires-python = ">=3.11"`
Python 3.10 goes EOL in October 2026. Python 3.11 is ~25% faster on average, and `tomllib` (for future config file support) is stdlib in 3.11+.

**Risk:** Drops 3.10 users (minor at this point).

---

## Code Quality & Type Safety

### Unused variable `tmp` in `download.py:67`
`tmp` is assigned from `tempfile.NamedTemporaryFile(...)` but never referenced after the two method calls. Either remove the assignment or use a context manager.

### Missing error wrapping for invalid local images
If `Image.open()` fails on a corrupt local file, the raw PIL exception propagates to the user (URL downloads get nice `DownloadError` wrapping). Wrap in try/except and raise a typed error.

---

## Tooling (Critical Gaps)

### Add a linter/formatter (`ruff`)
No `ruff`, `black`, `isort`, or `flake8` in dev deps or `pyproject.toml`. Type/modernization issues slip through.

**Approach:**
- Add `ruff` to `[project.optional-dependencies] dev`
- Add `[tool.ruff]` section to `pyproject.toml`
- Add `ruff check .` step to PR checklist in AGENTS.md

### Add pre-commit hooks
No `.pre-commit-config.yaml`. Ruff can auto-fix many issues before commit.

### Add a type checker (`mypy`)
AGENTS.md mandates strict typing but there's no type checker configured. Add `mypy` to dev deps and a `[tool.mypy]` section with `strict = true`.

### Add CI/CD (GitHub Actions)
No `.github/workflows/` directory. Even a simple CI (run `pytest`, `ruff check` on push/PR) would improve confidence before merging.

**Minimal workflow:**
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: pytest -v
      - run: ruff check
```

---

## Testing

### Extract shared test image fixture
At least 7 tests in `test_cli.py` create the same gradient PNG inline — ~28 lines of duplication. Use a single `pytest.fixture`.

### Move `MockResponse` to a shared `conftest.py`
Two nearly identical mock response classes exist in `test_cli.py` and `test_download.py`. Share one in `tests/conftest.py`.

### `render_html()` is never tested
`ascii.py:86–102` — `render_html` is defined but has zero test coverage. Add 2–3 tests covering basic output, empty grid, and XML escaping.

### No direct unit test for `render_ansi()`
Tested indirectly via CLI invocations but not as a unit.
