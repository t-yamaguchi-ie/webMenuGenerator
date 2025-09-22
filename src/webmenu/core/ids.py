"""ID/命名規約の管理。"""

def small_id(large_idx:int, middle_idx:int, small_idx:int) -> str:
    return f"sm-{large_idx:02d}{middle_idx:02d}{small_idx:03d}"

def page_relpath(small_id:str, page:int) -> str:
    return f"small/{small_id}/page-{page}.json"
