/* ==========================================================================
   COOKup Tracker - Modern Application Logic & Chart.js Analytics
   Supports Live API Backend & Static Fallback (GitHub Pages)
   ========================================================================== */

const API_BASE = '/api';

let isStaticMode = false;
let staticDishes = null;
let staticHistory = null;

// State Management
const state = {
  currentCategory: null,
  currentCategoryName: 'All Categories',
  searchQuery: '',
  maxPrice: 5000,
  sortBy: 'name_asc',
  priceDropsOnly: false,
  page: 1,
  totalPages: 1,
  limit: 24,
  categories: [],
  chartInstance: null
};

// DOM Elements
const elements = {
  statTotalDishes: document.getElementById('stat-total-dishes'),
  statCategories: document.getElementById('stat-categories'),
  statPriceDrops: document.getElementById('stat-price-drops'),
  statAvgPrice: document.getElementById('stat-avg-price'),
  catTree: document.getElementById('category-tree-container'),
  catSearch: document.getElementById('cat-search-input'),
  catBadge: document.getElementById('cat-count-badge'),
  dishSearch: document.getElementById('dish-search-input'),
  btnClearSearch: document.getElementById('btn-clear-search'),
  btnToggleDrops: document.getElementById('btn-toggle-drops'),
  priceRange: document.getElementById('price-range'),
  priceRangeVal: document.getElementById('price-range-val'),
  sortSelect: document.getElementById('sort-select'),
  catTitle: document.getElementById('current-category-title'),
  resultsBadge: document.getElementById('results-count-label'),
  dishesGrid: document.getElementById('dishes-grid-container'),
  btnPrevPage: document.getElementById('btn-prev-page'),
  btnNextPage: document.getElementById('btn-next-page'),
  paginationInfo: document.getElementById('pagination-info'),
  btnTriggerScrape: document.getElementById('btn-trigger-scrape'),
  toastScraper: document.getElementById('toast-scraper'),
  // Modal
  priceModal: document.getElementById('price-modal'),
  btnCloseModal: document.getElementById('btn-close-modal'),
  modalImg: document.getElementById('modal-dish-img'),
  modalCat: document.getElementById('modal-dish-category'),
  modalName: document.getElementById('modal-dish-name'),
  modalBengali: document.getElementById('modal-dish-bengali'),
  modalCook: document.getElementById('modal-dish-cook'),
  modalServing: document.getElementById('modal-dish-serving'),
  modalRating: document.getElementById('modal-dish-rating'),
  modalCurrentPrice: document.getElementById('modal-price-current'),
  modalLowestPrice: document.getElementById('modal-price-lowest'),
  modalHighestPrice: document.getElementById('modal-price-highest'),
  modalAvgPrice: document.getElementById('modal-price-avg'),
  modalLowestBadge: document.getElementById('modal-lowest-badge'),
  priceChartCtx: document.getElementById('priceChart').getContext('2d')
};

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
  await loadStats();
  await loadCategories();
  await loadDishes();

  setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
  // Search
  elements.dishSearch.addEventListener('input', (e) => {
    state.searchQuery = e.target.value.trim();
    elements.btnClearSearch.classList.toggle('hidden', !state.searchQuery);
    state.page = 1;
    loadDishes();
  });

  elements.btnClearSearch.addEventListener('click', () => {
    elements.dishSearch.value = '';
    state.searchQuery = '';
    elements.btnClearSearch.classList.add('hidden');
    state.page = 1;
    loadDishes();
  });

  // Price Slider
  elements.priceRange.addEventListener('input', (e) => {
    state.maxPrice = parseFloat(e.target.value);
    elements.priceRangeVal.textContent = `৳${state.maxPrice}`;
    state.page = 1;
    loadDishes();
  });

  // Price Drops Only
  elements.btnToggleDrops.addEventListener('click', () => {
    state.priceDropsOnly = !state.priceDropsOnly;
    elements.btnToggleDrops.classList.toggle('active', state.priceDropsOnly);
    state.page = 1;
    loadDishes();
  });

  // Sort
  elements.sortSelect.addEventListener('change', (e) => {
    state.sortBy = e.target.value;
    state.page = 1;
    loadDishes();
  });

  // Category Tree Filter
  elements.catSearch.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    const items = elements.catTree.querySelectorAll('.cat-item');
    items.forEach(item => {
      const txt = item.textContent.toLowerCase();
      item.style.display = txt.includes(q) ? 'flex' : 'none';
    });
  });

  // Pagination
  elements.btnPrevPage.addEventListener('click', () => {
    if (state.page > 1) {
      state.page--;
      loadDishes();
    }
  });

  elements.btnNextPage.addEventListener('click', () => {
    if (state.page < state.totalPages) {
      state.page++;
      loadDishes();
    }
  });

  // Trigger Scraper
  elements.btnTriggerScrape.addEventListener('click', triggerRealtimeScrape);

  // Close Modal
  elements.btnCloseModal.addEventListener('click', closeModal);
  elements.priceModal.addEventListener('click', (e) => {
    if (e.target === elements.priceModal) closeModal();
  });
}

