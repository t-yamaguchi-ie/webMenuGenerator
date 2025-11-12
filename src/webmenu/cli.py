"""
WebMenuGenerator CLI モジュール

このモジュールは、レガシーデータ（free ディレクトリや osusume ディレクトリ）から
最新の web_content ディレクトリを生成するコマンドラインインターフェイス（CLI）です。

主な処理の流れ:
  1. コマンドライン引数の解析
  2. generate コマンドにより run_pipeline を呼び出し
  3. run_pipeline 内でレガシーデータの読み込み、JSON生成、必要アセットの収集・コピー
  4. 最終的に web_content ディレクトリと index.html を出力

提供されるオプション:
  --free           : free ディレクトリのパス
  --osusume        : osusume ディレクトリのパス
  --out            : 出力先ルートディレクトリ
  --ref            : 任意のビルド識別子（未指定時は自動生成）
  --schema-version : web_content のスキーマバージョン
  --skip-assets    : アセットコピー/最適化をスキップ
  --show-dev-ui    : 生成される index.html に開発用UIを表示
"""
import argparse
from .pipeline import run_pipeline

def build_parser():
    p = argparse.ArgumentParser(prog="webmenu", description="WebMenuGenerator CLI")
    sp = p.add_subparsers(dest="cmd", required=True)

    g = sp.add_parser("generate", help="Convert legacy dumps to web_content")
    g.add_argument("--free", required=True, help="Path to 'free' directory (LZH展開済み)")
    g.add_argument("--osusume", required=True, help="Path to 'osusume' directory (LZH展開済み)")
    g.add_argument("--out", required=True, help="Output root path for builds/{ref}")
    g.add_argument("--ref", default="", help="Optional ref (YYYYMMDD-hhmmss-commit). Auto if empty.")
    g.add_argument("--schema-version", default="0.1", help="web_content schema version")
    g.add_argument("--skip-assets", action="store_true", help="Skip asset copy/optimization")
    g.add_argument("--show-dev-ui", action="store_true", help="Show toolbar/log UI in generated index.html")
    return p

def main():
    args = build_parser().parse_args()
    if args.cmd == "generate":
        run_pipeline(args)

if __name__ == "__main__":
    main()
