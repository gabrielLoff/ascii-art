# Future Feature Ideas

## URL Input Support
**Accept a URL as the image path (auto-download before processing).**

`cli_art ascii https://example.com/photo.jpg` would fetch the image, convert it, and display the result.

**Why:** Removes the friction of manually downloading images. Many fun use cases (profile pics, memes).

**Approach:** Detect URL pattern in the `image_path` argument, download to a temp file using `urllib` (stdlib, no extra deps), process as normal, clean up temp file.

**Considerations:**
- Need to distinguish URLs from local paths (check for `http://` or `https://` prefix)
- Use `urllib.request` from stdlib to avoid adding `requests` as a dependency
- Handle network errors gracefully (timeout, connection errors)
- Clean up temp file even on errors (use `tempfile.NamedTemporaryFile` or a try/finally block)
- File size limits? Could set a reasonable max (e.g., 10MB)

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
