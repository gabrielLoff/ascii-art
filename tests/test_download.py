import io
from pathlib import Path
from unittest.mock import patch

import pytest

from cli_art.download import DownloadError, download_image, is_url

from .conftest import MockResponse


def _tiny_png() -> bytes:
    """Create a minimal valid PNG (1×1 red pixel)."""
    # Minimal PNG: signature + IHDR + IDAT + IEND
    import struct
    import zlib

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)  # 1x1, 8-bit RGB
    ihdr_crc = struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff)
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + ihdr_crc

    raw = b'\x00' + b'\xff\x00\x00'  # filter byte + red pixel
    compressed = zlib.compress(raw)
    idat_crc = struct.pack('>I', zlib.crc32(b'IDAT' + compressed) & 0xffffffff)
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + idat_crc

    iend_crc = struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
    iend = struct.pack('>I', 0) + b'IEND' + iend_crc

    return sig + ihdr + idat + iend


def test_is_url() -> None:
    assert is_url("http://example.com/image.jpg")
    assert is_url("https://example.com/image.jpg")
    assert not is_url("/local/path/image.jpg")
    assert not is_url("relative/path/image.jpg")
    assert not is_url("image.jpg")


def test_download_success() -> None:
    png = _tiny_png()

    def mock_urlopen(req, timeout: int = 10) -> MockResponse:
        return MockResponse(png, {"Content-Length": str(len(png))})

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        with download_image("https://example.com/img.png") as path:
            assert path.exists()
            assert path.stat().st_size > 0
        assert not path.exists()


def test_download_content_length_too_large() -> None:
    def mock_urlopen(req, timeout: int = 10) -> MockResponse:
        return MockResponse(b"", {"Content-Length": str(20 * 1024 * 1024)})

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        with pytest.raises(DownloadError, match="too large"):
            with download_image("https://example.com/img.png", max_size=10 * 1024 * 1024):
                pass


def test_download_stream_exceeds_limit() -> None:
    big_data = b"x" * (12 * 1024 * 1024)

    def mock_urlopen(req, timeout: int = 10) -> MockResponse:
        return MockResponse(big_data)

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        with pytest.raises(DownloadError, match="exceeds size limit"):
            with download_image("https://example.com/img.png", max_size=10 * 1024 * 1024):
                pass


def test_download_invalid_image() -> None:
    def mock_urlopen(req, timeout: int = 10) -> MockResponse:
        return MockResponse(b"not an image")

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        with pytest.raises(DownloadError, match="not a valid image"):
            with download_image("https://example.com/img.png"):
                pass


def test_download_url_error() -> None:
    import urllib.error

    def mock_urlopen(req, timeout: int = 10) -> None:
        raise urllib.error.URLError("Connection refused")

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        with pytest.raises(DownloadError, match="Failed to download"):
            with download_image("https://example.com/img.png"):
                pass
