const RATE_FEED_URL = 'data/quote-market-rates.json';
const REFRESH_INTERVAL_MS = 15 * 60 * 1000;
let marketFeed = null;
let lastResult = null;

const byId = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value).replace(/[&<>"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[character]));
}

function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Unknown' : new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Kolkata', timeZoneName: 'short' }).format(date);
}

function validateFeed(feed) {
  if (!feed || feed.schemaVersion !== 1 || feed.currency !== 'USD') throw new Error('Unsupported market-feed format');
  if (!feed.products || !feed.freight || !feed.packing || !feed.assumptions) throw new Error('Incomplete market feed');
  Object.values(feed.products).forEach((product) => {
    if (![product.fob, product.load20, product.load40].every((value) => Number.isFinite(value) && value > 0)) throw new Error('Invalid product benchmark');
  });
  Object.values(feed.freight).forEach((lane) => {
    if (![lane['20ft'], lane['40ft']].every((value) => Number.isFinite(value) && value >= 0)) throw new Error('Invalid freight benchmark');
  });
  return feed;
}

function updateFeedStatus(state, message) {
  const status = byId('rate-status');
  status.className = `rate-indicator ${state}`;
  byId('rate-status-text').textContent = message;
}

function renderFeedMeta() {
  const expired = new Date(marketFeed.validUntil).getTime() < Date.now();
  const unverified = marketFeed.mode !== 'live';
  updateFeedStatus(expired ? 'stale' : (unverified ? '' : 'fresh'), expired ? 'Reference feed expired' : (unverified ? 'Reference benchmark feed' : 'Live market feed'));
  byId('rate-updated').innerHTML = `<strong>Updated:</strong> ${escapeHtml(formatDate(marketFeed.updatedAt))}`;
  byId('rate-validity').innerHTML = `<strong>Valid through:</strong> ${escapeHtml(formatDate(marketFeed.validUntil))}`;
  byId('rate-source').innerHTML = `<strong>Sources:</strong> ${escapeHtml(marketFeed.sources.products)}; ${escapeHtml(marketFeed.sources.freight)}`;
  byId('result-freshness').textContent = expired ? 'Expired reference feed' : (unverified ? 'Reference benchmark' : 'Live feed');
}

async function loadMarketFeed(force = false) {
  const button = byId('rate-refresh');
  button.disabled = true;
  button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Refreshing';
  updateFeedStatus('', 'Loading rate feed');
  try {
    const suffix = force ? `?v=${Date.now()}` : '';
    const response = await fetch(`${RATE_FEED_URL}${suffix}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Rate feed returned ${response.status}`);
    marketFeed = validateFeed(await response.json());
    renderFeedMeta();
    calculate();
  } catch (error) {
    console.error('Unable to load quote market feed:', error);
    updateFeedStatus('stale', 'Rate feed unavailable');
    byId('resultPlaceholder').innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i><strong>Estimate temporarily unavailable</strong><p>Market reference data could not be loaded. Please request a formal quotation.</p>';
  } finally {
    button.disabled = false;
    button.innerHTML = '<i class="fa-solid fa-rotate"></i> Refresh rates';
  }
}

function getInputs() {
  const containers = Math.min(50, Math.max(1, parseInt(byId('calc-containers').value, 10) || 1));
  byId('calc-containers').value = containers;
  const portKey = byId('calc-port').value;
  let incoterm = byId('calc-inco').value;
  if (portKey === 'ex_mill' && incoterm !== 'ExMill') {
    incoterm = 'ExMill';
    byId('calc-inco').value = 'ExMill';
  }
  return {
    productKey: byId('calc-product').value,
    portKey,
    containerSize: byId('calc-container-size').value,
    packingKey: byId('calc-packing').value,
    incoterm,
    containers,
    useOverride: byId('use-live-override').checked,
    productOverride: parseFloat(byId('override-product-rate').value),
    freightOverride: parseFloat(byId('override-freight-rate').value)
  };
}

