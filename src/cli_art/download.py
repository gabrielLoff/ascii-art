from __future__ import annotations

import io
import tempfile
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator

_URL_PREFIXES = ("http://", "https://")
MAX_DOWNLOAD_SIZE = 10 * 1024 * 1024
REQUEST_TIMEOUT = 10


class DownloadError(Exception):
    """Raised when image download fails."""


def is_url(source: str) -> bool:
    return source.startswith(_URL_PREFIXES)


@contextmanager
def download_image(url: str, max_size: int = MAX_DOWNLOAD_SIZE) -> Iterator[Path]:
    import urllib.error
    import urllib.request

    req = urllib.request.Request(
        url, headers={"User-Agent": "cli-art/1.0"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT)
    except urllib.error.URLError as e:
        raise DownloadError(f"Failed to download image: {e.reason}") from e
    except TimeoutError as e:
        raise DownloadError("Request timed out") from e

    content_length = resp.headers.get("Content-Length")
    if content_length is not None and int(content_length) > max_size:
        resp.close()
        raise DownloadError(
            f"Image too large ({int(content_length)} bytes, limit {max_size} bytes)"
        )

    buf = io.BytesIO()
    downloaded = 0
    while True:
        chunk = resp.read(8192)
        if not chunk:
            break
        downloaded += len(chunk)
        if downloaded > max_size:
            resp.close()
            raise DownloadError(
                f"Image exceeds size limit of {max_size} bytes"
            )
        buf.write(chunk)
    resp.close()

    buf.seek(0)
    try:
        from PIL import Image as PILImage
        PILImage.open(buf)
    except Exception as e:
        raise DownloadError(f"Downloaded content is not a valid image: {e}") from e

    buf.seek(0)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".img")
    tmp.write(buf.read())
    tmp.close()
    path = Path(tmp.name)
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)