function updateStatsUI(data) {
  elements.statTotalDishes.textContent = data.total_dishes.toLocaleString();
  elements.statCategories.textContent = data.total_categories;
  elements.statPriceDrops.textContent = data.price_drops;
  elements.statAvgPrice.textContent = `৳${data.avg_price}`;
}

// Fetch Global Statistics
async function loadStats() {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) throw new Error("API not available");
    const data = await res.json();
    updateStatsUI(data);
  } catch (err) {
    isStaticMode = true;
    try {
      const res = await fetch('data/stats.json');
      const data = await res.json();
      updateStatsUI(data);
    } catch (e) {
      console.error("Failed to load static stats:", e);
    }
  }
}

// Fetch & Render Category Tree
async function loadCategories() {
  try {
    const res = isStaticMode ? await fetch('data/categories.json') : await fetch(`${API_BASE}/categories`);
    if (!res.ok) throw new Error("API not available");
    state.categories = await res.json();
  } catch (err) {
    isStaticMode = true;
    try {
      const res = await fetch('data/categories.json');
      state.categories = await res.json();
    } catch (e) {
      console.error("Failed to load categories:", e);
      state.categories = [];
    }
  }
  elements.catBadge.textContent = state.categories.length;
  renderCategoryTree();
}

function renderCategoryTree() {
  elements.catTree.innerHTML = '';

  // "All Categories" option
  const allItem = document.createElement('div');
  allItem.className = `cat-item ${state.currentCategory === null ? 'active' : ''}`;
  allItem.innerHTML = `<span>All Categories</span><span class="cat-count">All</span>`;
  allItem.addEventListener('click', () => selectCategory(null, 'All Categories'));
  elements.catTree.appendChild(allItem);

  // Filter categories with items first
  const activeCats = state.categories.filter(c => c.dish_count > 0);

  activeCats.forEach(cat => {
    const item = document.createElement('div');
    item.className = `cat-item ${state.currentCategory === cat.id ? 'active' : ''}`;
    item.innerHTML = `<span>${cat.name}</span><span class="cat-count">${cat.dish_count}</span>`;
    item.addEventListener('click', () => selectCategory(cat.id, cat.name));
    elements.catTree.appendChild(item);
  });
}

function selectCategory(id, name) {
  state.currentCategory = id;
  state.currentCategoryName = name;
  state.searchQuery = '';
  elements.dishSearch.value = '';
  elements.btnClearSearch.classList.add('hidden');
  state.page = 1;

  elements.catTitle.textContent = name;
  renderCategoryTree();
  loadDishes();
}

