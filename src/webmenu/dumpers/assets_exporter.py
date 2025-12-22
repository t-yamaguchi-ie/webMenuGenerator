import os, shutil

FREE_PREFIX = "free_images/"
OSUSUME_PREFIX = "osusume_images/"
SOLDOUT_PREFIX = "soldout_images/"


def export_assets(free_dir:str, osusume_dir:str, out_assets_dir:str, required_assets=None):
    if required_assets:
        assets = sorted({asset for asset in required_assets if asset})
        os.makedirs(out_assets_dir, exist_ok=True)

        for rel in assets:
            src_path = None
            if rel.startswith(FREE_PREFIX):
                rel_sub = rel[len(FREE_PREFIX):]
                src_path = os.path.join(free_dir, "images", rel_sub)
            elif rel.startswith(OSUSUME_PREFIX):
                rel_sub = rel[len(OSUSUME_PREFIX):]
                src_path = os.path.join(osusume_dir, "smenu", rel_sub)
            else:
                # fallback: treat as free/images root
                src_path = os.path.join(free_dir, "images", rel)

            if not src_path or not os.path.isfile(src_path):
                continue

            dst_path = os.path.join(out_assets_dir, rel)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
        return

    os.makedirs(out_assets_dir, exist_ok=True)
    src = os.path.join(free_dir, "images")
    dst = os.path.join(out_assets_dir, "free_images")
    if not os.path.isdir(src):
        return
    
    for root, dirs, files in os.walk(src):
        rel_dir = os.path.relpath(root, src)
        dst_dir = dst if rel_dir == "." else os.path.join(dst, rel_dir)

        os.makedirs(dst_dir, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_dir, file)
            shutil.copy2(src_file, dst_file)
            

def export_soldout_assets(free_dir:str,out_assets_dir:str, soldout):
    if not soldout:
        return
    
    source_dir = os.path.join(free_dir, "images")
    target_dir = os.path.join(out_assets_dir, "soldout_images")
    os.makedirs(target_dir, exist_ok=True)
    
    image_files = set()
    
    def is_image_file(value: str) -> bool:
        return value.lower().endswith((
            ".jpg", ".jpeg", ".png", ".gif", ".webp"
        ))
    
    def collect_images(d):
        for value in d.values():
            if isinstance(value, dict):
                collect_images(value)
            elif isinstance(value, str) and is_image_file(value):
                image_files.add(value)

    collect_images(soldout)

    for image in image_files:
        source_path = os.path.join(source_dir, image)
        target_path = os.path.join(target_dir, image)

        if os.path.isfile(source_path):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(source_path, target_path)


def export_jump_btn_assets(free_dir:str,osusume_dir:str,out_assets_dir:str, jump_btns):
    buttons = jump_btns.get("jumpmenu", {}).get("buttons", [])
    if not buttons:
        return
    
    image_files = set()
    
    for btn in buttons:
        image_map = btn.get("image", {})
        if not isinstance(image_map, dict):
            continue

        for path in image_map.values():
            if path:
                image_files.add(path)
                
    for image in image_files:
        if image.startswith(FREE_PREFIX):
            rel = image[len(FREE_PREFIX):]
            src_path = os.path.join(free_dir, "images", rel)
        elif image.startswith(OSUSUME_PREFIX):
            rel = image[len(OSUSUME_PREFIX):]
            src_path = os.path.join(osusume_dir, "smenu", rel)
        else:
            src_path = os.path.join(free_dir, "images", image)

        if not os.path.isfile(src_path):
            continue

        dst_path = os.path.join(out_assets_dir, image)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)


def export_checkin_btn_assets(
    free_dir: str,
    osusume_dir: str,
    out_assets_dir: str,
    checkin_btn
):
    checkin = checkin_btn.get("checkin_hansoku", {})
    screens = checkin.get("screens", {})

    if not screens:
        return

    image_files = set()

    def collect_image_map(image_map):
        if not isinstance(image_map, dict):
            return
        for path in image_map.values():
            if path:
                image_files.add(path)

    for screen in screens.values():
        collect_image_map(screen.get("background"))
        for btn in screen.get("buttons", []):
            collect_image_map(btn.get("image"))

    for image in image_files:
        if image.startswith(FREE_PREFIX):
            rel = image[len(FREE_PREFIX):]
            src_path = os.path.join(free_dir, "images", rel)

        elif image.startswith(OSUSUME_PREFIX):
            rel = image[len(OSUSUME_PREFIX):]
            src_path = os.path.join(osusume_dir, "smenu", rel)

        else:
            src_path = os.path.join(free_dir, "images", image)

        if not os.path.isfile(src_path):
            continue

        dst_path = os.path.join(out_assets_dir, image)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
