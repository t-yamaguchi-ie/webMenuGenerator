"""レガシー→Web の参照テーブル。解析時に随時格納する。"""

class RefTable:
    def __init__(self):
        self.small_addr_to_id = {}
        self.page_index = {}  # (small_id) -> page_count/int など

    def bind_small(self, addr:int, small_id:str):
        self.small_addr_to_id[addr] = small_id
