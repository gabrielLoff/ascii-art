import shutil
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator
import typer

from .ascii import CHARS, ImageError, image_to_ascii_grid, render_ansi, render_html, render_plain, render_svg
from .clipboard import ClipboardError, copy_to_clipboard
from .config import load_config
from .download import DownloadError, download_image, is_url
from .themes import THEMES, resolve_chars, theme_names

from .animate import AnimationError, extract_frames, frames_to_grids, play_ansi_animation, render_html_animation

app = typer.Typer()


_MODES = ["linear", "edge", "threshold", "color-to-char"]


def _complete_theme(
    ctx: typer.Context,
    incomplete: str,
) -> list[str]:
    names = theme_names()
    if incomplete:
        return [n for n in names if n.startswith(incomplete)]
    return names


def _complete_mode(
    ctx: typer.Context,
    incomplete: str,
) -> list[str]:
    if incomplete:
        return [m for m in _MODES if m.startswith(incomplete)]
    return list(_MODES)


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


def _default_width() -> int:
    """Return terminal width, falling back to 80 when not in a TTY."""
    return shutil.get_terminal_size().columns


@app.command()
def ascii(
    source: str = typer.Argument(..., help="Path or URL of the image"),
    width: int | None = typer.Option(None, "--width", "-w", help="Output width in characters (default: terminal width, fallback 80)"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Save to file (.html / .svg for those formats, otherwise ANSI text)"
    ),
    invert: bool | None = typer.Option(
        None, "--invert/--no-invert", help="Invert brightness mapping"
    ),
    chars: str | None = typer.Option(
        None,
        "--chars",
        help="Custom character ramp for brightness mapping "
             "(from dark to bright). Default: ' .:-=+*#%@'",
    ),
    theme: str | None = typer.Option(
        None,
        "--theme",
        autocompletion=_complete_theme,
        help="Named character ramp theme. Cannot be combined with --chars. "
             "Use 'cli_art themes' to list available themes.",
    ),
    mode: str | None = typer.Option(
        None,
        "--mode",
        autocompletion=_complete_mode,
        help="Character mapping mode: linear, edge, threshold, color-to-char (default: linear)",
    ),
    no_color: bool | None = typer.Option(
        None,
        "--no-color/--color",
        help="Output plain text without ANSI color codes",
    ),
    copy: bool | None = typer.Option(
        None,
        "--copy",
        "-c",
        help="Copy the rendered ASCII art to the system clipboard",
    ),
    palette: int | None = typer.Option(
        None,
        "--palette",
        help="Reduce colors to N levels (2–256) before ASCII conversion",
        min=2,
        max=256,
        clamp=True,
    ),
    palette_file: Path | None = typer.Option(
        None,
        "--palette-file",
        help="Extract color palette from a reference image",
    ),
) -> None:
    """Convert an image to color ASCII art."""
    config = load_config()

    width = width if width is not None else config.get("width", _default_width())
    invert = invert if invert is not None else config.get("invert", False)
    no_color = no_color if no_color is not None else config.get("no_color", False)
    chars = chars if chars is not None else config.get("chars")
    theme = theme if theme is not None else config.get("theme")
    mode = mode if mode is not None else config.get("mode", "linear")
    palette = palette if palette is not None else config.get("palette")
    palette_file_raw = palette_file if palette_file is not None else config.get("palette_file")
    palette_file = Path(palette_file_raw) if palette_file_raw is not None else None

    if chars is not None and len(chars) == 0:
        raise typer.BadParameter("--chars must not be an empty string")

    if palette_file is not None and not palette_file.exists():
        raise typer.BadParameter(f"Palette file not found: {palette_file}")

    try:
        active_chars = resolve_chars(chars, theme)
    except ValueError as e:
        raise typer.BadParameter(str(e))

    try:
        with _resolve_image(source) as local_path:
            grid = image_to_ascii_grid(
                local_path,
                width=width,
                invert=invert,
                chars=active_chars,
                mode=mode,
                palette=palette,
                palette_file=palette_file,
            )
    except (DownloadError, ImageError) as e:
        raise typer.BadParameter(str(e))

    output_text = render_plain(grid) if no_color else render_ansi(grid)

    if output is not None:
        suffix = output.suffix.lower()
        if suffix == ".html":
            content = render_html(grid)
        elif suffix == ".svg":
            content = render_svg(grid)
        else:
            content = output_text
        output.write_text(content, encoding="utf-8")
        typer.echo(f"Saved to {output}")

    if copy:
        try:
            copy_to_clipboard(output_text)
            typer.echo("Copied to clipboard")
        except ClipboardError as e:
            typer.echo(f"Warning: {e}", err=True)

    typer.echo(output_text)


