# convert_zh

簡體中文轉繁體中文（台灣）轉換工具，支援批次處理純文字小說檔案。

## 功能特色

- **台灣用語轉換**：使用 OpenCC `s2twp` 模式，自動轉換詞彙（如「鼠标」→「滑鼠」、「软件」→「軟體」）
- **自動編碼偵測**：支援 GB18030、GBK、GB2312、UTF-8、Big5 等編碼
- **遞迴處理**：自動處理目錄下所有子目錄與檔案
- **檔名轉換**：同時轉換檔案名稱與目錄名稱
- **安全機制**：支援預覽模式與備份功能

## 安裝

```bash
# 使用 uv 安裝依賴
uv sync

# 或安裝為開發模式
uv pip install -e .
```

## 使用方式

```bash
# 基本用法 - 原地轉換
uv run convert_zh /path/to/novels

# 預覽變更（不修改檔案）
uv run convert_zh /path/to/novels --dry-run

# 轉換前建立備份
uv run convert_zh /path/to/novels --backup

# 跳過確認提示
uv run convert_zh /path/to/novels -y

# 顯示詳細輸出
uv run convert_zh /path/to/novels -v
```

## CLI 參數

| 參數 | 說明 |
|------|------|
| `directory` | 要處理的目錄路徑 |
| `--dry-run` | 預覽模式，不實際修改檔案 |
| `--backup` | 轉換前建立備份 |
| `--backup-dir PATH` | 指定備份目錄位置 |
| `-y, --yes` | 跳過確認提示 |
| `--no-rename` | 僅轉換內容，不重命名檔案 |
| `--no-content` | 僅重命名檔案，不轉換內容 |
| `-v, --verbose` | 顯示詳細輸出（可疊加 -vv） |
| `--log-file PATH` | 輸出日誌到檔案 |

## 範例

```bash
# 預覽 /home/user/novels 目錄下的變更
uv run convert_zh /home/user/novels --dry-run

# 輸出範例：
# Found 3 file(s) to process:
#   - /home/user/novels/小说.txt
#   - /home/user/novels/作者/故事.txt
#
# [DRY RUN] The following changes would be made:
#   /home/user/novels/小说.txt
#     Content: 1500 lines would change
#     Rename: 小说.txt -> 小說.txt

# 實際執行轉換（含備份）
uv run convert_zh /home/user/novels --backup -y
```

## 依賴套件

- [opencc-python-reimplemented](https://pypi.org/project/opencc-python-reimplemented/) - 中文簡繁轉換
- [charset-normalizer](https://pypi.org/project/charset-normalizer/) - 編碼偵測

## 授權

MIT License
