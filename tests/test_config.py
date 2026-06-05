from pathlib import Path

from typer.testing import CliRunner

from cli_art.cli import app
from cli_art.config import config_path, load_config

runner = CliRunner()


def test_no_config_file(monkeypatch) -> None:
    monkeypatch.setenv("CLI_ART_CONFIG", "/nonexistent/path/config.toml")
    assert load_config() == {}


def test_empty_config_file(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text("")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))
    assert load_config() == {}


def test_empty_defaults(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text("[defaults]\n")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))
    assert load_config() == {}


def test_partial_config(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text("[defaults]\nwidth = 120\n")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))
    result = load_config()
    assert result == {"width": 120}


def test_full_config(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        "[defaults]\n"
        'width = 100\n'
        'invert = true\n'
        'theme = "eighths"\n'
        'mode = "edge"\n'
        'no_color = true\n'
    )
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))
    result = load_config()
    assert result["width"] == 100
    assert result["invert"] is True
    assert result["theme"] == "eighths"
    assert result["mode"] == "edge"
    assert result["no_color"] is True


def test_malformed_toml(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text("this is not toml {{{")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))
    assert load_config() == {}


def test_unknown_keys_ignored(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text('[defaults]\nwidth = 80\nunknown = "ignored"\n')
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))
    assert load_config() == {"width": 80}


def test_non_dict_defaults(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text('defaults = "not a dict"\n')
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))
    assert load_config() == {}


def test_non_dict_root(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text('key = "value"\n')
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))
    assert load_config() == {}


def test_config_path_env_var(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "custom.toml"
    cfg.write_text("[defaults]\nwidth = 50\n")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))
    assert config_path() == cfg
    assert load_config() == {"width": 50}


def test_config_path_platform_linux(monkeypatch) -> None:
    monkeypatch.delenv("CLI_ART_CONFIG", raising=False)
    monkeypatch.setattr("cli_art.config.sys.platform", "linux")
    path = config_path()
    assert str(path).endswith("/.config/cli-art/config.toml")


def test_cli_width_overrides_config(gradient_png, tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text("[defaults]\nwidth = 200\n")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))

    result = runner.invoke(app, ["ascii", str(gradient_png), "--width", "40"])
    assert result.exit_code == 0


def test_cli_invert_overrides_config(gradient_png, tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text("[defaults]\ninvert = true\n")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))

    result = runner.invoke(app, ["ascii", str(gradient_png), "--no-invert"])
    assert result.exit_code == 0


def test_cli_no_color_overrides_config(gradient_png, tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text("[defaults]\nno_color = false\n")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))

    result = runner.invoke(app, ["ascii", str(gradient_png), "--no-color"])
    assert result.exit_code == 0
    assert "\033[" not in result.stdout


def test_cli_chars_overrides_config(gradient_png, tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text('[defaults]\nchars = " @%"\n')
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))

    result = runner.invoke(app, ["ascii", str(gradient_png), "--chars", "@%#"])
    assert result.exit_code == 0


def test_cli_theme_overrides_config(gradient_png, tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text('[defaults]\ntheme = "mono"\n')
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))

    result = runner.invoke(app, ["ascii", str(gradient_png), "--theme", "eighths"])
    assert result.exit_code == 0


def test_config_chars_and_theme_conflict(gradient_png, tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text('[defaults]\nchars = " @%"\ntheme = "mono"\n')
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))

    result = runner.invoke(app, ["ascii", str(gradient_png)])
    assert result.exit_code != 0


def test_config_does_not_affect_themes_command(tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text("[defaults]\nwidth = 999\n")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))

    result = runner.invoke(app, ["themes"])
    assert result.exit_code == 0
    assert "eighths" in result.stdout


def test_config_width_applied(gradient_png, tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text("[defaults]\nwidth = 120\n")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))

    result = runner.invoke(app, ["ascii", str(gradient_png)])
    assert result.exit_code == 0


def test_config_invert_applied(small_red_png, tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text("[defaults]\ninvert = true\n")
    monkeypatch.setenv("CLI_ART_CONFIG", str(cfg))

    result = runner.invoke(app, ["ascii", str(small_red_png)])
    assert result.exit_code == 0
