from .ascii import CHARS

THEMES: dict[str, str] = {
    "eighths": " ▁▂▃▄▅▆▇█",
    "vertical-bars": " ▏▎▍▌▋▊▉█",
    "quadrant": " ▘▝▀▖▌▞▛▜█",
    "stippled": " .·:•oO0@%#█",
    "halftone": " .·:*%#@",
    "geometric": " ○◔◐◕●▪▫◻◼⬡◆◇⬢",
    "mono": " .·●",
    "braille": " ⠀⠁⠂⠄⡀⢀⠠⠐⠈⠘⠨⠰⠱⠲⠶⠷⠿",
    "shade-blocks": " ░▒▓█",
    "classic": " .,:;i1IlLCH$@#",
    "numerical": " 123456789",
}


def theme_names() -> list[str]:
    """Return sorted list of available theme names."""
    return sorted(THEMES)


def resolve_chars(chars: str | None, theme: str | None) -> str:
    if chars is not None and theme is not None:
        raise ValueError("--chars and --theme are mutually exclusive")
    if theme is not None:
        if theme not in THEMES:
            available = ", ".join(sorted(THEMES))
            raise ValueError(
                f"Unknown theme '{theme}'. Available themes: {available}"
            )
        return THEMES[theme]
    return chars if chars is not None else CHARS