// Fetch & Render Dishes Grid
async function loadDishes() {
  elements.dishesGrid.innerHTML = `<div class="loading-skeleton">Loading items...</div>`;

  if (isStaticMode) {
    try {
      if (!staticDishes) {
        const res = await fetch('data/dishes.json');
        staticDishes = await res.json();
      }

      let filtered = staticDishes.filter(d => {
        if (state.currentCategory && d.category_id !== state.currentCategory) {
          const isSub = state.categories.some(c => c.id === d.category_id && c.parent_ids && c.parent_ids.includes(state.currentCategory));
          if (!isSub) return false;
        }
        if (state.searchQuery) {
          const q = state.searchQuery.toLowerCase();
          const m1 = d.name && d.name.toLowerCase().includes(q);
          const m2 = d.bengali_name && d.bengali_name.toLowerCase().includes(q);
          const m3 = d.cook_name && d.cook_name.toLowerCase().includes(q);
          if (!m1 && !m2 && !m3) return false;
        }
        if (d.current_price > state.maxPrice) return false;
        if (state.priceDropsOnly && (!d.previous_price || d.current_price >= d.previous_price)) return false;
        return true;
      });

      if (state.sortBy === 'price_asc') filtered.sort((a, b) => a.current_price - b.current_price);
      else if (state.sortBy === 'price_desc') filtered.sort((a, b) => b.current_price - a.current_price);
      else if (state.sortBy === 'rating_desc') filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
      else if (state.sortBy === 'discount_desc') {
        filtered.sort((a, b) => {
          const da = a.previous_price ? (a.previous_price - a.current_price) / a.previous_price : 0;
          const db = b.previous_price ? (b.previous_price - b.current_price) / b.previous_price : 0;
          return db - da;
        });
      } else {
        filtered.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
      }

      const total = filtered.length;
      state.totalPages = Math.ceil(total / state.limit) || 1;
      const start = (state.page - 1) * state.limit;
      const pageItems = filtered.slice(start, start + state.limit);

      elements.resultsBadge.textContent = `${total.toLocaleString()} items found`;
      elements.paginationInfo.textContent = `Page ${state.page} of ${state.totalPages}`;
      elements.btnPrevPage.disabled = state.page <= 1;
      elements.btnNextPage.disabled = state.page >= state.totalPages;

      renderDishesGrid(pageItems);
      return;
    } catch (e) {
      console.error("Failed loading static dishes:", e);
      elements.dishesGrid.innerHTML = `<div class="error-msg">Failed to load static dataset.</div>`;
      return;
    }
  }

  const params = new URLSearchParams({
    page: state.page,
    limit: state.limit,
    sort: state.sortBy,
    max_price: state.maxPrice,
    price_drops: state.priceDropsOnly
  });

  if (state.currentCategory) params.append('category_id', state.currentCategory);
  if (state.searchQuery) params.append('search', state.searchQuery);

  try {
    const res = await fetch(`${API_BASE}/dishes?${params.toString()}`);
    if (!res.ok) throw new Error("API not ok");
    const data = await res.json();

    state.totalPages = data.total_pages;
    elements.resultsBadge.textContent = `${data.total.toLocaleString()} items found`;
    elements.paginationInfo.textContent = `Page ${state.page} of ${data.total_pages || 1}`;
    elements.btnPrevPage.disabled = state.page <= 1;
    elements.btnNextPage.disabled = state.page >= state.totalPages;

    renderDishesGrid(data.items);
  } catch (err) {
    console.error("Failed to load dishes via API, falling back to static:", err);
    isStaticMode = true;
    loadDishes();
  }
}

function renderDishesGrid(dishes) {
  elements.dishesGrid.innerHTML = '';

  if (!dishes || dishes.length === 0) {
    elements.dishesGrid.innerHTML = `
      <div class="empty-state" style="grid-column: 1/-1; text-align: center; padding: 3rem;">
        <h3>No matching items found</h3>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.5rem;">Try adjusting your price range, search query, or category filter.</p>
      </div>
    `;
    return;
  }

  dishes.forEach(dish => {
    const card = document.createElement('div');
    card.className = 'dish-card';

    const hasDrop = dish.previous_price && dish.current_price < dish.previous_price;
    const dropPct = hasDrop ? Math.round(((dish.previous_price - dish.current_price) / dish.previous_price) * 100) : 0;
    const defaultImg = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80';
    const imgSrc = dish.image_url || defaultImg;

    card.innerHTML = `
      <div class="card-img-wrapper">
        <img src="${imgSrc}" alt="${dish.name}" loading="lazy" onerror="this.onerror=null;this.src='${defaultImg}';" />
        ${hasDrop ? `<span class="price-drop-badge">↓ ${dropPct}% OFF</span>` : ''}
      </div>
      <div class="card-body">
        <div>
          <span class="dish-cat-name">${dish.category_name || 'Cookups Special'}</span>
          <h4 class="dish-title">${dish.name}</h4>
          ${dish.bengali_name ? `<p class="dish-bengali">${dish.bengali_name}</p>` : ''}
        </div>
        
        <div class="dish-cook-info">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          <span>${dish.cook_name}</span>
        </div>

        <div class="card-footer">
          <div class="price-block">
            ${hasDrop ? `<span class="old-price">৳${dish.previous_price}</span>` : ''}
            <span class="current-price">৳${dish.current_price}</span>
          </div>
          <div class="rating-block">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="gold" stroke="gold" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <span>${dish.rating ? dish.rating.toFixed(1) : 'N/A'}</span>
          </div>
        </div>
      </div>
    `;

    card.addEventListener('click', () => openPriceModal(dish.id));
    elements.dishesGrid.appendChild(card);
  });
}

