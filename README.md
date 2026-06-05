# cli-art

Convert images to color ASCII art in your terminal.

## Installation

### Local / development install

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .
```

## Usage

```bash
# Convert an image to ASCII art
cli_art ascii path/to/image.jpg

# Control output width (default: auto-detect terminal width)
cli_art ascii image.jpg --width 40

# Use a URL instead of a local file
cli_art ascii https://example.com/photo.jpg

# Invert brightness mapping
cli_art ascii image.jpg --invert

# Use a custom character ramp
cli_art ascii image.jpg --chars "@%#*+=-:. "

# Use a named theme
cli_art ascii image.jpg --theme eighths

# List available themes
cli_art themes

# Save to file (.html, .svg preserve color; .txt keeps ANSI codes)
cli_art ascii image.jpg --output art.html
cli_art ascii image.jpg --output art.svg
cli_art ascii image.jpg --output art.txt

# Use a different mapping mode
cli_art ascii image.jpg --mode edge         # Sobel edge detection
cli_art ascii image.jpg --mode threshold    # Black & white posterization
cli_art ascii image.jpg --mode color-to-char # Map hue to characters

# Output plain text (no ANSI color codes)
cli_art ascii image.jpg --no-color

# Copy the result to the system clipboard
cli_art ascii image.jpg --copy

# Run via Python module
python -m cli_art ascii image.jpg
```

## Commands

| Command | Description |
|---|---|
| `ascii` | Convert an image to color ASCII art |
| `themes` | List available character ramp themes |

### `ascii` options

| Option | Default | Description |
|---|---|---|---|
| `source` | — | Path or URL of the image (required) |
| `--width` / `-w` | Auto (terminal width) | Output width in characters |
| `--output` / `-o` | — | Save to file (.html / .svg for those formats, otherwise ANSI text) |
| `--invert` / `--no-invert` | — | Invert brightness mapping |
| `--chars` | — | Custom character ramp (dark to bright). Mutually exclusive with `--theme` |
| `--theme` | — | Named theme. Mutually exclusive with `--chars` |
| `--mode` | `linear` | Mapping mode: `linear`, `edge`, `threshold`, `color-to-char` |
| `--no-color` / `--color` | — | Output plain text without ANSI codes |
| `--copy` / `-c` | — | Copy the result to the system clipboard |

### Available themes

| Theme | Ramp | Vibe |
|---|---|---|---|
| `braille` | ` ⠀⠁⠂⠄⡀⢀⠠⠐⠈⠘⠨⠰⠱⠲⠶⠷⠿` | High-resolution dot-matrix |
| `classic` | ` .,:;i1IlLCH$@#` | Traditional ASCII art |
| `eighths` | ` ▁▂▃▄▅▆▇█` | Smooth gradient, photorealistic |
| `geometric` | ` ○◔◐◕●▪▫◻◼⬡◆◇⬢` | Minimalist, vector-art |
| `halftone` | ` .·:*%#@` | Newsprint, halftone |
| `mono` | ` .·●` | Minimal, editorial |
| `numerical` | ` 123456789` | Numeric, unexpected |
| `quadrant` | ` ▘▝▀▖▌▞▛▜█` | Pixel-art, retro |
| `shade-blocks` | ` ░▒▓█` | Simple and bold |
| `stippled` | ` .·:•oO0@%#█` | Sketchy, ink-drawing |
| `vertical-bars` | ` ▏▎▍▌▋▊▉█` | Scanline, techy |

## Configuration

Create `~/.config/cli-art/config.toml` to set persistent defaults:

```toml
[defaults]
width = 100
invert = true
theme = "eighths"
mode = "edge"
no_color = false
```

CLI flags always override config values. Set `CLI_ART_CONFIG` to use a custom config path.

To install clipboard support (required for `--copy`):

```bash
pip install cli-art[clipboard]
```

## Shell Completion

Tab completion is supported for options like `--theme`:

```bash
# Install shell completion (run once)
cli_art --install-completion
```

After installation, restart your shell or source your rc file.

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

The `[dev]` extra includes `pyperclip` for clipboard tests. The clipboard feature can also be installed standalone via `pip install cli-art[clipboard]`.
