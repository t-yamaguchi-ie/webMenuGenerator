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
  }
  .toolbar label {
    font-size: 14px;
    color: #555;
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .toolbar input {
    padding: 4px 8px;
    font-size: 14px;
    width: 140px;
  }
  .toolbar button {
    padding: 6px 16px;
    font-size: 14px;
    cursor: pointer;
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
    box-shadow: none;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .tile img {
    width: 100%;
    flex: 1 1 auto;
    object-fit: cover;
    background: #ececec;
  }
  .tile .meta {
    padding: 8px 10px 10px;
    font-size: 13px;
    line-height: 1.4;
    background: rgba(255,255,255,0.65);
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
  <label>Small ID
    <input id="pageId" type="text" value="sm-0201013" />
  </label>
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
const cache = { products: null };

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

function renderTiles(gridEl, items, productMap, layout) {
  gridEl.innerHTML = '';
  for (const gi of items) {
    const product = productMap.get(gi.product_code) || {};
    const tile = document.createElement('div');
    tile.className = 'tile';

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

    const price = product.price != null ? `¥${product.price}` : '-';
    tile.innerHTML = `
      <img src="${product.image || ''}" alt="">
      <div class="meta">
        <div>${product.name || gi.product_code}</div>
        <span class="price">${price}</span>
      </div>`;

    gridEl.appendChild(tile);
  }
}

async function run() {
  const canvas = document.getElementById('canvas');
  const log = document.getElementById('log');
  const grid = document.getElementById('grid');
  const input = document.getElementById('pageId');
  const sid = (input.value || '').trim();
  if (!sid) {
    log.textContent = 'small ID が未入力です';
    grid.innerHTML = '';
    canvas.style.backgroundImage = 'none';
    return;
  }

  try {
    const productMap = await ensureProducts();
    const page = await fetchJson(`./small/${sid}/page-1.json`);

    applyBackground(canvas, page);
    const layout = layoutCanvas(page.grid_items || []);
    renderTiles(grid, page.grid_items || [], productMap, layout);

    log.textContent = `Loaded ${sid} (items: ${page.grid_items?.length || 0}, layout: ${page.layout_type})`;
  } catch (err) {
    console.error(err);
    log.textContent = 'Error: ' + err.message;
    grid.innerHTML = '';
    canvas.style.backgroundImage = 'none';
  }
}

document.getElementById('btn').addEventListener('click', run);
</script>
</body>
</html>"""

def write_index_html(web_dir: str) -> None:
    p = Path(web_dir) / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_HTML, encoding="utf-8")
