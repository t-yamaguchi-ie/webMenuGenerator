import os
from typing import List, Dict, Optional
from ..core.ids import small_id


def _check_is_multi_lang(free_dir: str) -> List[str]:
    """
    images ディレクトリ直下に存在し、
    かつ内部にファイルを含むサブディレクトリ名の一覧を返す。
    """
    image_path = os.path.join(free_dir, "images")
    result: List[str] = []

    # images 直下を走査
    for entry in os.listdir(image_path):
        full_path = os.path.join(image_path, entry)

        # サブディレクトリのみ対象
        if os.path.isdir(full_path):
            # サブディレクトリ内にファイルがあるか確認
            for sub in os.listdir(full_path):
                sub_path = os.path.join(full_path, sub)
                if os.path.isfile(sub_path):
                    result.append(entry)
                    break  # 同じディレクトリは一度だけ追加

    return result


def _get_image_path(
    free_dir: str,
    osusume_dir: str,
    name: str,
    multi_lang_dirs: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    画像パスの map を返す。
    戻り値は常に Dict[str, str]。
    """
    if not name:
        return {}

    result: Dict[str, str] = {}
    multi_lang_dirs = multi_lang_dirs or []

    free_image_base = os.path.join(free_dir, "images")
    osusume_image_base = os.path.join(osusume_dir, "smenu", "menu", "images")

    # freeディレクトリから画像を優先的に取得
    file_path = os.path.join(free_image_base, name)
    if os.path.isfile(file_path):
        result["default"] = f"free_images/{name}"

    # osusumeディレクトリに同名画像が存在する場合は、freeの画像を置き換え
    file_path = os.path.join(osusume_image_base, name)
    if os.path.isfile(file_path):
        result["default"] = f"osusume_images/menu/images/{name}"

    # ---- 多言語なし ----
    if not multi_lang_dirs:
        return result

    # ---- 多言語あり ----
    for lang in multi_lang_dirs:
        # osusume を優先
        file_path = os.path.join(osusume_image_base, lang, name)
        if os.path.isfile(file_path):
            result[lang] = f"osusume_images/menu/images/{lang}/{name}"
            continue

        # osusume に無い場合は free を確認
        file_path = os.path.join(free_image_base, lang, name)
        if os.path.isfile(file_path):
            result[lang] = f"free_images/{lang}/{name}"
            continue

        # 両方無い場合は何もしない
        continue

    return result


def _filename_label(name: str, fallback: str) -> str:
    if not name:
        return fallback
    base = name.rsplit('/', 1)[-1]
    base = base.rsplit('.', 1)[0]
    return base or fallback


def make_categories(free_dir: str, osusume_dir: str, menudb, ini_bundle, small_pages, schema_version="0.1"):
    lmenus = menudb.get("lmenus", [])
    mmenus = menudb.get("mmenus", [])
    smenus = menudb.get("smenus", [])
    item_infos = menudb.get("item_infos", [])

    products_by_code = {str(info.get("code")): info.get(
        "name", "") for info in item_infos}

    small_page_map = {}
    for path, payload in (small_pages or {}).items():
        parts = path.split('/')
        if len(parts) >= 2:
            sid = parts[1]
            small_page_map[sid] = {
                "path": path,
                "payload": payload,
            }

    smenu_offset_index = {
        sm.get("offset"): idx for idx, sm in enumerate(smenus)}

    # 多言語対応画像ディレクトリ一覧を取得
    multi_lang_dirs = _check_is_multi_lang(free_dir)

    tree = []
    for lmenu in lmenus:
        if not lmenu:
            continue
        if lmenu.get("property", 0) == 0:
            continue
        l_index = lmenu.get("index") or 0
        l_id = f"L{l_index:02d}"
        l_label = _filename_label(lmenu.get("scrBtnImg", ""), l_id)

        # 大分類関連画像を取得する
        l_scr_btn_img = _get_image_path(
            free_dir, osusume_dir, lmenu.get("scrBtnImg", ""), multi_lang_dirs)
        l_frm_back_img = _get_image_path(
            free_dir, osusume_dir, lmenu.get("lmFrmBackImg", ""), multi_lang_dirs)
        l_frm_off_btn_img = _get_image_path(
            free_dir, osusume_dir, lmenu.get("frmOffBtnImg", ""), multi_lang_dirs)
        l_frm_on_btn_img = _get_image_path(
            free_dir, osusume_dir, lmenu.get("frmOnBtnImg", ""), multi_lang_dirs)
        l_m_frm_back_img = _get_image_path(
            free_dir, osusume_dir, lmenu.get("mmFrmBackImg", ""), multi_lang_dirs)
        children = []
        for mmenu in mmenus:
            if mmenu.get("l_index") != l_index:
                continue
            if mmenu.get("property", 0) == 0:
                continue

            m_index = mmenu.get("index") or 0
            m_id = f"M{l_index:02d}{m_index:02d}"
            m_label = _filename_label(mmenu.get("btnOnImg", ""), m_id)

            # 中分類関連画像を取得する
            m_btn_on_img = _get_image_path(
                free_dir, osusume_dir, mmenu.get("btnOnImg", ""), multi_lang_dirs)
            m_btn_off_img = _get_image_path(
                free_dir, osusume_dir, mmenu.get("btnOffImg", ""), multi_lang_dirs)

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
                if not sm:
                    continue
                if sm.get("showType", 0) != 6 and sm.get("itemNum", 0) == 0:
                    continue
                sid = small_id(l_index, m_index, sm.get("index", 0))
                info = small_page_map.get(sid)
                if not info:
                    continue

                payload = info["payload"]
                grid_items = payload.get("grid_items", [])
                page_meta = payload.get("page_meta", {})
                layout_type = payload.get(
                    "layout_type", page_meta.get("layout_type", "free"))
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
                    "index": m_index,
                    "property": mmenu.get("property", 0),
                    "btn_on_img": m_btn_on_img,
                    "btn_off_img": m_btn_off_img,
                    "pages": pages,
                })

        if children:
            tree.append({
                "id": l_id,
                "label": l_label,
                "index": l_index,
                "property": lmenu.get("property", 0),
                "free_flag": lmenu.get("freeFlg", 0),
                "scr_btn_img": l_scr_btn_img,
                "frm_back_img": l_frm_back_img,
                "frm_off_btn_img": l_frm_off_btn_img,
                "frm_on_btn_img": l_frm_on_btn_img,
                "m_frm_back_img": l_m_frm_back_img,
                "children": children,
            })

    return {
        "schema_version": schema_version,
        "tree": tree
    }
