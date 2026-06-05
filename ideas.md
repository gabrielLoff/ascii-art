# Future Feature Ideas

## Ordered / Floyd-Steinberg Dithering (`--dither`)
**Add dithering to improve quality with limited character ramps.**

**Why:** With a small ramp (e.g., `shade-blocks` with 4 chars), smooth gradients flatten to harsh bands. Dithering distributes quantization error across neighboring pixels, simulating intermediate brightness levels and preserving detail.

**Approach:**
- Add `--dither` flag (e.g., `--dither floyd` or `--dither ordered`)
- Floyd-Steinberg algorithm (~30 lines) distributes error to adjacent pixels
- Ordered dither uses a Bayer matrix for a structured pattern
- Pure ASCII (no color) benefits most, but also improves color output

**Considerations:**
- Slightly slower conversion
- Output character changes — some may prefer the clean "posterized" look
- Best as opt-in, not default

---

## Text Overlay / Caption (`--caption`)
**Add a caption below or overlaid on the ASCII art.**

**Why:** Turns an image into a meme-style ASCII with a caption — high fun factor for sharing.

**Approach:**
- Add `--caption "text"` option to the `ascii` command
- Append caption rows below the grid after conversion
- Or overlay as a banner on top of the art

**Considerations:**
- Slightly opinionated — could be a separate command (`cli_art caption`)
- Caption should use the same character ramp/color treatment

---

## Aspect Ratio Control (`--aspect`)
**Let users override the automatic height calculation.**

Currently height = `width * aspect_ratio * 0.45` (hardcoded font aspect correction factor).

`--aspect 0.5` would override the magic number 0.45. `--height N` could also be added for explicit height.

**Why:** The 0.45 factor works for most terminals but not all (different font aspect ratios). Power users may want explicit control.

**Approach:**
- Add `--aspect` option (float, default `0.45`)
- Alternatively or additionally, add `--height` option (int, overrides automatic calculation)
- If both are provided, `--height` takes precedence
- Validate values (aspect > 0, height > 0)

**Considerations:**
- Should not break existing behavior — default remains 0.45
- Could also add `--height` for explicit row count

---

## Batch / Directory Processing (`cli_art batch`)
**Convert an entire directory of images to ASCII art in one command.**

**Why:** The current tool processes one image at a time. Users with a folder of photos (e.g., for a gallery, a blog series, or a terminal-based photo album) need to iterate manually. Batch mode saves time and enables shell pipelines.

