# 先頭のimportをこうする（os/jsonはトップレベルで）
import os
import json
import datetime

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

ASSET_PREFIX_FREE = "free_images/"


def _normalize_asset_path(name: str) -> str:
    if not name:
        return ""
    name = str(name).strip()
    if not name:
        return ""
    return name


def collect_required_assets(small_pages: dict) -> set[str]:
    assets: set[str] = set()
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


def run_pipeline(args):
    # ★ここから下、関数内に「import json, os」は置かない！
    ref = args.ref or datetime.datetime.now().strftime("%Y%m%d-%H%M%S-000000")
    out_root = os.path.join(args.out, "builds", ref)
    raw_dump_dir = os.path.join(out_root, "raw_dump")
    web_dir = os.path.join(out_root, "web_content")

    os.makedirs(raw_dump_dir, exist_ok=True)
    os.makedirs(web_dir, exist_ok=True)

    # Parse legacy
    ini_bundle = load_all_ini(os.path.join(args.free, "config"))
    menudb_path = os.path.join(args.free, "datas", "menudb.dat")
    menudb = read_menudb(menudb_path)
    osusume = read_osusume(args.osusume)

    # Raw dump
    write_raw_dump(raw_dump_dir, ini_bundle, menudb, osusume)

    # Mapping to web_content
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

    write_index_html(web_dir, show_dev_ui=args.show_dev_ui)
    validate_all(web_dir)
    print(f"Done → {out_root}")
