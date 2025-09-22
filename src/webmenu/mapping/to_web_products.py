# mapping/to_web_products.py はそのまま：
def make_products(menudb, ini_bundle, schema_version="0.1"):
    prods = []
    for it in menudb.get("item_infos", []):
        prods.append({
        "product_code": str(it["code"]),
        "name": it["name"],
        "price": it["price"],
        "menuAtt": it.get("menuAtt", 0),
        "subMenuFlg": it.get("subMenuFlg", 0),
        "image": ""
        })
    return {"schema_version": schema_version, "currency": "JPY", "tax_included": True, "products": prods}
