
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
    
    kt_settings = (
        ini_bundle
        .get("menu.ini", {})
        .get("sections", {})
        .get("hm", {})
    )
    
    frm_btn_images = {}
    cell_btn_images = {}
    sort_soldout_state = {}
    kt_soldout_state = {}
    
    frm_pattern = re.compile(r"^FrmBtnImgName(\d*)$")
    cell_pattern = re.compile(r"^CellBtnImgName(\d*)$")
    sort_pattern = re.compile(r"^SortSoldoutState(\d*)$")
    kt_soldout_pattern = re.compile(r"^SoldOutState(\d*)$")
    
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
            
    for key, state in kt_settings.items():
        kt_soldout_match = kt_soldout_pattern.match(key)
        if kt_soldout_match:
            index = kt_soldout_match.group(1)
            index = index if index else "1"
            kt_soldout_state[index] = state

    return {
        "backImage": soldout_settings.get("BackImgName", ""),
        "frm_btn_images": frm_btn_images,
        "cell_btn_images": cell_btn_images,
        "use_item_sort": osusume_settings.get("UseItemSort","0"),
        "sort_hide_frame": osusume_settings.get("SortHideFrame","0"), 
        "sort_soldout_state": sort_soldout_state,
        "kt_soldout_state": kt_soldout_state
    }