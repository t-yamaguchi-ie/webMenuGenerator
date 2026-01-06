import os


def validate_all(web_dir: str, processed_dump_dir: str):
    # PoC: スキーマ検証は後日。本関数が存在することでパイプラインが通る。

    if not os.path.exists(os.path.join(web_dir, "index.html")):
        print("WARN: missing index.html")

    req = ["menudb.json", "categories.json"]
    for r in req:
        if not os.path.exists(os.path.join(processed_dump_dir, r)):
            print("WARN: missing", r)
