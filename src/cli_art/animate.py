import sys
import time
from pathlib import Path
from typing import Any

from PIL import Image

from .ascii import CHARS, AsciiGrid, _apply_palette, _escape_xml, _image_to_grid, render_ansi, render_plain


def extract_frames(path: str | Path, max_frames: int = 500) -> list[tuple[Image.Image, int]]:
    img = Image.open(path)
    frames: list[tuple[Image.Image, int]] = []
    try:
        while True:
            frame = img.copy()
            if frame.mode in ("P", "PA"):
                frame = frame.convert("RGBA")
            if frame.mode == "RGBA":
                background = Image.new("RGBA", frame.size, (0, 0, 0, 255))
                background.paste(frame, mask=frame)
                frame = background.convert("RGB")
            elif frame.mode != "RGB":
                frame = frame.convert("RGB")

            delay = max(20, img.info.get("duration", 100))
            frames.append((frame, delay))
            if len(frames) >= max_frames:
                break
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    return frames


def frames_to_grids(
    frames: list[tuple[Image.Image, int]],
    width: int,
    active: str,
    mode: str,
    palette: int | None = None,
    palette_file: str | Path | None = None,
) -> list[tuple[AsciiGrid, int]]:
    result: list[tuple[AsciiGrid, int]] = []
    for frame, delay in frames:
        reduced = _apply_palette(frame, palette=palette, palette_file=palette_file)
        grid = _image_to_grid(reduced, width, active, mode)
        result.append((grid, delay))
    return result


def _render_frame_html(grid: AsciiGrid) -> str:
    lines: list[str] = []
    for row in grid:
        lines.append("".join(
            f'<span style="color:rgb({r},{g},{b})">{_escape_xml(char)}</span>'
            for char, (r, g, b) in row
        ))
    return "\n".join(lines)


def _escape_js(s: str) -> str:
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def render_html_animation(animated_grids: list[tuple[AsciiGrid, int]], fps: float) -> str:
    delay_ms = int(1000.0 / fps)
    frame_strings = [_render_frame_html(grid) for grid, _ in animated_grids]
    js_frames = ",\n".join(
        "`" + _escape_js(f) + "`" for f in frame_strings
    )
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="background:#000;margin:0;">
<pre id="frame" style="color:#fff;line-height:1;font-size:6px;letter-spacing:0;display:inline-block;">
</pre>
<script>
var frames = [{js_frames}];
var index = 0;
setInterval(function() {{
  document.getElementById('frame').innerHTML = frames[index];
  index = (index + 1) % frames.length;
}}, {delay_ms});
</script>
</body>
</html>"""


def play_ansi_animation(
    animated_grids: list[tuple[AsciiGrid, int]],
    fps: float | None = None,
    no_color: bool = False,
) -> None:
    render_fn = render_plain if no_color else render_ansi
    delay_base = 1000.0 / fps if fps is not None else None
    is_tty = sys.stdout.isatty()

    for i, (grid, native_delay) in enumerate(animated_grids):
        delay = delay_base if delay_base is not None else native_delay / 1000.0
        output = render_fn(grid)
        if i > 0 and is_tty:
            output = "\033[H" + output
        sys.stdout.write(output)
        sys.stdout.flush()
        if is_tty:
            time.sleep(delay)


class AnimationError(Exception):
    """Raised when animation processing fails."""
