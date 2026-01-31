"""File and directory processing logic."""

import logging
from pathlib import Path

from .converter import ChineseConverter
from .encoding import read_file_with_encoding, write_file_with_encoding


class FileProcessor:
    """Processes files and directories for Chinese conversion."""

    def __init__(
        self,
        converter: ChineseConverter,
        extensions: list[str] | None = None,
        rename_files: bool = True,
        convert_content: bool = True,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize the file processor.

        Args:
            converter: ChineseConverter instance
            extensions: File extensions to process (e.g., ['.txt'])
            rename_files: Whether to rename files
            convert_content: Whether to convert file contents
            logger: Logger instance
        """
        self.converter = converter
        self.extensions = set(ext.lower() for ext in (extensions or [".txt"]))
        self.rename_files = rename_files
        self.convert_content = convert_content
        self.logger = logger or logging.getLogger(__name__)

    def scan_directory(self, directory: Path) -> list[Path]:
        """
        Recursively scan directory for matching files.

        Args:
            directory: Root directory to scan

        Returns:
            List of matching file paths
        """
        files = []

        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in self.extensions:
                files.append(path)

        return sorted(files)

    def process_directory(
        self,
        source_dir: Path,
        dry_run: bool = False,
    ) -> tuple[int, int]:
        """
        Process all matching files in a directory.

        Args:
            source_dir: Source directory
            dry_run: If True, only preview changes

        Returns:
            Tuple of (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0

        files = self.scan_directory(source_dir)

        # Process files from deepest to shallowest (for directory renaming later)
        files.sort(key=lambda p: len(p.parts), reverse=True)

        for file_path in files:
            try:
                self.process_file(file_path, dry_run=dry_run)
                success_count += 1
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
                failure_count += 1

        # Rename directories if needed (after processing files)
        if self.rename_files and not dry_run:
            self._rename_directories(source_dir)

        return success_count, failure_count

    def process_file(
        self,
        file_path: Path,
        dry_run: bool = False,
    ) -> Path:
        """
        Process a single file.

        Args:
            file_path: Path to the file
            dry_run: If True, only preview changes

        Returns:
            Final path of the processed file
        """
        new_path = file_path

        # Determine new filename if renaming
        if self.rename_files:
            new_name = self.converter.convert_filename(file_path.name)
            new_path = file_path.parent / new_name

        if dry_run:
            self._log_dry_run(file_path, new_path)
            return new_path

        # Convert content if requested
        if self.convert_content:
            content, original_encoding = read_file_with_encoding(file_path)
            converted_content = self.converter.convert(content)

            # Write with UTF-8 encoding
            write_file_with_encoding(file_path, converted_content, encoding="utf-8")
            self.logger.info(f"Converted content: {file_path}")

        # Rename file if needed
        if self.rename_files and new_path != file_path:
            file_path.rename(new_path)
            self.logger.info(f"Renamed: {file_path.name} -> {new_path.name}")

        return new_path

    def _log_dry_run(self, source: Path, target: Path) -> None:
        """Log what would happen in a dry run."""
        changes = []

        if self.convert_content:
            try:
                content, _ = read_file_with_encoding(source)
                converted = self.converter.convert(content)
                if content != converted:
                    original_lines = content.split("\n")
                    converted_lines = converted.split("\n")
                    changed_lines = sum(
                        1
                        for a, b in zip(original_lines, converted_lines)
                        if a != b
                    )
                    changes.append(f"Content: {changed_lines} lines would change")
            except Exception as e:
                changes.append(f"Content: Error reading file - {e}")

        if self.rename_files and source.name != target.name:
            changes.append(f"Rename: {source.name} -> {target.name}")

        if changes:
            print(f"  {source}")
            for change in changes:
                print(f"    {change}")

    def _rename_directories(self, source_dir: Path) -> None:
        """Rename directories with Simplified Chinese names."""
        # Get all directories, sorted deepest first
        dirs = sorted(
            [d for d in source_dir.rglob("*") if d.is_dir()],
            key=lambda p: len(p.parts),
            reverse=True,
        )

        for dir_path in dirs:
            new_name = self.converter.convert(dir_path.name)
            if new_name != dir_path.name:
                new_path = dir_path.parent / new_name
                if not new_path.exists():
                    dir_path.rename(new_path)
                    self.logger.info(f"Renamed directory: {dir_path.name} -> {new_name}")
