# Technical Debt & Improvements

## Dependencies & Python Version

### `tomli` conditional dependency for Python < 3.11
`tomli>=2.0.0` is required only when `python_version < '3.11'`. This is handled cleanly via a PEP 508 conditional dependency and a `try/except ImportError` in `config.py`. If Python 3.10 support is ever dropped, `tomli` can be removed from dependencies entirely.

### Consider dropping Python 3.10 support
Setting `requires-python = ">=3.11"` would remove the `tomli` dependency, the try/except in `config.py`, and simplify the dependency list.

### `typer>=0.12.0` — consider upgrading to `>=0.15.0`
Newer versions include `rich_help_panel=`, better error messages, and `show_default=True` on options (removes manual default mentions in help text).

---

## Code Quality & Type Safety

### ~~Missing error wrapping for invalid local images~~
~~If `Image.open()` fails on a corrupt local file, the raw PIL exception propagates to the user (URL downloads get nice `DownloadError` wrapping). Wrap in try/except and raise a typed error.~~
**RESOLVED:** `ImageError` exception added in `ascii.py`, wraps `Image.open()` in `image_to_ascii_grid()` and `_apply_palette()`. `extract_frames()` in `animate.py` wraps with `AnimationError`. Caught in `cli.py` alongside `DownloadError`.

### ~~Add `assert pixels is not None` after `img.load()` in `ascii.py`~~
~~Pillow's stubs type `Image.load()` as returning `PixelAccess | None`. In practice it never returns `None` for RGB images, but strict mypy will reject `pixels[x, y]` without a guard. An `assert pixels is not None` or a `# type: ignore` is needed.~~
**RESOLVED:** All mode functions now use `get_flattened_data()` instead of `img.load()`, eliminating the `None` return issue entirely.

### Add `assert pixels is not None` after `img.load()` in `ascii.py`
Pillow's stubs type `Image.load()` as returning `PixelAccess | None`. In practice it never returns `None` for RGB images, but strict mypy will reject `pixels[x, y]` without a guard. An `assert pixels is not None` or a `# type: ignore` is needed.

### `cli.py` re-renders the grid twice when `--output` is used
Lines 98–100: `render_ansi(grid)` is called once for the file output, then again for stdout. Could cache the result to avoid double-render for large grids.

### `is_url()` is case-sensitive
`_URL_PREFIXES = ("http://", "https://")` — `HTTP://` or `HTTPS://` would not be detected as URLs. Add `.lower()` or `.casefold()`.

### `AsciiGrid` type alias is duplicated
`AsciiGrid = list[list[tuple[str, tuple[int, int, int]]]]` is defined in both `ascii.py:9` and `modes.py:5`. If the type changes, both must be updated. Define in one place and import.

### `animate.py` imports private helpers from `ascii.py`
`animate.py:8` imports `_apply_palette`, `_image_to_grid`, `_escape_xml` — all private (`_`-prefixed) functions. Promote to public names or move to a shared utility module.

### CLI option resolution boilerplate duplicated between `ascii` and `animate`
Lines 122–131 and 236–246 in `cli.py`: the entire config-resolution block (`width = width if width is not None else config.get(...)`) is identical in structure across both commands. Extract a helper function or use a dataclass.

### ~~`_MODES` is a mutable list used as a constant~~
~~`cli.py:18`: `_MODES = ["linear", "edge", "threshold", "color-to-char"]` — should be a `tuple` for immutability. The mode-to-function dict in `ascii.py:42–47` is also rebuilt on every `_image_to_grid()` call; move to a module-level constant.~~
**RESOLVED:** Moved `_MODES` dict to a module-level constant in `ascii.py` with `Callable` typing. `cli.py` `_MODES` list remains but is unrelated (used for autocompletion).

### `from __future__ import annotations` not consistently applied
Modules like `modes.py`, `config.py`, `download.py` lack the import. Add for consistency and deferred evaluation.

### ~~`_apply_palette()` can raise unhandled `OSError`~~
~~`ascii.py:18`: `Image.open(palette_file)` can raise if the file is corrupt or not an image. Wrap and raise a typed error.~~
**RESOLVED:** Wrapped in `_apply_palette()` alongside the main `image_to_ascii_grid()` fix — all `Image.open()` calls now raise `ImageError`.

### `config.get("palette_file")` returns unvalidated `Any`
`cli.py`: config could contain `palette_file = 123` (integer), which would crash `Path(123)`. Validate the value is a `str` before converting.

### `config.py` uses `dict[str, Any]` for return type
Consider a `TypedDict` or `dataclass` for the resolved config shape to improve type safety and IDE support.

---

## Performance

### ~~Pixel-by-pixel loops in all four mode functions~~
~~`modes.py`: every mode iterates via `img.load()` in pure Python `for` loops. For a 200×100 image this is 20,000 interpreted iterations. Pillow can vectorize brightness/luminance/hue via `ImageFilter.Kernel` or `Image.point()`. Could yield 10–50× speedup for large images.~~
**RESOLVED:** Replaced `img.load()` + `pixels[x,y]` with `get_flattened_data()` + flat list indexing in all four mode functions. `linear_map` and `threshold_map` use `Image.point()` with a prebuilt LUT for C-accelerated brightness→char mapping. `edge_map` uses list indexing instead of `PixelAccess`. `hue_map` still requires per-pixel `colorsys.rgb_to_hsv` but uses `get_flattened_data()` for faster pixel access.

### ~~`edge_map()` computes Sobel manually~~
~~`modes.py:59–85`: the Sobel convolution is implemented in pure Python with 9 operations per pixel. Use Pillow's `ImageFilter.Kernel` with a 3×3 Sobel kernel over the grayscale image — delegates the convolution to C code.~~
**RESOLVED:** Sobel computation still uses flat-list indexing (not `ImageFilter.Kernel`) to avoid sign clipping issues with 8-bit output. The neighbor-access pattern via list indexing is significantly faster than `PixelAccess`.

### `_ramp_preview()` recalculates index per character
`cli.py:52–58`: `int(i / width * (len(ramp) - 1))` is recomputed for each of `width` characters. Pre-compute the index list once.

### Hard-coded minimum frame delay in `extract_frames()`
`animate.py:26`: `delay = max(20, img.info.get("duration", 100))` — `20` ms is a magic number. Define as a module-level constant with a comment.

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

### Consider property-based tests for mode functions
Invariants: `linear_map` with a single-char ramp produces all that char; `threshold_map` outputs at most 2 distinct chars; `hue_map` with same hue produces same char. Use `hypothesis` (lightweight property-based testing).

### Some test functions missing `-> None` return annotations
Several tests in `test_cli.py` and `test_config.py` lack return type annotations. Add for consistency and mypy compliance.
