from unittest.mock import patch

import pyperclip
import pytest

from cli_art.clipboard import ClipboardError, copy_to_clipboard


def test_copy_success() -> None:
    with patch("pyperclip.copy") as mock_copy:
        copy_to_clipboard("hello")
        mock_copy.assert_called_once_with("hello")


def test_copy_failure() -> None:
    with patch(
        "pyperclip.copy",
        side_effect=pyperclip.PyperclipException("no clipboard tool"),
    ):
        with pytest.raises(ClipboardError, match="no clipboard tool"):
            copy_to_clipboard("hello")
