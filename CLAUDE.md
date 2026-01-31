# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the CLI
uv run convert_zh /path/to/files

# Run with options
uv run convert_zh /path/to/files --dry-run    # Preview changes
uv run convert_zh /path/to/files --backup     # Create backup first
uv run convert_zh /path/to/files -y           # Skip confirmation
uv run convert_zh /path/to/files -v           # Verbose output

# Install package in dev mode
uv pip install -e .
```

## Architecture

This CLI tool converts Simplified Chinese (zh_CN) text files to Traditional Chinese (zh_TW, Taiwan standard).

**Core Modules:**

- `converter.py` - Wraps OpenCC library using "s2twp" mode (Simplified → Traditional Taiwan with idioms like 鼠标→滑鼠)
- `encoding.py` - Detects file encoding with fallback chain: charset_normalizer → gb18030/gbk/gb2312/utf-8/big5 → gb18030 with error replacement. Output is always UTF-8.
- `file_processor.py` - Recursive directory scanning, processes files depth-first for proper directory renaming
- `cli.py` - Entry point with argparse, handles user confirmation and progress reporting
- `backup.py` - Creates timestamped backups: `<dirname>_backup_<timestamp>`
- `logger.py` - Configures logging with verbosity levels

**Data Flow:**
1. CLI validates directory and scans for .txt files
2. For each file: detect encoding → read content → convert with OpenCC → write as UTF-8
3. Rename files/directories from Simplified to Traditional Chinese names