@app.command()
def animate(
    source: str = typer.Argument(..., help="Path or URL of an animated GIF"),
    width: int | None = typer.Option(None, "--width", "-w", help="Output width in characters (default: terminal width, fallback 80)"),
    fps: float | None = typer.Option(None, "--fps", "-f", help="Playback speed in frames per second (default: GIF native timing)"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Save to HTML file (otherwise play in terminal)"
    ),
    invert: bool | None = typer.Option(
        None, "--invert/--no-invert", help="Invert brightness mapping"
    ),
    chars: str | None = typer.Option(
        None,
        "--chars",
        help="Custom character ramp for brightness mapping "
             "(from dark to bright). Default: ' .:-=+*#%@'",
    ),
    theme: str | None = typer.Option(
        None,
        "--theme",
        autocompletion=_complete_theme,
        help="Named character ramp theme. Cannot be combined with --chars. "
             "Use 'cli_art themes' to list available themes.",
    ),
    mode: str | None = typer.Option(
        None,
        "--mode",
        autocompletion=_complete_mode,
        help="Character mapping mode: linear, edge, threshold, color-to-char (default: linear)",
    ),
    no_color: bool | None = typer.Option(
        None,
        "--no-color/--color",
        help="Output plain text without ANSI color codes",
    ),
    max_frames: int | None = typer.Option(
        None, "--max-frames", help="Maximum number of frames to process (default: 500)",
    ),
    palette: int | None = typer.Option(
        None,
        "--palette",
        help="Reduce colors to N levels (2–256) before ASCII conversion",
        min=2,
        max=256,
        clamp=True,
    ),
    palette_file: Path | None = typer.Option(
        None,
        "--palette-file",
        help="Extract color palette from a reference image",
    ),
) -> None:
    """Convert an animated GIF to a looping ASCII animation."""
    config = load_config()

    width = width if width is not None else config.get("width", _default_width())
    fps = fps if fps is not None else config.get("fps")
    invert = invert if invert is not None else config.get("invert", False)
    no_color = no_color if no_color is not None else config.get("no_color", False)
    chars = chars if chars is not None else config.get("chars")
    theme = theme if theme is not None else config.get("theme")
    mode = mode if mode is not None else config.get("mode", "linear")
    max_frames = max_frames if max_frames is not None else config.get("max_frames", 500)
    palette = palette if palette is not None else config.get("palette")
    palette_file_raw = palette_file if palette_file is not None else config.get("palette_file")
    palette_file = Path(palette_file_raw) if palette_file_raw is not None else None

    if chars is not None and len(chars) == 0:
        raise typer.BadParameter("--chars must not be an empty string")

    if palette_file is not None and not palette_file.exists():
        raise typer.BadParameter(f"Palette file not found: {palette_file}")

    try:
        active_chars = resolve_chars(chars, theme)
    except ValueError as e:
        raise typer.BadParameter(str(e))

    try:
        with _resolve_image(source) as local_path:
            frames = extract_frames(local_path, max_frames=max_frames)
    except (DownloadError, AnimationError, ImageError) as e:
        raise typer.BadParameter(str(e))

    if len(frames) == 0:
        raise typer.BadParameter("No frames found in the source")

    animated = frames_to_grids(frames, width, active_chars, mode, palette=palette, palette_file=palette_file)

    if output is not None:
        suffix = output.suffix.lower()
        if suffix == ".svg":
            raise typer.BadParameter("SVG animation output is not supported yet")
        html = render_html_animation(animated, fps or 10.0)
        output.write_text(html, encoding="utf-8")
        typer.echo(f"Saved to {output}")
    else:
        try:
            play_ansi_animation(animated, fps=fps, no_color=no_color)
        except AnimationError as e:
            raise typer.BadParameter(str(e))


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
