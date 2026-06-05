# Future Feature Ideas

## Plain ASCII Output (`--no-color`)
**Add a flag to output clean, shareable plain text without ANSI color codes.**

**Why:** Enables use in markdown code blocks, READMEs, terminals without true color support, or any environment where ANSI codes are unwanted.

**Approach:**
- Add `--no-color` / `--plain` flag to the `ascii` command
- Add a `render_plain()` function in `ascii.py` that outputs characters only (no ANSI escapes)
- When `--no-color` is set, call `render_plain()` instead of `render_ansi()`




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
