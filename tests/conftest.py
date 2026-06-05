from pathlib import Path

from PIL import Image
import pytest


class MockResponse:
    def __init__(self, data: bytes, headers: dict | None = None):
        self._data = data
        self._pos = 0
        self.headers = headers or {}

    def read(self, size: int = -1) -> bytes:
        if size == -1:
            remaining = self._data[self._pos:]
            self._pos = len(self._data)
            return remaining
        chunk = self._data[self._pos:self._pos + size]
        self._pos += len(chunk)
        return chunk

    def close(self) -> None:
        pass


@pytest.fixture
def gradient_png(tmp_path: Path) -> Path:
    img = Image.new("RGB", (30, 10), color=(255, 0, 0))
    for x in range(30):
        for y in range(10):
            img.putpixel((x, y), (int(x / 30 * 255), int(y / 10 * 255), 128))
    path = tmp_path / "gradient.png"
    img.save(path)
    return path


@pytest.fixture
def small_red_png(tmp_path: Path) -> Path:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    path = tmp_path / "red.png"
    img.save(path)
    return path
