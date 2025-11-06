
import re


def make_soldout_json(ini_bundle):
    soldout_settings = (
        ini_bundle
        .get("menu.ini", {})
        .get("sections", {})
        .get("soldout", {})
    )
    
    osusume_settings = (
        ini_bundle
        .get("menu.ini", {})
        .get("sections", {})
        .get("osusume", {})
    )
    
    frm_btn_images = {}
    cell_btn_images = {}
    sort_soldout_state = {}
    
    frm_pattern = re.compile(r"^FrmBtnImgName(\d*)$")
    cell_pattern = re.compile(r"^CellBtnImgName(\d*)$")
    sort_pattern = re.compile(r"^SortSoldoutState(\d*)$")
    
    for key, filename in soldout_settings.items():
        frm_match = frm_pattern.match(key)
        if frm_match:
            index = frm_match.group(1)
            index = index if index else "1"
            frm_btn_images[index] = filename
            continue
        
        cell_match = cell_pattern.match(key)
        if cell_match:
            index = cell_match.group(1)
            index = index if index else "1"
            cell_btn_images[index] = filename
            continue
    for key, state in osusume_settings.items():
        sort_match = sort_pattern.match(key)
        if sort_match:
            index = sort_match.group(1)
            index = index if index else "1"
            sort_soldout_state[index] = state

    return {
        "backImage": soldout_settings.get("BackImgName", ""),
        "frm_btn_images": frm_btn_images,
        "cell_btn_images": cell_btn_images,
        "use_item_sort": sort_soldout_state.get("UseItemSort","0"),
        "sort_item_frame": sort_soldout_state.get("SortItemFrame","0"), 
        "sort_soldout_state": sort_soldout_state
    }