function calculate() {
  if (!marketFeed) return;
  const input = getInputs();
  const product = marketFeed.products[input.productKey];
  const lane = marketFeed.freight[input.portKey];
  const packing = marketFeed.packing[input.packingKey];
  if (!product || !lane || !packing) return;

  const loadKey = input.containerSize === '40ft' ? 'load40' : 'load20';
  const mtPerContainer = product[loadKey];
  const quantity = mtPerContainer * input.containers;
  const productRate = input.useOverride && Number.isFinite(input.productOverride) && input.productOverride > 0 ? input.productOverride : product.fob;
  const freightRate = input.portKey === 'ex_mill' ? 0 : (input.useOverride && Number.isFinite(input.freightOverride) && input.freightOverride >= 0 ? input.freightOverride : lane[input.containerSize]);
  const packingPremium = packing.premiumPerMt;
  const fob = productRate + packingPremium;
  const freightPerMt = freightRate / mtPerContainer;
  const cfr = fob + freightPerMt;
  const insurance = input.portKey === 'ex_mill' ? 0 : cfr * (marketFeed.assumptions.insuranceCoveragePct / 100) * (marketFeed.assumptions.insurancePct / 100);
  const cif = cfr + insurance;
  const exMill = fob * (1 - marketFeed.assumptions.exMillDiscountPct / 100);
  const values = { ExMill: exMill, FOB: fob, CFR: cfr, CIF: cif };
  const selected = values[input.incoterm];
  const productVariation = product.rangePct / 100;
  const freightVariationPerMt = (freightPerMt * (lane.rangePct / 100));
  const low = Math.max(0, (selected - productRate * productVariation - (['CFR', 'CIF'].includes(input.incoterm) ? freightVariationPerMt : 0)));
  const high = selected + productRate * productVariation + (['CFR', 'CIF'].includes(input.incoterm) ? freightVariationPerMt : 0);
  const bags = Math.floor(mtPerContainer * 1000 / packing.bagKg);

  byId('calc-qty').value = quantity.toFixed(1);
  lastResult = { input, product, lane, packing, quantity, mtPerContainer, productRate, freightRate, freightPerMt, packingPremium, insurance, values, selected, low, high, bags, totalLow: low * quantity, totalHigh: high * quantity };
  renderResults(lastResult);
}

function renderResults(result) {
  byId('resultPlaceholder').style.display = 'none';
  byId('resultsContent').classList.add('show');
  byId('mainPriceLabel').textContent = `${result.input.incoterm} REFERENCE RANGE`;
  byId('mainPriceRange').textContent = `$${result.low.toFixed(0)} - $${result.high.toFixed(0)}`;
  byId('mainPriceUnit').textContent = `per metric ton | Total range: $${result.totalLow.toLocaleString('en-US', { maximumFractionDigits: 0 })} - $${result.totalHigh.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;

  byId('incoTabs').innerHTML = ['ExMill', 'FOB', 'CFR', 'CIF'].map((term) => `<button type="button" class="inco-tab ${result.input.incoterm === term ? 'active' : ''}" data-incoterm="${term}">${term}<br><small>$${result.values[term].toFixed(0)}</small></button>`).join('');
  byId('incoTabs').querySelectorAll('button').forEach((button) => button.addEventListener('click', () => {
    byId('calc-inco').value = button.dataset.incoterm;
    calculate();
  }));

  const rows = [
    ['fa-seedling', 'Product benchmark', `$${result.productRate.toFixed(0)} /MT`],
    ['fa-box', result.packing.name, result.packingPremium === 0 ? 'Included' : `${result.packingPremium > 0 ? '+' : ''}$${result.packingPremium.toFixed(0)} /MT`],
    ['fa-ship', `${result.input.containerSize} freight benchmark`, result.input.portKey === 'ex_mill' ? 'Excluded' : `$${result.freightRate.toFixed(0)} /container`],
    ['fa-route', 'Freight allocation', result.input.portKey === 'ex_mill' ? 'Excluded' : `$${result.freightPerMt.toFixed(0)} /MT`],
    ['fa-shield-halved', `Insurance allowance (${marketFeed.assumptions.insurancePct}% x ${marketFeed.assumptions.insuranceCoveragePct}%)`, result.input.incoterm === 'CIF' ? `$${result.insurance.toFixed(1)} /MT` : 'Excluded']
  ];
  byId('breakdownRows').innerHTML = rows.map(([icon, name, value]) => `<div class="breakdown-row"><span><i class="fa-solid ${icon}"></i>${escapeHtml(name)}</span><strong>${escapeHtml(value)}</strong></div>`).join('') + `<div class="breakdown-row total"><span><strong>Midpoint ${escapeHtml(result.input.incoterm)} reference</strong></span><span>$${result.selected.toFixed(0)} /MT</span></div>`;
  byId('resultMeta').innerHTML = `<strong>Product:</strong> ${escapeHtml(result.product.name)}<br><strong>Destination:</strong> ${escapeHtml(result.lane.name)}<br><strong>Estimated load:</strong> ${result.mtPerContainer.toFixed(1)} MT per ${escapeHtml(result.input.containerSize)} container<br><strong>Quantity:</strong> ${result.quantity.toFixed(1)} MT across ${result.input.containers} container${result.input.containers === 1 ? '' : 's'}<br><strong>Approximate bags:</strong> ${result.bags.toLocaleString('en-US')} per container<br><strong>Origin reference:</strong> ${escapeHtml(marketFeed.assumptions.originPorts)}${result.input.useOverride ? '<br><strong>Rate mode:</strong> Buyer-entered live override' : ''}`;

  const message = encodeURIComponent(`Hi JFT Agro, please confirm a formal quote for:\nProduct: ${result.product.name}\nQuantity: ${result.quantity.toFixed(1)} MT (${result.input.containers} x ${result.input.containerSize})\nDestination: ${result.lane.name}\nIncoterm: ${result.input.incoterm}\nPacking: ${result.packing.name}\nCalculator reference: $${result.low.toFixed(0)}-$${result.high.toFixed(0)}/MT\nI understand this calculator output is non-binding and for reference only.`);
  byId('ctaWA').href = `https://wa.me/918425057274?text=${message}`;
}

