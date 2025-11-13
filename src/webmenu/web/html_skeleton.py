from pathlib import Path
from textwrap import dedent

_HTML_BEFORE_STYLE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Menu SPA (PoC)</title>
<style>
"""

_CSS_COMMON_TOP = dedent(
    """
    :root { color-scheme: light dark; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      background: #f6f6f6;
    }
    """
).strip()

_CSS_TOOLBAR_VISIBLE = dedent(
    """
    .toolbar {
      max-width: 1000px;
      margin: 24px auto 0;
      display: flex;
      gap: 12px;
      align-items: center;
      padding: 0 16px;
      flex-wrap: wrap;
    }
    """
).strip()

_CSS_TOOLBAR_HIDDEN = dedent(
    """
    .toolbar {
      display: none;
    }
    """
).strip()

_CSS_TOOLBAR_COMMON = dedent(
    """
    .toolbar-group {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .toolbar label {
      font-size: 13px;
      color: #444;
    }
    .toolbar select,
    .toolbar button {
      padding: 6px 10px;
      font-size: 13px;
    }
    """
).strip()

_CSS_STAGE = dedent(
    """
    .stage {
      width: 1000px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    """
).strip()

_CSS_LOG_VISIBLE = dedent(
    """
    #log {
      font-size: 14px;
      color: #333;
      padding: 0 4px;
    }
    """
).strip()

_CSS_LOG_HIDDEN = dedent(
    """
    #log {
      display: none;
    }
    """
).strip()

_CSS_CANVAS = dedent(
    """
    .canvas {
      position: relative;
      width: 1000px;
      height: 533px;
      border: 1px solid #d0d0d0;
      overflow: hidden;
      background: #f2f2f2 center/cover no-repeat;
      box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    """
).strip()

_CSS_GRID = dedent(
    """
    .grid {
      position: relative;
      width: 100%;
      height: 100%;
    }
    """
).strip()

_CSS_TILE = dedent(
    """
    .tile {
      position: absolute;
      box-sizing: border-box;
      background: transparent;
      border: none;
      overflow: hidden;
    }
    """
).strip()

_CSS_TILE_INNER = dedent(
    """
    .tile-inner {
      position: relative;
      width: 100%;
      height: 100%;
    }
    """
).strip()

_CSS_TILE_IMAGE = dedent(
    """
    .tile-inner img {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      background: #ececec;
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    .tile-inner img.is-loaded {
      opacity: 1;
    }
    """
).strip()

_CSS_SOLDOUT_LAYER = dedent(
    """
    .tile-inner div.soldout-layer {
      position: absolute;
      inset: 0;
      display: none; 
      justify-content: center;
      align-items: center;
      pointer-events: auto;
      background: transparent; 
      z-index: 20;
    }
    """
).strip()

_CSS_SOLDOUT = dedent(
    """
    .tile-inner img.soldout-img {
      position: absolute;
      background: transparent;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: auto;
      height: auto;
      opacity: 1;
    }
    """
).strip()

_CSS_CELL_LAYER = dedent(
    """
    .cell-layer {
      display: none;
    }
    """
).strip()

_CSS_CELL_BOX = dedent(
    """
    .cell-box {
      position: absolute;
      border: 1px solid rgba(0, 120, 255, 0.5);
      background: rgba(0, 120, 255, 0.15);
      box-sizing: border-box;
    }
    """
).strip()

_CSS_TILE_META = dedent(
    """
    .tile .meta {
      display: none;
    }
    """
).strip()

_HTML_AFTER_STYLE = """</style>
</head>
<body>
<div class="toolbar">
  <div class="toolbar-group">
    <label for="lSelect">L</label>
    <select id="lSelect"></select>
  </div>
  <div class="toolbar-group">
    <label for="mSelect">M</label>
    <select id="mSelect"></select>
  </div>
  <div class="toolbar-group">
    <label for="sSelect">S</label>
    <select id="sSelect"></select>
  </div>
  <button id="btn">Load</button>
</div>
<div class="stage">
  <div id="log">Ready</div>
  
  <div id="canvas" class="canvas">
    <div id="grid" class="grid"></div>
  </div>
</div>
<script>
const CANVAS_WIDTH = 1000;
const CANVAS_HEIGHT = 533;
const ABS_COLS = 40;
const ABS_ROWS = 20;
const cache = { products: null, categories: null, cells: new Map(), soldout_settings: null };

<!-- 現在の言語設定を維持する -->
let currentLangPath = "default";

<!-- 品切れ情報を維持する -->
let soldOutData = new Map();

async function fetchJson(path) {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json();
}

async function ensureProducts() {
  if (cache.products) {
    return cache.products;
  }
  const menudb = await fetchJson('./menudb.json');
  cache.products = new Map((menudb.products || []).map(p => [p.product_code, p]));
  return cache.products;
}

async function ensureCategories() {
  if (cache.categories) {
    return cache.categories;
  }
  const cats = await fetchJson('./categories.json');
  cache.categories = cats;
  return cats;
}

async function ensureCells(path) {
  if (!path) {
    return null;
  }
  if (cache.cells.has(path)) {
    return cache.cells.get(path);
  }
  const data = await fetchJson(`./${path}`);
  cache.cells.set(path, data);
  return data;
}

<!-- 品切れ設定情報を取得する -->
async function ensureSoldoutSettings() {
  if (cache.soldout_settings) {
    return cache.soldout_settings;
  }
  const soldout_settings = await fetchJson('./soldout.json');
  cache.soldout_settings = soldout_settings;
  return soldout_settings;
}

function applyBackground(canvasEl, page) {
  const bg = page.background ? `url(./assets/${page.background})` : 'none';
  canvasEl.style.backgroundImage = bg;
}

function layoutCanvas(items) {
  if (!items.length) {
    return {
      mode: 'absolute',
      offsetX: 1,
      offsetY: 1,
      scaleX: CANVAS_WIDTH / ABS_COLS,
      scaleY: CANVAS_HEIGHT / ABS_ROWS
    };
  }
  const xs = items.map(i => i.cell?.[0] ?? 0);
  const ys = items.map(i => i.cell?.[1] ?? 0);
  const minX = Math.min(...xs);
  const minY = Math.min(...ys);
  const maxX = Math.max(...xs);
  const maxY = Math.max(...ys);

  const fitsAbsolute = maxX <= ABS_COLS && maxY <= ABS_ROWS && minX >= 1 && minY >= 1;
  if (fitsAbsolute) {
    return {
      mode: 'absolute',
      offsetX: 1,
      offsetY: 1,
      scaleX: CANVAS_WIDTH / ABS_COLS,
      scaleY: CANVAS_HEIGHT / ABS_ROWS
    };
  }

  const cols = Math.max(1, (maxX - minX) + 1);
  const rows = Math.max(1, (maxY - minY) + 1);
  return {
    mode: 'relative',
    offsetX: minX,
    offsetY: minY,
    scaleX: CANVAS_WIDTH / cols,
    scaleY: CANVAS_HEIGHT / rows
  };
}

function renderTiles(gridEl, items, productMap, layout, cellsData, layoutType, soldout_settings) {
  const tiles = [];
  let renderIndex = 0; // 可见タイルのレンダリング順インデックス
  
  for (let i = 0; i < items.length; i++) {
    const gi = items[i];
    // 表示位置を決定
    const placeInfo = items[renderIndex];
    
    <!-- 品切れ整列機能 -->
    const soldOutState = getSoldOutState(gi, soldout_settings);
    // gi.osusume が存在しない、またはおすすめフレーム非表示、または品切れの場合は非表示対象
    const isSortTarget = (
      !gi.osusume || 
      (soldout_settings?.sort_hide_frame === "1" && gi.osusume.show === "0") ||
      soldOutState === "1"
    );
      
    // 並べ替えが有効な場合のみ前詰め処理
    if (soldout_settings?.use_item_sort === "1") {
      if (!isSortTarget) {
        // 非表示でない場合はレンダリングインデックスを使う
        renderIndex++;
      } else {
        // 非表示の場合はスキップ
        continue;
      }
    } else {
      // 並べ替え無効の場合は元のインデックスを使用
      renderIndex = i;
    }
    
    const product = productMap.get(gi.product_code) || {};
    const tile = document.createElement('div');
    tile.className = 'tile';
    tile.dataset.code = gi.product_code;
    if (layoutType === 'recommended' || gi.osusume) {
      tile.classList.add('tile--recommended');
    }

    const spanX = Math.max(1, placeInfo.span?.[0] ?? 1);
    const spanY = Math.max(1, placeInfo.span?.[1] ?? 1);
    const rawX = placeInfo.cell?.[0] ?? 0;
    const rawY = placeInfo.cell?.[1] ?? 0;

    const left = (rawX - layout.offsetX) * layout.scaleX;
    const top = (rawY - layout.offsetY) * layout.scaleY;
    const width = spanX * layout.scaleX;
    const height = spanY * layout.scaleY;

    tile.style.left = `${left}px`;
    tile.style.top = `${top}px`;
    tile.style.width = `${width}px`;
    tile.style.height = `${height}px`;

    const inner = document.createElement('div');
    inner.className = 'tile-inner';
    tile.appendChild(inner);
   
    <!--  画像を生成 -->
    let imageSrc = getMultiLangImage(gi, product);
    if (imageSrc) {
      const img = document.createElement('img');
      img.src = imageSrc;
      img.alt = '';
      img.dataset.code = gi.product_code;
      const markLoaded = () => {
        requestAnimationFrame(() => img.classList.add('is-loaded'));
      };
      if (img.complete) {
        markLoaded();
      } else {
        img.addEventListener('load', markLoaded, { once: true });
        img.addEventListener('error', markLoaded, { once: true });
      }
      
      <!--  クリックイベントを追加 -->
      const link = document.createElement('a');
      link.href = `a-menu://webAddOrder?data=${encodeURIComponent(JSON.stringify(gi))}`;
      link.appendChild(img);
      inner.appendChild(link);
    }
    
    <!--  品切れ画像表示 -->
    const soldoutLayer = document.createElement('div');
    soldoutLayer.className = 'soldout-layer';
    soldoutLayer.dataset.code = gi.product_code;
    soldoutLayer.style.display = 'none';
    
    const soldoutImg  = document.createElement('img');
    soldoutImg.className = 'soldout-img';
    soldoutImg.alt = 'Sold Out';
    soldoutImg.dataset.code = gi.product_code;
    soldoutImg.style.display = 'none';
    
    soldoutLayer.appendChild(soldoutImg);
      
    let soldOutImgSrc = getSoldOutImage(gi, soldout_settings);
    
    if (soldOutImgSrc) {
      soldoutImg.src = soldOutImgSrc;
      soldoutImg.style.display = "";
     
      soldoutLayer.style.display = "flex";
      soldoutLayer.style.pointerEvents = "auto";
      soldoutLayer.addEventListener('click', e => {
        e.preventDefault();
        e.stopPropagation();
      });
    } else {
      soldoutImg.style.display = "none";
      
      soldoutLayer.style.pointerEvents = "none";
      soldoutLayer.style.display = "none";
    }
    
    const soldOutFlag = soldOutData.get(gi.product_code);
    soldoutImg.style.width = (soldOutFlag === 4) ? "100%" : "auto";
    soldoutImg.style.height = (soldOutFlag === 4) ? "100%" : "auto";
    
    inner.appendChild(soldoutLayer);

    const cellsPath = gi.cells_path;
    const cellEntries = cellsPath ? (cellsData[cellsPath]?.cells || {}) : {};
    const cellCoords = cellEntries[gi.product_code] || [];
    if (cellCoords.length) {
      const layer = document.createElement('div');
      layer.className = 'cell-layer';
      const baseX = gi.cell?.[0] ?? 0;
      const baseY = gi.cell?.[1] ?? 0;
      for (const [cx, cy] of cellCoords) {
        const cellDiv = document.createElement('div');
        cellDiv.className = 'cell-box';
        cellDiv.style.left = `${(cx - baseX) * layout.scaleX}px`;
        cellDiv.style.top = `${(cy - baseY) * layout.scaleY}px`;
        cellDiv.style.width = `${layout.scaleX}px`;
        cellDiv.style.height = `${layout.scaleY}px`;
        layer.appendChild(cellDiv);
      }
      inner.appendChild(layer);
    }

    const osusumeMeta = gi.osusume || {};
    const name = (layoutType === 'recommended' && osusumeMeta.text1) ? osusumeMeta.text1 : (product.name || gi.product_detail?.name || gi.product_code);
    const price = (() => {
      if (layoutType === 'recommended' && osusumeMeta.tanka) {
        return `¥${osusumeMeta.tanka}`;
      }
      if (product.price != null) {
        return `¥${product.price}`;
      }
      const fallback = gi.product_detail?.price;
      return fallback != null ? `¥${fallback}` : '-';
    })();
    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.innerHTML = `
      <div>${name}</div>
      <span class="price">${price}</span>`;
    inner.appendChild(meta);

    tiles.push(tile);
  }

  gridEl.replaceChildren(...tiles);
}

async function run() {
  const canvas = document.getElementById('canvas');
  const log = document.getElementById('log');
  const grid = document.getElementById('grid');
  const sid = getSelectedSmallId();
  if (!sid) {
    log.textContent = 'small ID が未入力です';
    grid.innerHTML = '';
    canvas.style.backgroundImage = 'none';
    return;
  }

  try {
    const productMap = await ensureProducts();
    const page = await fetchJson(`./small/${sid}/page-1.json`);

    const uniquePaths = Array.from(new Set((page.grid_items || []).map(it => it.cells_path).filter(Boolean)));
    const cellsData = {};
    for (const path of uniquePaths) {
      cellsData[path] = await ensureCells(path);
    }

    applyBackground(canvas, page);
    const layout = layoutCanvas(page.grid_items || []);
    const layoutType = page.layout_type || page.page_meta?.layout_type || 'free';
    const soldout_settings = await ensureSoldoutSettings();
    renderTiles(grid, page.grid_items || [], productMap, layout, cellsData, layoutType, soldout_settings);

    log.textContent = `Loaded ${sid} (items: ${page.grid_items?.length || 0}, layout: ${page.layout_type})`;
  } catch (err) {
    console.error(err);
    log.textContent = 'Error: ' + err.message;
    grid.innerHTML = '';
    canvas.style.backgroundImage = 'none';
  }
}

document.getElementById('btn').addEventListener('click', run);

function getSelectedSmallId() {
  const sSelect = document.getElementById('sSelect');
  return sSelect ? (sSelect.value || '') : '';
}

function populateSelect(selectEl, options) {
  selectEl.innerHTML = options.map(opt => `<option value="${opt.value}">${opt.label}</option>`).join('');
}

function handleSelectionChange(cats, initialLoad=false) {
  const lSelect = document.getElementById('lSelect');
  const mSelect = document.getElementById('mSelect');
  const sSelect = document.getElementById('sSelect');

  const lNode = (cats.tree || []).find(l => l.id === lSelect.value) || (cats.tree || [])[0];
  if (lNode) {
    populateSelect(mSelect, (lNode.children || []).map(m => ({ value: m.id, label: m.label })));
  } else {
    populateSelect(mSelect, []);
  }

  const mNode = (lNode?.children || []).find(m => m.id === mSelect.value) || (lNode?.children || [])[0];
  if (mNode) {
    populateSelect(sSelect, (mNode.pages || []).map(p => ({ value: p.id, label: p.label })));
  } else {
    populateSelect(sSelect, []);
  }

  if (!initialLoad) {
    run();
  }
}

<!--大分類の切り替え -->
function changeLMenu(lValue) {
    var select = document.getElementById('lSelect');
    select.value = `L${String(lValue).padStart(2, '0')}`; 
    select.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
}

<!--中分類の切り替え -->
function changeMMenu(lValue, mValue) {
    changeLMenu(lValue);
    
    var select = document.getElementById('mSelect');
    select.value = `M${String(lValue).padStart(2, '0')}${String(mValue).padStart(2, '0')}`; 
    select.dispatchEvent(new Event('change', { bubbles: true }));
 
    return true;
}

<!-- 多言語情報を取得する -->
function receiveLangMsg(langPath) {
    currentLangPath = langPath || "default";
    refreshAllImages();
}

<!-- 多言語対応の画像パスを取得する -->
function getMultiLangImage(gi,product) {
    let imageSrc = '';

    if (gi.multi_lang_images) {
        if (gi.multi_lang_images[currentLangPath]) {
            imageSrc = gi.multi_lang_images[currentLangPath];
        } else {
            imageSrc = gi.multi_lang_images["default"] || '';
        }
    }

    if (!imageSrc) {
        imageSrc = gi.image || product.image || '';
    }
    
    if (imageSrc && !imageSrc.startsWith('./') && !imageSrc.startsWith('/') && !imageSrc.startsWith('http') && !imageSrc.startsWith('data:')) {
        imageSrc = `./assets/${imageSrc}`;
    }
    
    return imageSrc;
}

<!-- 商品画像を言語に合わせて更新する -->
async function refreshAllImages() {
    const sid = getSelectedSmallId();
    if (!sid) {
      log.textContent = 'small ID が未入力です';
      grid.innerHTML = '';
      canvas.style.backgroundImage = 'none';
      return;
    }
        
    const productMap = await ensureProducts();
    const page = await fetchJson(`./small/${sid}/page-1.json`);
    const gridItems = page.grid_items || [];
    
    const imgs = document.querySelectorAll('img[data-code]');

    imgs.forEach(img => {
      const code = img.dataset.code;
      const gi = gridItems.find(g => g.product_code === code);
      const product = productMap.get(code) || {};
      if (!gi) return;
      
      let newSrc = getMultiLangImage(gi, product);
      img.src = newSrc;
    });
}

<!-- 品切れ情報を取得する -->
async function receiveSoldOutMsg(soldoutList) {
  let data = [];
  try {
    data = JSON.parse(soldoutList);
    if (!Array.isArray(data)) data = [];
  } catch (err) {
    console.error('soldoutList の解析に失敗しました:', err);
    data = [];
  }

  // soldOutData を Map に変換（全局変数として使用する場合）
  soldOutData = new Map(
    data.map(item => [String(item.item_code), item.sold_out_flag])
  );

  // カテゴリ情報を取得して refreshPage を呼び出す
  const cats = await ensureCategories();
  refreshPage(cats);
}


<!-- 現在画面表示を更新する -->
async function refreshPage(cats) {
  try {
    const lSelect = document.getElementById('lSelect');
    const mSelect = document.getElementById('mSelect');
    const sSelect = document.getElementById('sSelect');

    // 現在の選択を保存
    const currentL = lSelect.value;
    const currentM = mSelect.value;
    const currentS = sSelect.value;

    // L（大カテゴリ）のドロップダウンを再構築
    const lOptions = (cats.tree || []).map(l => ({ value: l.id, label: l.label }));
    populateSelect(lSelect, lOptions);

    // L の選択を復元
    if (lOptions.some(o => o.value === currentL)) {
      lSelect.value = currentL;
    } else {
      lSelect.value = lOptions[0]?.value || '';
    }

    // M/S（中カテゴリ/小カテゴリ）下位ドロップダウンを更新
    handleSelectionChange(cats, true);

    // M/S の選択を復元
    const lNode = (cats.tree || []).find(l => l.id === lSelect.value);
    const mNode = (lNode?.children || []).find(m => m.id === currentM);
    if (mNode) {
      mSelect.value = currentM;
      populateSelect(sSelect, (mNode.pages || []).map(p => ({ value: p.id, label: p.label })));
    }
    if ((mNode?.pages || []).some(p => p.id === currentS)) {
      sSelect.value = currentS;
    } else {
      sSelect.value = (mNode?.pages || [])[0]?.id || '';
    }
    
    run();

  } catch (err) {
    console.error('ページ更新に失敗しました', err);
  }
}

<!-- 品切れ状態を取得する -->
function getSoldOutState(gi, soldout_settings) {
  if (!soldOutData || !gi || !gi.product_code) return 0;
  const soldOutFlag = soldOutData.get(String(gi.product_code));
  return soldout_settings?.sort_soldout_state?.[soldOutFlag] || 0;
}

<!-- 品切れ対応の画像パスを取得する -->
function getSoldOutImage(gi, soldout_settings) {
  let imageSrc = '';

  if (!soldOutData) return imageSrc;

  const soldOutFlag = soldOutData.get(gi.product_code);
    
  if (soldOutFlag && soldOutFlag !== 0) {
    if (gi.layout_type === 'recommended' && gi.osusume) {
      imageSrc = soldout_settings.frm_btn_images[soldOutFlag];
    } else {
      imageSrc = soldout_settings.cell_btn_images[soldOutFlag];
    }
  }
    
  if (imageSrc && !imageSrc.startsWith('./') && !imageSrc.startsWith('/') && !imageSrc.startsWith('http') && !imageSrc.startsWith('data:')) {
      imageSrc = `./assets/soldout/${imageSrc}`;
  }

  return imageSrc;
}

(async () => {
  try {
    const cats = await ensureCategories();
    const lSelect = document.getElementById('lSelect');
    const mSelect = document.getElementById('mSelect');
    const sSelect = document.getElementById('sSelect');

    const lOptions = (cats.tree || []).map(l => ({ value: l.id, label: l.label }));
    populateSelect(lSelect, lOptions);

    handleSelectionChange(cats, true);

    lSelect.addEventListener('change', () => handleSelectionChange(cats));
    mSelect.addEventListener('change', () => {
      const lNode = (cats.tree || []).find(l => l.id === lSelect.value);
      const mNode = (lNode?.children || []).find(m => m.id === mSelect.value);
      if (mNode) {
        populateSelect(sSelect, (mNode.pages || []).map(p => ({ value: p.id, label: p.label })));
      } else {
        populateSelect(sSelect, []);
      }
      run();
    });
    sSelect.addEventListener('change', run);

    if (getSelectedSmallId()) {
      run();
    }
  } catch (err) {
    console.error('Failed to init selectors', err);
  }
})();
</script>
</body>
</html>
"""


def _build_css(show_dev_ui: bool) -> str:
    parts = [
        _CSS_COMMON_TOP,
        _CSS_TOOLBAR_VISIBLE if show_dev_ui else _CSS_TOOLBAR_HIDDEN,
        _CSS_TOOLBAR_COMMON,
        _CSS_STAGE,
        _CSS_LOG_VISIBLE if show_dev_ui else _CSS_LOG_HIDDEN,
        _CSS_CANVAS,
        _CSS_GRID,
        _CSS_TILE,
        _CSS_TILE_INNER,
        _CSS_TILE_IMAGE,
        _CSS_SOLDOUT_LAYER,
        _CSS_SOLDOUT,
        _CSS_CELL_LAYER,
        _CSS_CELL_BOX,
        _CSS_TILE_META,
    ]
    return "\n\n".join(parts) + "\n"


def build_index_html(show_dev_ui: bool = False) -> str:
    css = _build_css(show_dev_ui)
    return "".join([_HTML_BEFORE_STYLE, css, _HTML_AFTER_STYLE])


def write_index_html(web_dir: str, show_dev_ui: bool = False) -> None:
    p = Path(web_dir) / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(build_index_html(show_dev_ui), encoding="utf-8")
