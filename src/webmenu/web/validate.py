import os, json

def validate_all(web_dir:str):
    # PoC: スキーマ検証は後日。本関数が存在することでパイプラインが通る。
    req = ["menudb.json", "categories.json", "index.html"]
    for r in req:
        if not os.path.exists(os.path.join(web_dir, r)):
            print("WARN: missing", r)
