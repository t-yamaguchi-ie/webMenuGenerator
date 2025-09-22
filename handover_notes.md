# WebMenuGenerator 引き継ぎメモ

最終更新: 2025-09-17

## 1. 現在の成果
- `menudb.dat` の ITEM_INFO を Java 実装と同じ 376byte ストライドで解析する Python 実装を完了。
- `PYTHONPATH=src python -m webmenu.cli generate --free dataSrc/free --osusume dataSrc/osusume --out outroot --ref 20250917-dev` でビルドでき、`outroot/builds/20250917-dev/` に `raw_dump` および `web_content` を出力。
- `raw_dump/menudb/item_infos.json` の 0 行目から `code:101 エビ`, `code:103 特大エビ` など、`specification/iteminfo.csv` との整合を確認済み。
- `web_content/menudb.json` は税込価格を採用し、SPA (`src/webmenu/web/html_skeleton.py`) で一覧表示できる最小動作を確認。

## 2. 作業環境メモ
- Python 3.10+ 前提。`pip install -e .` で依存 (`pandas`, `openpyxl`) を導入。
- 仕様リファレンス: `specification/MenuDb.java`, `MENU仕様書Rev128.pdf`, `iteminfo.csv`。
- データソース: `dataSrc/free/`（config, menudb.dat）と `dataSrc/osusume/`（おすすめ設定）。

## 3. 今後の優先タスク
1. **分類ツリー生成** – `src/webmenu/mapping/to_web_categories.py` はスタブ。大/中/小分類、サブ分類のツリーを Java 実装から起こす。
2. **小分類ページ出力** – `src/webmenu/mapping/to_web_small_pages.py` のロジック拡充（コメント行や管理行を表示上除外するポリシー実装）。
3. **検索・表記ゆれ対策** – SPA 側でキーワード検索時の全角/半角/平仮名揺れを正規化する仕組みを検討。
4. **テスト追加** – menudb.dat の既知バイナリを fixture 化し、パーサーの出力差分を自動検証。CI も検討。
5. **資産コピー** – `export_assets` での画像/動画コピー要件を整理し、`specification` の画像パス仕様と突き合わせ。

## 4. 既知の注意点
- `menudb_reader` は保持目的なので管理メモ行も捨てていない。表示で除外する場合はマッピング層またはフロント側で対応。
- `infoImg` は Shift_JIS 前提。現状ファイル名が空の場合が多いが、今後の案件で要確認。
- CLI のエントリーポイントは `webmenu`（pyproject の `project.scripts`）。Poetry は未導入、`python -m` 実行前提。

## 5. 連絡事項
- 追加仕様・疑問点は `specification/設計詳細_WebMenuGenerator.xlsx` 参照（現行チームの運用メモ）。
- Java 版のロジック追従が必要になった場合、`MenuDb#getItemInformation` 周辺が最も参照頻度高い。

以上を踏まえ、次回作業者は 3. 今後の優先タスクから着手するとスムーズです。
