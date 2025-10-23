from pathlib import Path

_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Menu SPA (PoC)</title>
<style>
  :root { color-scheme: light dark; }
  body {
    margin: 0;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    background: #f6f6f6;
  }
  .toolbar {
    max-width: 1000px;
    margin: 24px auto 0;
    display: flex;
    gap: 12px;
    align-items: center;
    padding: 0 16px;
    flex-wrap: wrap;
  }
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
  .stage {
    width: 1000px;
    margin: 16px auto 48px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  #log {
    font-size: 14px;
    color: #333;
    padding: 0 4px;
  }
  .canvas {
    position: relative;
    width: 1000px;
    height: 533px;
    border: 1px solid #d0d0d0;
    border-radius: 12px;
    overflow: hidden;
    background: #f2f2f2 center/cover no-repeat;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  }
  .grid {
    position: relative;
    width: 100%;
    height: 100%;
  }
  .tile {
    position: absolute;
    box-sizing: border-box;
    border-radius: 10px;
    background: transparent;
    border: none;
    overflow: hidden;
  }
  .tile-inner {
    position: relative;
    width: 100%;
    height: 100%;
  }
  .tile-inner img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    background: #ececec;
  }
  .cell-layer {
    position: absolute;
    inset: 0;
  }
  .cell-box {
    position: absolute;
    border: 1px solid rgba(0, 120, 255, 0.5);
    background: rgba(0, 120, 255, 0.15);
    border-radius: 2px;
    box-sizing: border-box;
  }
  .tile .meta {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 6px 10px 8px;
    font-size: 13px;
    line-height: 1.4;
    background: rgba(255,255,255,0.65);
  }
  .tile--recommended .meta {
    background: rgba(0,0,0,0.55);
    color: #fff;
  }
  .tile--recommended .price {
    color: #ffd54f;
  }
  .tile .price {
    display: block;
    margin-top: 4px;
    color: #6c9a00;
    font-weight: 600;
  }
</style>
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
const cache = { products: null, categories: null, cells: new Map() };

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

function renderTiles(gridEl, items, productMap, layout, cellsData, layoutType) {
  gridEl.innerHTML = '';
  for (const gi of items) {
    const product = productMap.get(gi.product_code) || {};
    const tile = document.createElement('div');
    tile.className = 'tile';
    if (layoutType === 'recommended' || gi.osusume) {
      tile.classList.add('tile--recommended');
    }

    const spanX = Math.max(1, gi.span?.[0] ?? 1);
    const spanY = Math.max(1, gi.span?.[1] ?? 1);
    const rawX = gi.cell?.[0] ?? 0;
    const rawY = gi.cell?.[1] ?? 0;

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

    const osusumeMeta = gi.osusume || {};
    let imageSrc = gi.image || product.image || '';
    if (imageSrc) {
      if (!imageSrc.startsWith('./') && !imageSrc.startsWith('/') && !imageSrc.startsWith('http') && !imageSrc.startsWith('data:')) {
        imageSrc = `./assets/${imageSrc}`;
      }
      const img = document.createElement('img');
      img.src = imageSrc;
      img.alt = '';
      inner.appendChild(img);
    }

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

    gridEl.appendChild(tile);
  }
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
    renderTiles(grid, page.grid_items || [], productMap, layout, cellsData, layoutType);

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
</html>"""

def write_index_html(web_dir: str) -> None:
    p = Path(web_dir) / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_HTML, encoding="utf-8")
