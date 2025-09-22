# WebMenuGenerator

レガシーな飲食店向け端末データ（`menudb.dat`、`free/config/*.ini`、`osusume` など）を解析し、Web 表示用 JSON と最小 SPA を生成する PoC プロジェクトです。保持（raw dump）と表示（web_content）を分離し、旧データ資産を安全にリファクタリングすることを目的としています。

## 進捗状況（2025-09-17 時点）
- `menudb.dat` の ITEM_INFO を Java 実装（`MenuDb.java` Rev128）に完全追従する Python パーサーを実装。ヘッダ算出から 376byte ストライドまで整合済み。
- `webmenu generate` CLI が `menudb.dat`／`free/config/*.ini`／`osusume` を読み込み、`outroot/builds/<ref>/` 以下に `raw_dump` と `web_content` を出力。
- `web_content/menudb.json` では全商品を保持、税込価格を採用。SPA（`src/webmenu/web/html_skeleton.py`）で一覧表示の最小動作を確認。
- 仕様資料（`specification/MenuDb.java`, `MENU仕様書Rev128.pdf`, `iteminfo.csv`）をプロジェクトに追加済み。

## TODO / 未完了タスク
- `to_web_categories.py` はスタブ状態。大/中/小分類ツリーの生成ロジックを Java 仕様から移植する。
- 小分類ページ（`small/{id}/page-n.json`）の生成は PoC 仕様。品切れ・コメント・サブメニューの扱いを詰める。
- SPA 側の検索・フィルタ（表記ゆれ対策や管理行の非表示）を調整。
- テスト整備（ユニットテスト＋ fixture 化）と CI 導入。

## ディレクトリ構成
- `src/webmenu` – 解析・マッピング・出力ロジック一式
- `src/webmenu/web` – 最小 SPA とバリデーション
- `src/webmenu/parsers` – レガシーフォーマットのリーダ（`menudb_reader`, `ini_loader`, `osusume_reader`）
- `outroot/` – `webmenu generate` の成果物（`raw_dump`/`web_content`）
- `specification/` – 仕様書・既存実装リファレンス
- `tests/` – テスト雛形（今後拡充予定）

## セットアップ
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

※ `pyproject.toml` には `pandas` / `openpyxl` など必要ライブラリを定義済み。

## 実行方法
```bash
# プロジェクトルートで実行
PYTHONPATH=src python -m webmenu.cli generate \
  --free     dataSrc/free \
  --osusume  dataSrc/osusume \
  --out      outroot \
  --ref      20250917-dev

# 実行後: outroot/builds/20250917-dev/ 以下に raw_dump / web_content が生成されます
```

## 動作確認のポイント
- `raw_dump/menudb/item_infos.json` 先頭が `code:101 エビ`, `code:103 特大エビ` となっていることを確認済み。
- `web_content/menudb.json` の `schema_version` は CLI オプションで上書き可能。
- HTML テンプレートは `src/webmenu/web/html_skeleton.py`。SPA から `web_content/*.json` を fetch。

## 参考資料
- `specification/MenuDb.java` – 元 Android 実装。構造体サイズ・オフセットの根拠。
- `specification/iteminfo.csv` – ITEM_INFO の既知正解（SJIS, 376 byte ストライド確認用）。
- `specification/MENU仕様書Rev128.pdf` – 公式仕様書。
