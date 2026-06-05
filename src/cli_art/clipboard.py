class ClipboardError(Exception):
    """Raised when clipboard operation fails."""


def copy_to_clipboard(text: str) -> None:
    try:
        import pyperclip

        pyperclip.copy(text)
    except ImportError:
        raise ClipboardError(
            "pyperclip is not installed. Install it with: pip install cli-art[clipboard]"
        ) from None
    except Exception as e:
        raise ClipboardError(str(e)) from e
