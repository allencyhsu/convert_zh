"""Backup management for file conversion."""

import logging
import shutil
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def create_backup(
    source_dir: Path,
    backup_dir: Path | None = None,
    timestamp_format: str = "%Y%m%d_%H%M%S",
) -> Path:
    """
    Create a backup of the source directory.

    Args:
        source_dir: Directory to backup
        backup_dir: Destination for backup (auto-generated if None)
        timestamp_format: Format for timestamp in backup name

    Returns:
        Path to the created backup directory

    Raises:
        FileExistsError: If backup directory already exists
    """
    if backup_dir is None:
        timestamp = datetime.now().strftime(timestamp_format)
        backup_dir = source_dir.parent / f"{source_dir.name}_backup_{timestamp}"

    if backup_dir.exists():
        raise FileExistsError(f"Backup directory already exists: {backup_dir}")

    logger.info(f"Creating backup: {source_dir} -> {backup_dir}")
    shutil.copytree(source_dir, backup_dir)

    return backup_dir
