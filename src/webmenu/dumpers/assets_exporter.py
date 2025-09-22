import os, shutil

def export_assets(free_dir:str, osusume_dir:str, out_assets_dir:str):
    os.makedirs(out_assets_dir, exist_ok=True)
    # 最低限: free/images をコピー（PoC）
    src = os.path.join(free_dir, "images")
    if os.path.isdir(src):
        dst = os.path.join(out_assets_dir, "free_images")
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    # TODO: osusume 側の画像コピーも追加