function populateModalUI(d, stats, history) {
  const defaultImg = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80';
  elements.modalImg.onerror = () => { elements.modalImg.src = defaultImg; };
  elements.modalImg.src = (d.image_url && d.image_url.startsWith('http')) ? d.image_url : defaultImg;
  elements.modalCat.textContent = d.category_name || 'Cookups Special';
  elements.modalName.textContent = d.name;
  elements.modalBengali.textContent = d.bengali_name || '';
  elements.modalCook.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> ${d.cook_name}`;
  elements.modalServing.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg> ${d.serving_size} ${d.serving_type}`;
  elements.modalRating.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="gold" stroke="gold" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg> ${d.rating ? d.rating.toFixed(1) : 'N/A'} (${d.rating_count || 0})`;

  elements.modalCurrentPrice.textContent = `৳${d.current_price}`;
  elements.modalLowestPrice.textContent = `৳${stats.lowest_price}`;
  elements.modalHighestPrice.textContent = `৳${stats.highest_price}`;
  elements.modalAvgPrice.textContent = `৳${stats.avg_price}`;

  elements.modalLowestBadge.classList.toggle('hidden', !stats.is_lowest_ever);

  setTimeout(() => {
    renderPriceChart(history);
  }, 100);
}

// Price History Modal (CamelCamelCamel & SteamDB Style)
async function openPriceModal(dishId) {
  elements.priceModal.classList.remove('hidden');

  if (isStaticMode) {
    try {
      if (!staticHistory) {
        const res = await fetch('data/history.json');
        staticHistory = await res.json();
      }
      const d = staticDishes ? staticDishes.find(item => item.id === dishId) : null;
      if (!d) return;
      const history = staticHistory[dishId] || [];
      const prices = history.length > 0 ? history.map(h => h.price) : [d.current_price];
      const lowest_price = Math.min(...prices);
      const highest_price = Math.max(...prices);
      const avg_price = Math.round((prices.reduce((a, b) => a + b, 0) / prices.length) * 100) / 100;
      const is_lowest_ever = d.current_price <= lowest_price;

      populateModalUI(d, { lowest_price, highest_price, avg_price, is_lowest_ever, history_count: history.length }, history);
      return;
    } catch (e) {
      console.error("Failed to load static history:", e);
      return;
    }
  }

  try {
    const res = await fetch(`${API_BASE}/dish/${dishId}`);
    if (!res.ok) throw new Error("API not ok");
    const data = await res.json();
    populateModalUI(data.dish, data.stats, data.price_history);
  } catch (err) {
    console.error("Failed to fetch dish details via API, attempting static fallback:", err);
    isStaticMode = true;
    openPriceModal(dishId);
  }
}

function renderPriceChart(history) {
  const wrapper = document.querySelector('.canvas-wrapper');
  if (!wrapper) return;
  
  if (!history || history.length === 0) {
    wrapper.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding-top: 5rem;">No historical price data available</div>';
    return;
  }

  // Collapse to one point per day (seed + scraper can leave duplicate rows for the same date)
  const latestByDate = new Map();
  for (const h of history) {
    const key = h.date_str || h.timestamp || '';
    if (!key) continue;
    const prev = latestByDate.get(key);
    if (!prev || (h.timestamp || '') >= (prev.timestamp || '')) latestByDate.set(key, h);
  }
  history = Array.from(latestByDate.values()).sort((a, b) => (a.date_str || '').localeCompare(b.date_str || ''));

  if (history.length === 0) {
    wrapper.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding-top: 5rem;">No historical price data available</div>';
    return;
  }

  const prices = history.map(h => h.price);
  const dates = history.map(h => h.date_str ? h.date_str.slice(5) : '');

  const minP = Math.floor(Math.min(...prices) * 0.92);
  const maxP = Math.ceil(Math.max(...prices) * 1.08);
  const range = (maxP - minP) || 1;

  const width = wrapper.clientWidth > 0 ? wrapper.clientWidth : 740;
  const height = 240;
  const padding = { top: 20, right: 35, bottom: 35, left: 55 };

  const graphW = width - padding.left - padding.right;
  const graphH = height - padding.top - padding.bottom;

  const points = prices.map((price, idx) => {
    const x = padding.left + (idx / (prices.length - 1 || 1)) * graphW;
    const y = padding.top + graphH - ((price - minP) / range) * graphH;
    return { x, y, price, date: dates[idx] };
  });

  const pathD = points.reduce((acc, p, i) => i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`, '');
  const areaD = `${pathD} L ${points[points.length - 1].x} ${height - padding.bottom} L ${points[0].x} ${height - padding.bottom} Z`;

  const yTicks = 4;
  let yGridHtml = '';
  for (let i = 0; i <= yTicks; i++) {
    const val = Math.round(minP + (range / yTicks) * i);
    const y = padding.top + graphH - (i / yTicks) * graphH;
    yGridHtml += `
      <line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="rgba(255,255,255,0.07)" stroke-dasharray="3,3" />
      <text x="${padding.left - 10}" y="${y + 4}" fill="#94a3b8" font-size="11" text-anchor="end">৳${val}</text>
    `;
  }

  let xGridHtml = '';
  const step = Math.max(1, Math.floor(points.length / 6));
  for (let i = 0; i < points.length; i += step) {
    const p = points[i];
    xGridHtml += `<text x="${p.x}" y="${height - 10}" fill="#94a3b8" font-size="11" text-anchor="middle">${p.date}</text>`;
  }

  const dotsHtml = points.map(p => `
    <circle class="chart-dot" cx="${p.x}" cy="${p.y}" r="4" fill="#8b5cf6" stroke="#ffffff" stroke-width="1.5">
      <title>${p.date}: ৳${p.price}</title>
    </circle>
  `).join('');

  wrapper.innerHTML = `
    <svg width="100%" height="100%" viewBox="0 0 ${width} ${height}" style="overflow: visible;">
      <defs>
        <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#6366f1" stop-opacity="0.5" />
          <stop offset="100%" stop-color="#6366f1" stop-opacity="0.0" />
        </linearGradient>
      </defs>
      
      <!-- Grid -->
      ${yGridHtml}
      ${xGridHtml}

      <!-- Area & Path -->
      <path d="${areaD}" fill="url(#chartGrad)" />
      <path d="${pathD}" fill="none" stroke="#6366f1" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />

      <!-- Dots -->
      ${dotsHtml}
    </svg>
  `;
}

function closeModal() {
  elements.priceModal.classList.add('hidden');
}

// Trigger Real-Time Scraper
async function triggerRealtimeScrape() {
  if (isStaticMode) {
    alert("Live scraper requires local backend execution. Run 'python server.py' to use live API & background scraping.");
    return;
  }
  elements.btnTriggerScrape.classList.add('spinning');
  elements.btnTriggerScrape.disabled = true;
  elements.toastScraper.classList.remove('hidden');

  try {
    const res = await fetch(`${API_BASE}/scrape`, { method: 'POST' });
    const data = await res.json();

    setTimeout(() => {
      elements.btnTriggerScrape.classList.remove('spinning');
      elements.btnTriggerScrape.disabled = false;
      elements.toastScraper.classList.add('hidden');

      loadStats();
      loadCategories();
      loadDishes();
    }, 6000);
  } catch (err) {
    console.error("Scraper trigger error:", err);
    elements.btnTriggerScrape.classList.remove('spinning');
    elements.btnTriggerScrape.disabled = false;
    elements.toastScraper.classList.add('hidden');
  }
}
