# WebMenuGenerator

レガシーな飲食店向け端末データ（`menudb.dat`、`free/config/*.ini`、`osusume` など）を解析し、Web 表示用 JSON と最小 SPA を生成する PoC プロジェクトです。保持（raw dump）と表示（web_content）を分離し、旧データ資産を安全にリファクタリングすることを目的としています。

## 進捗状況（2025-10-06 時点）
- `menudb.dat` の ITEM_INFO を Java 実装（`MenuDb.java` Rev128）に準拠して解析。ヘッダ算出・376byte ストライドなど整合済み。
- `webmenu generate` CLI が `free/config/*.ini`・`menudb.dat`・`osusume` を取り込み、`outroot/builds/<ref>/` 配下に `raw_dump` と `web_content` を出力。
- 小分類ページ生成（`to_web_small_pages.py`）は showType=0（フリーレイアウト）と showType=6（おすすめグリッド）の両方に対応。セル座標は `small/<id>/cells.json` へ切り出し、`grid_items` に `product_detail` とおすすめ特有の `osusume` メタを保持。
- カテゴリツリー（`to_web_categories.py`）が L/M/S をツリー化し、ページの `layout_type` / `sequence` / `show_type` を付与。
- SPA（`src/webmenu/web/html_skeleton.py`）はブラウザ上で階層をプルダウン選択し、セルオーバーレイ付きでレイアウト確認が可能。おすすめページは背景＋セル枠でのプレビューデバッグができる。デフォルト出力は商品画像のみを表示し、`--show-dev-ui` を付けてビルドするとツールバーやログを含むデバッグ UI が有効になる。

## TODO / 未完了タスク
- おすすめページの売切れ時挙動（非表示・左詰め）や放題モードなど、表示制御の実装。
- サブメニュー／セット商品の遷移仕様を Kotlin 連携も含めて詰める（JS のイベント仕様化含む）。
- おすすめ画像や商品画像差し替えの仕組みを検討する。
- おすすめレイアウトのマス寸法（パターンごとの固定グリッド）を定義し、セル幅/高さを再現する。
- テスト整備（ユニットテスト＋ fixture 化）と CI 導入。
- 検証用データセットを最新サンプルに差し替え、動作確認手順を更新する。

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

- Windows PowerShell

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

## 実行方法
```bash
# プロジェクトルートで実行
PYTHONPATH=src python -m webmenu.cli generate \
  --free     dataSrc/free \
  --osusume  dataSrc/osusume \
  --out      outroot \
  --ref      20250917-dev
  # ツールバー/ログを表示したい場合は --show-dev-ui を追加

# 実行後: outroot/builds/20250917-dev/ 以下に raw_dump / web_content が生成されます

# 参照画像も含める場合は --skip-assets を外す（デフォルト）。
# `outroot/builds/<ref>/web_content` で `python -m http.server` を起動し、
# http://localhost:8000/ を開くと `result.html` と同じ UI で確認できます。
```

- Windows PowerShell

```bash
$env:PYTHONPATH = "src"
python -m webmenu.cli generate `
  --free dataSrc/free `
  --osusume dataSrc/osusume `
  --out outroot `
  --ref 20250917-dev
  # --show-dev-ui を付けるとデバッグ UI 付きで出力されます

cd outroot/builds/<ref>/web_content
python -m http.server
```

## 動作確認のポイント
- `raw_dump/menudb/item_infos.json` 先頭が `code:101 エビ`, `code:103 特大エビ` であること（仕様書と整合）。
- `web_content/categories.json` に L01〜L10 が展開され、`layout_type` が `free` / `recommended` になっていること。
- おすすめページ（例: `small/sm-0101001/page-1.json`）の `grid_items` に `osusume` メタが含まれ、セル座標は `cells_path` で参照できること。
- SPA (`result.html`) でプルダウン操作によりセル枠付きでレイアウトを確認できる。デバッグ後は CSS (`.cell-box` 等) を透明にすることで実機表示へ寄せられる。

## 参考資料
- `specification/MenuDb.java` – 元 Android 実装。構造体サイズ・オフセットの根拠。
- `specification/iteminfo.csv` – ITEM_INFO の既知正解（SJIS, 376 byte ストライド確認用）。
- `specification/MENU仕様書Rev128.pdf` – 公式仕様書。
