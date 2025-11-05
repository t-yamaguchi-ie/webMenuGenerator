import os, shutil

FREE_PREFIX = "free_images/"
OSUSUME_PREFIX = "osusume_images/"
SOLDOUT_PREFIX = "soldout_images/"


def export_assets(free_dir:str, osusume_dir:str, out_assets_dir:str, required_assets=None):
    if required_assets:
        assets = sorted({asset for asset in required_assets if asset})
        if os.path.isdir(out_assets_dir):
            shutil.rmtree(out_assets_dir)
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
    if os.path.isdir(src):
        dst = os.path.join(out_assets_dir, "free_images")
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    # TODO: osusume 側の画像コピーも追加


def export_soldout_assets(free_dir:str,out_assets_dir:str, soldout):
    if not soldout:
        return
    
    source_dir = os.path.join(free_dir, "images")
    target_dir = os.path.join(out_assets_dir, "soldout")
    os.makedirs(target_dir, exist_ok=True)
    
    
    def copy_images(d):
        for key, value in d.items():
            if isinstance(value, dict):
                copy_images(value)
            elif isinstance(value, str) and value.strip():
                source_path = os.path.join(source_dir, value)
                target_path = os.path.join(target_dir, value)
                if os.path.exists(source_path):
                    shutil.copy2(source_path, target_path)

    copy_images(soldout)