**Approach:**
- New subcommand `cli_art batch <directory> [--output-dir <path>]` (or add `--batch` to the existing `ascii` command)
- Iterate over common image extensions (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`)
- For each file, run the full conversion pipeline with the same options (width, theme, mode, etc.)
- Save each result to `--output-dir` (default: same directory with `.txt`/`.html`/`.svg` appended)
- Show a progress bar (use `rich.progress` for a polished feel)

**Considerations:**
- Error handling: skip corrupt images with a warning instead of aborting the whole batch
- Could accept glob patterns directly: `cli_art ascii "*.jpg"` as a lighter alternative
- Adds a new command — follows the existing `cli_art themes` pattern

---

## Watch / Live-Reload Mode (`cli_art watch`)
**Watch a source image (or directory) and re-render the ASCII art every time the file changes.**

**Why:** Great for creative workflows — edit a photo in GIMP/Photoshop, save, and see the ASCII version update in the terminal instantly. Also fun for live webcam feeds (pipe a periodically updated snapshot).

**Approach:**
- New subcommand `cli_art watch <source>` with all the usual options (width, theme, mode, etc.)
- Use `watchdog` library (or a simple polling loop with `time.sleep`) to detect file modification
- Clear the terminal and re-render on each change
- Show a small status line at the bottom with the file watched and last-rendered timestamp

**Considerations:**
- Adds `watchdog` as an optional dependency (or implement lightweight polling with `os.stat().st_mtime`)
- Terminal flicker — could use `shutil.get_terminal_size()` to size the output and avoid reflow
- Polling interval should be configurable (`--interval 0.5`) to avoid busy-waiting

---

## Braille Dot-Matrix Mode (`--mode braille`)
**Render images using 2×2 braille dot patterns for significantly higher resolution per character.**

**Why:** The existing `braille` theme maps brightness linearly to braille characters, losing the dot-level structure. A dedicated mode that maps 2×2 pixel blocks to individual braille dots produces roughly 4× the vertical resolution — photorealistic ASCII art.

**Approach:**
- New mapping mode: `--mode braille` (distinct from the existing `--theme braille`)
- For each 2×2 pixel block in the source image, compute which of the 4 dots should be "on" (based on brightness threshold)
- Map each 2×2 pattern to the corresponding Unicode braille codepoint (U+2800–U+28FF)
- Preserve color by averaging the 4 pixels for the foreground color
- Extend the `modes.py` module with a `braille_map()` function

**Considerations:**
- Braille characters render at roughly half the width of regular characters in most terminals — the effective aspect ratio changes
- Block size could be configurable (`--braille-block 2x2`, or even 1×2 for "half-height" dots)
- Some terminals/fonts render braille glyphs poorly — should be opt-in, not the default
- The resolution boost makes this a strong candidate for the default edge/texture mode

---

## Color Palette Reduction (`--palette` / `--palette-file`)
**Reduce the image to a limited color palette before ASCII conversion, creating a posterized/stylized look.**

**Why:** Full true-color output is impressive but noisy. A restricted palette (2–16 colors) gives a retro, screen-printed, or comic-book feel — matching the aesthetic of classic ASCII art. Palette files let users import their own brand colors.

**Approach:**
- Add `--palette N` (integer, 2–256) to quantize colors to N levels using Pillow's `Image.quantize()`
- Add `--palette-file <image>` to extract a custom palette from a reference image
- Apply palette reduction before the character mapping step (the mapper still sees the reduced colors)
- Works with all existing modes (`linear`, `edge`, `threshold`, `color-to-char`)

**Considerations:**
- Quantization + dithering (from ideas.md) are natural companions — `--dither floyd --palette 8` together
- A 2-color palette + threshold mode recreates the classic "monochrome ASCII" look
- Palette extraction from a reference image lets users match brand colors or a specific aesthetic

---

## Text-to-ASCII Banner (`cli_art banner`)
**Generate ASCII art text banners from plain text (like figlet, but integrated).**

**Why:** This expands `cli-art` from "image to ASCII" to a general-purpose ASCII art tool. Users can create headers for their READMEs, terminal welcome messages, or forum signatures without installing a separate tool. It fits naturally — the existing rendering pipeline (ANSI, HTML, SVG) applies directly.

**Approach:**
- New subcommand `cli_art banner <text>` (e.g., `cli_art banner "Hello" --width 40`)
- Use a bundled set of basic bitmap font glyphs (e.g., 6×8 pixel matrices stored as a dict in a new `fonts.py` module)
- Or integrate with the `pyfiglet` library (wrapper around figlet fonts) as an optional dependency
- Size the output to `--width` with proportional character spacing
- Apply the same output options: `--output`, `--theme` (for the character ramp), `--no-color`

**Considerations:**
- Bundling bitmap fonts keeps the dependency light; pyfiglet adds ~200K but unlocks 100+ fonts
- Should not steal the `--chars`/`--theme` meaning — here those control the fill characters inside the glyphs
- Could later combine with caption (from ideas.md): `--caption` on a banner creates a two-line header

---

## Animated SVG Output (`--animate`)
**Generate an animated SVG that reveals the ASCII art progressively (typewriter, fade-in, or scan-line effect).**

**Why:** A static SVG is nice, but an animated SVG — viewable in any browser, embeddable in GitHub READMEs, or sent as a standalone file — is eye-catching and shareable. This adds production value with no runtime dependencies.

**Approach:**
- Add `--animate` flag (only meaningful with `--output file.svg`)
- Three animation styles: `typewriter` (characters appear left-to-right, top-to-bottom), `scan` (horizontal bars reveal the image), `fade` (all characters fade in)
- Generate CSS `@keyframes` inside the SVG with staggered `animation-delay` per character/row
- The file size grows linearly with grid size, but even a 100×50 grid produces < 50KB SVG

**Considerations:**
- Only works for SVG output — ANSI terminals can't play CSS animations
- Animation parameters (`--duration 3`, `--delay 0.05`) for precise control
- The typewriter effect pairs well with the caption idea from ideas.md — caption fades in first, then the art
- Could be a separate output format choice or a distinct command
