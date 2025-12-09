# ============================================================
# パイプライン処理用モジュール
# - ini/json からメニュー情報を読み込み
# - web 用データに変換して出力
# - 必要なアセットを収集してコピー
# ============================================================

# 先頭のimportをこうする（os/jsonはトップレベルで）
import os
import json
import datetime
import logging

# 自作モジュール
from .parsers.ini_loader import load_all_ini
from .parsers.menudb_reader import read_menudb
from .parsers.osusume_reader import read_osusume
from .dumpers.raw_dump_writer import write_raw_dump
from .mapping.to_web_products import make_products
from .mapping.to_web_categories import make_categories
from .mapping.to_web_small_pages import make_small_pages
from .mapping.to_web_soldout import make_soldout_json
from .web.html_skeleton import write_index_html
from .web.validate import validate_all
from .dumpers.assets_exporter import export_assets
from .dumpers.assets_exporter import export_soldout_assets
from typing import Set

ASSET_PREFIX_FREE = "free_images/"

# ------------------------------------------------------------
# ログ初期化処理
# ・ログ出力ディレクトリを作成
# ・ファイル名は「機能名_YYYYMMDD.log」形式
# ・コンソール ＋ ファイルの両方へ出力
# ------------------------------------------------------------
def setup_logger(log_dir="D:/WebMenu/logs", name="webmenu_generate"):
    os.makedirs(log_dir, exist_ok=True)

    today = datetime.datetime.now().strftime("%Y%m%d")
    log_path = os.path.join(log_dir, f"{name}_{today}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s"
        )

        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(fmt)

        ch = logging.StreamHandler()
        ch.setFormatter(fmt)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger

# ------------------------------------------------------------
# アセットパス正規化
# 文字列の空チェック＋前後スペース削除
# ------------------------------------------------------------
def _normalize_asset_path(name: str) -> str:
    if not name:
        return ""
    name = str(name).strip()
    if not name:
        return ""
    return name

# ------------------------------------------------------------
# small_pages 内の必要アセットを収集
# ------------------------------------------------------------
def collect_required_assets(small_pages: dict) -> Set[str]:
    assets: Set[str] = set()
    for payload in small_pages.values():
        if not isinstance(payload, dict):
            continue
        bg = _normalize_asset_path(payload.get("background", ""))
        if bg:
            assets.add(bg)
        for item in payload.get("grid_items", []):
            if not isinstance(item, dict):
                continue
            img = _normalize_asset_path(item.get("image", ""))
            if img:
                assets.add(img)
            detail = item.get("product_detail") or {}
            info_img = _normalize_asset_path(detail.get("infoImg", ""))
            if info_img:
                if "/" in info_img:
                    assets.add(info_img)
                else:
                    assets.add(f"{ASSET_PREFIX_FREE}{info_img}")
                    
            # multi_lang_images
            multi_lang_images = item.get("multi_lang_images") or {}
            for lang, path in multi_lang_images.items():
                path = _normalize_asset_path(path)
                if path:
                    assets.add(path)
    return assets

# ------------------------------------------------------------
# パイプライン実行
# メニュー関連データを読み込んで加工し、Web向けに出力する一連の処理
# args: コマンドライン引数オブジェクト
# ------------------------------------------------------------
def run_pipeline(args):
    logger = setup_logger()
    logger.info("WebMenuGenerate 処理を開始します。")
    
    try:
        # ★ここから下、関数内に「import json, os」は置かない！
        ref = args.ref or datetime.datetime.now().strftime("%Y%m%d-%H%M%S-000000")
        out_root = os.path.join(args.out, "builds", ref)
        raw_dump_dir = os.path.join(out_root, "raw_dump")
        web_dir = os.path.join(out_root, "web_content")

        os.makedirs(raw_dump_dir, exist_ok=True)
        os.makedirs(web_dir, exist_ok=True)
    
        # Parse legacy
        logger.info("設定ファイルの読み込みを開始します。")
        ini_bundle = load_all_ini(os.path.join(args.free, "config"))
        menudb_path = os.path.join(args.free, "datas", "menudb.dat")
        menudb = read_menudb(menudb_path)
        osusume = read_osusume(args.osusume)

        # Raw dump
        logger.info("Raw dump の出力処理を開始します。")
        write_raw_dump(raw_dump_dir, ini_bundle, menudb, osusume)
        
        # Mapping to web_content
        logger.info("Web 向け JSON データの生成処理を開始します。")
        products = make_products(menudb, ini_bundle, schema_version=args.schema_version)
        small_pages, cell_files = make_small_pages(
            menudb,
            osusume,
            ini_bundle,
            schema_version=args.schema_version
        )
        categories = make_categories(menudb, ini_bundle, small_pages, schema_version=args.schema_version)
        soldout = make_soldout_json(ini_bundle)
        
        # Emit web_content
        logger.info("Web 向け JSON ファイルの出力を開始します。")
        with open(os.path.join(web_dir, "menudb.json"), "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        with open(os.path.join(web_dir, "categories.json"), "w", encoding="utf-8") as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)
        with open(os.path.join(web_dir, "soldout.json"), "w", encoding="utf-8") as f:
            json.dump(soldout, f, ensure_ascii=False, indent=2)
        for rel_path, payload in small_pages.items():
            p = os.path.join(web_dir, rel_path)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        for rel_path, cells_payload in cell_files.items():
            p = os.path.join(web_dir, rel_path)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(cells_payload, f, ensure_ascii=False, indent=2)

        logger.info("画像素材ファイルの出力処理を開始します。")
        required_assets = collect_required_assets(small_pages)

        if not args.skip_assets:
            export_assets(
                args.free,
                args.osusume,
                os.path.join(web_dir, "assets"),
                required_assets=required_assets
            )
            export_soldout_assets(
                args.free,
                os.path.join(web_dir, "assets"),
                soldout
            )

        logger.info("index.html の生成処理を開始します。")
        write_index_html(web_dir, show_dev_ui=args.show_dev_ui)
        validate_all(web_dir)
    
        logger.info(f"WebMenuGenerate 処理が正常に完了いたしました。出力先: {out_root}")
        
    except Exception as e:
        logger.error("WebMenuGenerate 処理中にエラーが発生しました。")
        logger.error("エラー種別: %s", type(e).__name__)
        logger.error("エラーメッセージ: %s", str(e))
        logger.error("入力パラメータ: ref=%s, out=%s, free=%s, osusume=%s, schema_version=%s",args.ref, args.out, args.free, args.osusume, args.schema_version)
        logger.exception("スタックトレース詳細")
        raise

        
    