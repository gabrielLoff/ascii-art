from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

import typer

from .ascii import CHARS, image_to_ascii_grid, render_ansi, render_html
from .download import DownloadError, download_image, is_url
from .themes import THEMES, resolve_chars, theme_names

app = typer.Typer()


def _complete_theme(
    ctx: typer.Context,
    incomplete: str,
) -> list[str]:
    names = theme_names()
    if incomplete:
        return [n for n in names if n.startswith(incomplete)]
    return names


@contextmanager
def _resolve_image(source: str) -> Iterator[Path]:
    if is_url(source):
        with download_image(source) as path:
            yield path
    else:
        path = Path(source)
        if not path.exists():
            raise typer.BadParameter(f"File not found: {source}")
        yield path


def _ramp_preview(ramp: str, width: int = 24) -> str:
    if len(ramp) == 1:
        return ramp * width
    return "".join(
        ramp[min(int(i / width * (len(ramp) - 1)), len(ramp) - 1)]
        for i in range(width)
    )


@app.command()
def ascii(
    source: str = typer.Argument(..., help="Path or URL of the image"),
    width: int = typer.Option(80, "--width", "-w", help="Output width in characters"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Save to file (.html for HTML, otherwise ANSI text)"
    ),
    invert: bool = typer.Option(
        False, "--invert", help="Invert brightness mapping"
    ),
    chars: Optional[str] = typer.Option(
        None,
        "--chars",
        help="Custom character ramp for brightness mapping "
             "(from dark to bright). Default: ' .:-=+*#%@'",
    ),
    theme: Optional[str] = typer.Option(
        None,
        "--theme",
        autocompletion=_complete_theme,
        help="Named character ramp theme. Cannot be combined with --chars. "
             "Use 'cli_art themes' to list available themes.",
    ),
) -> None:
    """Convert an image to color ASCII art."""
    if chars is not None and len(chars) == 0:
        raise typer.BadParameter("--chars must not be an empty string")

    try:
        active_chars = resolve_chars(chars, theme)
    except ValueError as e:
        raise typer.BadParameter(str(e))

    try:
        with _resolve_image(source) as local_path:
            grid = image_to_ascii_grid(local_path, width=width, invert=invert, chars=active_chars)
    except DownloadError as e:
        raise typer.BadParameter(str(e))

    if output is not None:
        if output.suffix == ".html":
            content = render_html(grid)
        else:
            content = render_ansi(grid)
        output.write_text(content, encoding="utf-8")
        typer.echo(f"Saved to {output}")

    typer.echo(render_ansi(grid))


@app.command()
def themes() -> None:
    """List available character ramp themes with previews."""
    typer.echo("Available themes:\n")
    for name in sorted(THEMES):
        ramp = THEMES[name]
        preview = _ramp_preview(ramp)
        typer.echo(f"  {name:<20} {ramp:<12} {preview}")
    typer.echo(f"\nDefault ramp: {CHARS!r}")


if __name__ == "__main__":
    app()
