from ..core.ids import small_id


def _filename_label(name: str, fallback: str) -> str:
    if not name:
        return fallback
    base = name.rsplit('/', 1)[-1]
    base = base.rsplit('.', 1)[0]
    return base or fallback


def make_categories(menudb, ini_bundle, small_pages, schema_version="0.1"):
    lmenus = menudb.get("lmenus", [])
    mmenus = menudb.get("mmenus", [])
    smenus = menudb.get("smenus", [])
    item_infos = menudb.get("item_infos", [])

    products_by_code = {str(info.get("code")): info.get("name", "") for info in item_infos}

    small_page_map = {}
    for path, payload in (small_pages or {}).items():
        parts = path.split('/')
        if len(parts) >= 2:
            sid = parts[1]
            small_page_map[sid] = {
                "path": path,
                "payload": payload,
            }

    smenu_offset_index = {sm.get("offset"): idx for idx, sm in enumerate(smenus)}

    tree = []
    for lmenu in lmenus:
        if not lmenu:
            continue
        if lmenu.get("property", 0) == 0:
            continue
        l_index = lmenu.get("index") or 0
        l_id = f"L{l_index:02d}"
        l_label = _filename_label(lmenu.get("scrBtnImg", ""), l_id)

        children = []
        for mmenu in mmenus:
            if mmenu.get("l_index") != l_index:
                continue
            if mmenu.get("property", 0) == 0:
                continue

            m_index = mmenu.get("index") or 0
            m_id = f"M{l_index:02d}{m_index:02d}"
            m_label = _filename_label(mmenu.get("btnOnImg", ""), m_id)

            sm_addr = mmenu.get("sMenuAddr")
            start_idx = smenu_offset_index.get(sm_addr)
            if start_idx is None:
                continue
            sm_count = max(1, mmenu.get("sMenuNum", 0))

            pages = []
            for seq in range(sm_count):
                sm_idx = start_idx + seq
                if sm_idx >= len(smenus):
                    break
                sm = smenus[sm_idx]
                if not sm or sm.get("itemNum", 0) == 0:
                    continue
                sid = small_id(l_index, m_index, sm.get("index", 0))
                info = small_page_map.get(sid)
                if not info:
                    continue

                payload = info["payload"]
                grid_items = payload.get("grid_items", [])
                page_meta = payload.get("page_meta", {})
                layout_type = payload.get("layout_type", page_meta.get("layout_type", "free"))
                label = sid
                for gi in grid_items:
                    name = products_by_code.get(gi.get("product_code"), "")
                    if name:
                        label = name
                        break

                pages.append({
                    "id": sid,
                    "label": label,
                    "page_path": info["path"],
                    "background": payload.get("background", ""),
                    "layout_type": layout_type,
                    "show_type": page_meta.get("show_type", sm.get("showType", 0)),
                    "sequence": page_meta.get("sequence", seq + 1),
                    "total_in_group": page_meta.get("total_in_group", sm_count),
                    "meta": page_meta,
                    "product_codes": [gi.get("product_code") for gi in grid_items],
                })

            if pages:
                children.append({
                    "id": m_id,
                    "label": m_label,
                    "property": mmenu.get("property", 0),
                    "pages": pages,
                })

        if children:
            tree.append({
                "id": l_id,
                "label": l_label,
                "property": lmenu.get("property", 0),
                "free_flag": lmenu.get("freeFlg", 0),
                "children": children,
            })

    return {
        "schema_version": schema_version,
        "tree": tree
    }
