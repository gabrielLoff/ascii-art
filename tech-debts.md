# Technical Debt & Improvements

## Dependencies & Python Version

### `tomli` conditional dependency for Python < 3.11
`tomli>=2.0.0` is required only when `python_version < '3.11'`. This is handled cleanly via a PEP 508 conditional dependency and a `try/except ImportError` in `config.py`. If Python 3.10 support is ever dropped, `tomli` can be removed from dependencies entirely.

---

## Code Quality & Type Safety

### Missing error wrapping for invalid local images
If `Image.open()` fails on a corrupt local file, the raw PIL exception propagates to the user (URL downloads get nice `DownloadError` wrapping). Wrap in try/except and raise a typed error.

### Add `assert pixels is not None` after `img.load()` in `ascii.py`
Pillow's stubs type `Image.load()` as returning `PixelAccess | None`. In practice it never returns `None` for RGB images, but strict mypy will reject `pixels[x, y]` without a guard. An `assert pixels is not None` or a `# type: ignore` is needed.

### `cli.py` re-renders the grid twice when `--output` is used
Lines 98–100: `render_ansi(grid)` is called once for the file output, then again for stdout. Could cache the result to avoid double-render for large grids.

### `is_url()` is case-sensitive
`_URL_PREFIXES = ("http://", "https://")` — `HTTP://` or `HTTPS://` would not be detected as URLs. Add `.lower()` or `.casefold()`.

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

### `render_html()` is never tested
`ascii.py:86–102` — `render_html` is defined but has zero test coverage. Add 2–3 tests covering basic output, empty grid, and XML escaping.

### No direct unit test for `render_ansi()`
Tested indirectly via CLI invocations but not as a unit.

### `MockResponse` imported from `conftest` is fragile
`test_cli.py` and `test_download.py` import `MockResponse` from `.conftest`. If the test layout changes, this breaks. Consider extracting to a separate `test_helpers.py` module.
