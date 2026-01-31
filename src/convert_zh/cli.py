"""CLI entry point for convert_zh tool."""

import argparse
import sys
from pathlib import Path

from .backup import create_backup
from .converter import ChineseConverter
from .file_processor import FileProcessor
from .logger import setup_logger


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="convert_zh",
        description="Convert Simplified Chinese to Traditional Chinese (Taiwan) in text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  convert_zh /path/to/novels                    # Convert in-place
  convert_zh /path/to/novels --dry-run          # Preview changes only
  convert_zh /path/to/novels --backup           # Create backups before converting
        """,
    )

    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing text files to convert",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )

    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup of original files before conversion",
    )

    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Directory for backups (default: <directory>_backup_<timestamp>)",
    )

    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )

    parser.add_argument(
        "--no-rename",
        action="store_true",
        help="Do not rename files (only convert contents)",
    )

    parser.add_argument(
        "--no-content",
        action="store_true",
        help="Do not convert file contents (only rename files)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for INFO, -vv for DEBUG)",
    )

    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Write log to file",
    )

    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    logger = setup_logger(
        verbosity=args.verbose,
        log_file=args.log_file,
    )

    # Validate input directory
    if not args.directory.exists():
        print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
        return 1

    if not args.directory.is_dir():
        print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
        return 1

    # Initialize components
    converter = ChineseConverter()
    processor = FileProcessor(
        converter=converter,
        extensions=[".txt"],
        rename_files=not args.no_rename,
        convert_content=not args.no_content,
        logger=logger,
    )

    # Scan files
    files = processor.scan_directory(args.directory)

    if not files:
        print("No matching files found.")
        return 0

    # Display summary
    print(f"\nFound {len(files)} file(s) to process:")
    for f in files[:10]:
        print(f"  - {f}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more")

    # Dry run mode
    if args.dry_run:
        print("\n[DRY RUN] The following changes would be made:")
        processor.process_directory(
            source_dir=args.directory,
            dry_run=True,
        )
        return 0

    # Confirmation prompt
    if not args.yes:
        response = input("\nProceed with conversion? [y/N]: ")
        if response.lower() not in ("y", "yes"):
            print("Aborted.")
            return 0

    # Create backup if requested
    if args.backup:
        try:
            backup_path = create_backup(
                source_dir=args.directory,
                backup_dir=args.backup_dir,
            )
            print(f"Backup created at: {backup_path}")
        except FileExistsError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # Process files
    success, failed = processor.process_directory(
        source_dir=args.directory,
        dry_run=False,
    )

    # Report results
    print(f"\nConversion complete:")
    print(f"  Successful: {success}")
    print(f"  Failed: {failed}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
