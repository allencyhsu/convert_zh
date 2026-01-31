"""Core Chinese conversion logic using OpenCC."""

from pathlib import Path

from opencc import OpenCC


class ChineseConverter:
    """Handles Simplified to Traditional Chinese conversion."""

    def __init__(self, conversion: str = "s2twp"):
        """
        Initialize the converter.

        Args:
            conversion: OpenCC conversion mode. Default 's2twp' for
                       Simplified -> Traditional (Taiwan) with idioms.
        """
        self._cc = OpenCC(conversion)

    def convert(self, text: str) -> str:
        """
        Convert text from Simplified to Traditional Chinese.

        Args:
            text: Input text in Simplified Chinese

        Returns:
            Converted text in Traditional Chinese
        """
        if not text:
            return text
        return self._cc.convert(text)

    def convert_filename(self, filename: str) -> str:
        """
        Convert a filename from Simplified to Traditional Chinese.

        Preserves file extension.

        Args:
            filename: Original filename

        Returns:
            Converted filename with Traditional Chinese characters
        """
        path = Path(filename)
        stem = path.stem
        suffix = path.suffix

        converted_stem = self.convert(stem)
        return f"{converted_stem}{suffix}"

    def has_changes(self, text: str) -> bool:
        """
        Check if converting text would produce changes.

        Args:
            text: Text to check

        Returns:
            True if conversion would change the text
        """
        return self.convert(text) != text
