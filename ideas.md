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

## Animated GIF Support
**Convert animated GIFs into frame-by-frame ASCII animations.**

**Why:** GIFs become dynamic, impressive ASCII art — high fun factor and shareability.

**Approach:**
- Extract frames using Pillow (iterate over `n_frames`)
- Convert each frame to ASCII grid
- Output as ANSI animation (clear screen between frames with delay) or as an HTML page with JS frame cycling
- Could live as a separate subcommand: `cli_art animate`

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
