# cli-art

Convert images to color ASCII art in your terminal.

## Installation

### Global install (recommended)

```bash
pip install git+https://github.com/yourusername/cli-art.git
```

This makes `cli_art` available system-wide.

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

# Control output width (default: 80)
cli_art ascii image.jpg --width 40

# Invert brightness mapping
cli_art ascii image.jpg --invert

# Use a custom character ramp
cli_art ascii image.jpg --chars "@%#*+=-:. "

# Use a named theme
cli_art ascii image.jpg --theme eighths

# List available themes
cli_art themes

# Save to file (.html preserves color, .txt keeps ANSI codes)
cli_art ascii image.jpg --output art.html
cli_art ascii image.jpg --output art.txt

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
|---|---|---|
| `image_path` | — | Path to the image file (required) |
| `--width` / `-w` | `80` | Output width in characters |
| `--output` / `-o` | — | Save to file (.html or .txt) |
| `--invert` | — | Invert brightness mapping |
| `--chars` | — | Custom character ramp (dark to bright). Mutually exclusive with `--theme` |
| `--theme` | — | Named theme. Mutually exclusive with `--chars` |

### Available themes

| Theme | Ramp | Vibe |
|---|---|---|
| `eighths` | ` ▁▂▃▄▅▆▇█` | Smooth gradient, photorealistic |
| `vertical-bars` | ` ▏▎▍▌▋▊▉█` | Scanline, techy |
| `quadrant` | ` ▘▝▀▖▌▞▛▜█` | Pixel-art, retro |
| `stippled` | ` .·:•oO0@%#█` | Sketchy, ink-drawing |
| `halftone` | ` .·:*%#@` | Newsprint, halftone |
| `geometric` | ` ○◔◐◕●▪▫◻◼⬡◆◇⬢` | Minimalist, vector-art |
| `mono` | ` .·●` | Minimal, editorial |

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
