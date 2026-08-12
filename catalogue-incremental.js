(function () {
  'use strict';
  if (!document.getElementById('product-grid')) return;

  let matches = [];
  let limit = 0;
  let sequence = 0;
  const pageSize = () => window.innerWidth < 600 ? 8 : 12;
  const data = () => window.PRODUCT_DATA || (typeof PRODUCT_DATA !== 'undefined' ? PRODUCT_DATA : []);

  function card(product, visibleIndex) {
    const products = data();
    const globalIndex = products.indexOf(product);
    const id = `specs-incremental-${sequence++}`;
    const specs = product.s.concat([['Load (20ft)', product.l], ['Packing', product.p]])
      .map(row => `<tr><td>${row[0]}</td><td>${row[1]}</td></tr>`).join('');
    const markets = (product.f || []).slice(0, 5).map(value => `<span class="p-market-item">${value}</span>`).join(' ');
    const image = product.u
      ? `<a href="${product.u}" aria-label="View ${product.t} details" style="display:block;height:100%;"><img src="${product.i}" alt="${product.t}" loading="${visibleIndex < 4 ? 'eager' : 'lazy'}" decoding="async" width="290" height="260" style="width:100%;height:100%;object-fit:cover;"><span class="p-cat-badge" style="position:absolute;top:14px;left:14px;background:rgba(26,60,52,.88);color:#fff;padding:5px 12px;border-radius:20px;font-family:var(--font-sub);font-weight:800;font-size:.65rem;text-transform:uppercase;">${product.c}</span></a>`
      : `<img src="${product.i}" alt="${product.t}" loading="lazy" decoding="async" width="290" height="260">`;
    const hs = (product.s.find(row => row[0] === 'HS Code') || ['', 'Not specified'])[1];
    return `<div class="p-item" style="animation:dropIn .4s ease forwards;opacity:0;transform:translateY(14px);">
      <div class="p-img-box" style="position:relative;overflow:hidden;">${image}</div>
      <div class="p-content"><div class="p-cat">${product.c.toUpperCase()}</div>
        <h3 class="p-title">${product.u ? `<a href="${product.u}" style="color:inherit;text-decoration:none;">${product.t}</a>` : product.t}</h3>
        <div class="p-specs-wrapper"><div class="p-specs-scrollable" id="${id}" tabindex="0"><table class="p-table-shared">${specs}</table></div><div class="p-toggle-overlay"><button type="button" class="p-toggle-btn" onclick="toggleSpecs('${id}',this)" aria-label="Toggle specifications for ${product.t}" aria-expanded="false"><i class="fa-solid fa-chevron-down" aria-hidden="true"></i></button></div></div>
        <div class="p-flags-area"><div class="p-flag-label">Top Importers</div><div class="p-market-list">${markets}</div></div>
        <div class="p-hs-strip"><span class="p-hs-code">HS: ${hs}</span><span class="p-load-pill"><i class="fa-solid fa-ship"></i> ${product.l.split(' in ')[0]}</span></div>
        <div class="p-action" style="display:flex;gap:8px;flex-wrap:wrap;">${product.u ? `<a href="${product.u}" class="btn-jft btn-primary" style="flex:1;padding:11px 8px;font-size:.72rem;text-align:center;">View Details</a>` : ''}<a href="contact.html?product=${encodeURIComponent(product.t)}#inquiry-form" class="btn-jft" style="flex:1;padding:11px 8px;font-size:.72rem;text-align:center;background:rgba(26,60,52,.08);color:var(--jft-navy);border:1px solid rgba(26,60,52,.2);border-radius:8px;">Get Quote</a><button class="p-btn" onclick="openModal(${globalIndex})" aria-label="View full specifications for ${product.t}"><i class="fa-solid fa-table-list"></i></button></div>
      </div></div>`;
  }

  function paint(reset) {
    const grid = document.getElementById('product-grid');
    if (reset) { grid.replaceChildren(); limit = pageSize(); sequence = 0; }
    const rendered = grid.children.length;
    grid.insertAdjacentHTML('beforeend', matches.slice(rendered, limit).map((product, i) => card(product, rendered + i)).join(''));
    const remaining = Math.max(0, matches.length - grid.children.length);
    const more = document.getElementById('catalogue-load-more');
    const label = document.getElementById('catalogue-remaining');
    const empty = document.getElementById('no-results');
    if (more) more.hidden = remaining === 0;
    if (label) label.textContent = remaining ? `(${remaining} remaining)` : '';
    if (empty) empty.style.display = matches.length ? 'none' : 'block';
    const count = document.getElementById('result-num');
    if (count) count.textContent = matches.length;
    grid.style.opacity = '1';
    if (typeof initDragScroll === 'function') initDragScroll();
    if (typeof attachScrollObserver === 'function') attachScrollObserver();
  }

  function setMatches(next) { matches = next; paint(true); }
  window.renderProducts = cat => setMatches(cat === 'all' ? data() : data().filter(product => product.c === cat));
  window.loadMoreProducts = () => { limit += pageSize(); paint(false); };
  window.performSearch = () => {
    const input = document.getElementById('prod-search');
    const query = input.value.trim().toLowerCase();
    const clear = document.getElementById('search-clear-btn');
    if (clear) clear.style.display = query ? 'flex' : 'none';
    setMatches(data().filter(product => !query || [product.t, product.c, product.p, ...(product.k || []), ...(product.f || []), ...product.s.flat()].some(value => String(value).toLowerCase().includes(query))));
  };
  window.filterRice = (type, button) => {
    document.querySelectorAll('.cz-subtab, .sub-cat-btn').forEach(item => { item.classList.remove('active'); item.setAttribute('aria-pressed', 'false'); });
    button.classList.add('active'); button.setAttribute('aria-pressed', 'true');
    setMatches(data().filter(product => {
      if (product.c !== 'rice') return false;
      if (type === 'all') return true;
      const title = product.t.toLowerCase();
      const nonBasmati = /non[\s-]?basmati/.test(title);
      return type === 'basmati' ? title.includes('basmati') && !nonBasmati : !title.includes('basmati') || nonBasmati;
    }));
  };

  window.addEventListener('load', () => window.renderProducts('all'), { once: true });
})();
