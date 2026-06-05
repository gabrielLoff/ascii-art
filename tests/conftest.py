from pathlib import Path

from PIL import Image
import pytest


def _make_gif(
    tmp_path: Path,
    frames: list[Image.Image],
    durations: list[int] | None = None,
    filename: str = "test.gif",
) -> Path:
    path = tmp_path / filename
    first = frames[0]
    rest = frames[1:]
    kwargs: dict = {"save_all": True, "append_images": rest, "loop": 0}
    if durations is not None:
        kwargs["duration"] = durations
    first.save(path, format="GIF", **kwargs)
    return path


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


@pytest.fixture
def single_frame_gif(tmp_path: Path) -> Path:
    img = Image.new("RGB", (30, 10), color=(0, 255, 0))
    return _make_gif(tmp_path, [img], filename="single.gif")


@pytest.fixture
def two_frame_gif(tmp_path: Path) -> Path:
    frame1 = Image.new("RGB", (30, 10), color=(255, 0, 0))
    frame2 = Image.new("RGB", (30, 10), color=(0, 255, 0))
    return _make_gif(tmp_path, [frame1, frame2], durations=[100, 200], filename="two_frame.gif")
