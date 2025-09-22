import os, json

def write_raw_dump(raw_dump_dir:str, ini_bundle, menudb, osusume):
    os.makedirs(raw_dump_dir, exist_ok=True)
    # ini
    ini_dir = os.path.join(raw_dump_dir, "ini")
    os.makedirs(ini_dir, exist_ok=True)
    for fname, payload in ini_bundle.items():
        with open(os.path.join(ini_dir, fname + ".json"), "w", encoding="utf-8") as f:
            json.dump({"__file": fname, **payload}, f, ensure_ascii=False, indent=2)

    # menudb (スタブ構成)
    mdir = os.path.join(raw_dump_dir, "menudb")
    os.makedirs(mdir, exist_ok=True)
    with open(os.path.join(mdir, "lmenus.json"), "w", encoding="utf-8") as f:
        json.dump(menudb.get("lmenus", []), f, ensure_ascii=False, indent=2)
    with open(os.path.join(mdir, "mmenus.json"), "w", encoding="utf-8") as f:
        json.dump(menudb.get("mmenus", []), f, ensure_ascii=False, indent=2)
    with open(os.path.join(mdir, "smenus.json"), "w", encoding="utf-8") as f:
        json.dump(menudb.get("smenus", []), f, ensure_ascii=False, indent=2)
    with open(os.path.join(mdir, "item_infos.json"), "w", encoding="utf-8") as f:
        json.dump(menudb.get("item_infos", []), f, ensure_ascii=False, indent=2)
    with open(os.path.join(mdir, "item_cells.json"), "w", encoding="utf-8") as f:
        json.dump(menudb.get("item_cells", []), f, ensure_ascii=False, indent=2)
    with open(os.path.join(mdir, "item_frames.json"), "w", encoding="utf-8") as f:
        json.dump(menudb.get("item_frames", []), f, ensure_ascii=False, indent=2)

    # osusume
    with open(os.path.join(raw_dump_dir, "osusume.json"), "w", encoding="utf-8") as f:
        json.dump(osusume, f, ensure_ascii=False, indent=2)
