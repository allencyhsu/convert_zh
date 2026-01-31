"""File encoding detection utilities."""

import logging
from pathlib import Path

from charset_normalizer import from_bytes

logger = logging.getLogger(__name__)

# Common encodings for Chinese text files (ordered by likelihood for Simplified Chinese)
CHINESE_ENCODINGS = [
    "gb18030",  # Superset of GBK/GB2312, most compatible for Simplified Chinese
    "gbk",
    "gb2312",
    "utf-8",
    "utf-8-sig",
    "big5",
    "big5hkscs",
]


def detect_encoding(file_path: Path, sample_size: int = 65536) -> tuple[str, float]:
    """
    Detect the encoding of a text file.

    Args:
        file_path: Path to the file
        sample_size: Number of bytes to sample for detection

    Returns:
        Tuple of (encoding_name, confidence)
    """
    with open(file_path, "rb") as f:
        raw_data = f.read(sample_size)

    result = from_bytes(raw_data).best()
    if result:
        return result.encoding, 1.0 - result.chaos

    # Fallback: try common encodings
    for encoding in CHINESE_ENCODINGS:
        try:
            raw_data.decode(encoding)
            return encoding, 0.5
        except (UnicodeDecodeError, LookupError):
            continue

    logger.warning(f"Could not detect encoding for {file_path}, defaulting to UTF-8")
    return "utf-8", 0.0


def read_file_with_encoding(file_path: Path) -> tuple[str, str]:
    """
    Read a text file with automatic encoding detection.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (file_content, detected_encoding)

    Raises:
        UnicodeDecodeError: If file cannot be decoded with any known encoding
    """
    # Read entire file for encoding detection
    with open(file_path, "rb") as f:
        raw_data = f.read()

    # Try charset_normalizer first
    result = from_bytes(raw_data).best()
    if result:
        encoding = result.encoding
        logger.debug(f"Detected encoding {encoding} for {file_path}")
        try:
            return raw_data.decode(encoding), encoding
        except UnicodeDecodeError:
            pass

    # Try common Chinese encodings
    for enc in CHINESE_ENCODINGS:
        try:
            content = raw_data.decode(enc)
            logger.debug(f"Using encoding {enc} for {file_path}")
            return content, enc
        except (UnicodeDecodeError, LookupError):
            continue

    # Last resort: gb18030 with error replacement
    logger.warning(f"Using gb18030 with error replacement for {file_path}")
    return raw_data.decode("gb18030", errors="replace"), "gb18030"


def write_file_with_encoding(
    file_path: Path,
    content: str,
    encoding: str = "utf-8",
) -> None:
    """
    Write content to a file with specified encoding.

    Args:
        file_path: Path to write to
        content: Text content to write
        encoding: Output encoding (default: UTF-8)
    """
    with open(file_path, "w", encoding=encoding) as f:
        f.write(content)
