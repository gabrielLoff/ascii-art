import os
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


CONFIG_FILENAME = "config.toml"
ENV_VAR = "CLI_ART_CONFIG"
CONFIG_KEYS = frozenset({"width", "invert", "chars", "theme", "mode", "no_color"})


def _platform_config_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home() / "_appdata"))
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))


def config_path() -> Path:
    env = os.environ.get(ENV_VAR)
    if env:
        return Path(env)
    return _platform_config_dir() / "cli-art" / CONFIG_FILENAME


def load_config() -> dict[str, Any]:
    path = config_path()
    if not path.exists():
        return {}

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    try:
        data = tomllib.loads(raw)
    except Exception:
        _warn_malformed(path)
        return {}

    if not isinstance(data, dict):
        _warn_malformed(path)
        return {}

    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        _warn_malformed(path)
        return {}

    return {k: v for k, v in defaults.items() if k in CONFIG_KEYS}


def _warn_malformed(path: Path) -> None:
    import typer

    typer.echo(f"Warning: ignoring malformed config file at {path}", err=True)
