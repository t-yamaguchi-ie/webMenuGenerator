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
from .web.html_skeleton import write_index_html
from .web.validate import validate_all
from .dumpers.assets_exporter import export_assets

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
    categories = make_categories(menudb, ini_bundle, schema_version=args.schema_version)
    small_pages = make_small_pages(menudb, osusume, ini_bundle, schema_version=args.schema_version)

    # Emit web_content
    with open(os.path.join(web_dir, "menudb.json"), "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    with open(os.path.join(web_dir, "categories.json"), "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    for rel_path, payload in small_pages.items():
        p = os.path.join(web_dir, rel_path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    if not args.skip_assets:
        export_assets(args.free, args.osusume, os.path.join(web_dir, "assets"))

    write_index_html(web_dir)
    validate_all(web_dir)
    print(f"Done → {out_root}")