function copyQuote() {
  if (!lastResult) return;
  const result = lastResult;
  const text = [
    'JFT AGRO OVERSEAS - REFERENCE ESTIMATE',
    'Not a quotation, offer or Proforma Invoice',
    `Data updated: ${formatDate(marketFeed.updatedAt)}`,
    `Product: ${result.product.name}`,
    `Destination: ${result.lane.name}`,
    `Quantity: ${result.quantity.toFixed(1)} MT (${result.input.containers} x ${result.input.containerSize})`,
    `Packing: ${result.packing.name}`,
    `Incoterm: ${result.input.incoterm}`,
    `Reference range: $${result.low.toFixed(0)}-$${result.high.toFixed(0)}/MT`,
    `Estimated total range: $${result.totalLow.toFixed(0)}-$${result.totalHigh.toFixed(0)}`,
    'Excludes duties, taxes, clearance, storage and unlisted surcharges.',
    'Request a formal PI to confirm product, freight, validity and shipment terms.'
  ].join('\n');
  navigator.clipboard.writeText(text).then(() => {
    byId('copy-confirm').style.display = 'block';
    setTimeout(() => { byId('copy-confirm').style.display = 'none'; }, 2500);
  }).catch(() => window.prompt('Copy this reference estimate:', text));
}

function initialiseCalculator() {
  document.querySelectorAll('#quote-form select, #calc-containers').forEach((field) => field.addEventListener('change', calculate));
  byId('calculate-button').addEventListener('click', calculate);
  byId('rate-refresh').addEventListener('click', () => loadMarketFeed(true));
  byId('copy-quote').addEventListener('click', copyQuote);
  byId('print-quote').addEventListener('click', () => window.print());
  byId('use-live-override').addEventListener('change', (event) => {
    byId('override-fields').classList.toggle('show', event.target.checked);
    calculate();
  });
  ['override-product-rate', 'override-freight-rate'].forEach((id) => byId(id).addEventListener('input', calculate));
  loadMarketFeed();
  window.setInterval(() => loadMarketFeed(true), REFRESH_INTERVAL_MS);
}

document.addEventListener('DOMContentLoaded', initialiseCalculator);
