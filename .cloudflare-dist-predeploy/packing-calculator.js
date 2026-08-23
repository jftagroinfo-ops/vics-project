const PACKING_DATA_URL = 'data/packing-reference-data.json';
let packingData = null;
let selectedContainer = '20ft';
let lastPackingResult = null;

const packById = (id) => document.getElementById(id);
const packNumber = (id, fallback = 0) => {
  const value = parseFloat(packById(id).value);
  return Number.isFinite(value) ? value : fallback;
};

function formatNumber(value, decimals = 0) {
  return Number(value).toLocaleString('en-IN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

function validatePackingData(data) {
  if (!data || data.schemaVersion !== 1 || !data.containers || !data.products || !data.bagTareKg || !data.defaults) throw new Error('Invalid packing reference data');
  Object.values(data.containers).forEach((container) => {
    if (![container.volumeCbm, container.equipmentPayloadKg, container.planningCargoCapKg].every((value) => Number.isFinite(value) && value > 0)) throw new Error('Invalid container reference');
  });
  return data;
}

function productChanged() {
  const product = packingData.products[packById('product').value];
  if (product) packById('bulk-density').value = product.densityKgCbm;
  calculatePacking();
}

function containerChanged(type) {
  selectedContainer = type;
  document.querySelectorAll('.container-option').forEach((button) => {
    const active = button.dataset.container === type;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  const container = packingData.containers[type];
  packById('cargo-cap').value = container.planningCargoCapKg;
  packById('pallet-count').value = container.palletCount;
  packById('equipment-reference').textContent = `${formatNumber(container.equipmentPayloadKg)} kg maximum payload`;
  calculatePacking();
}

function bagTare(netKg, material) {
  const table = packingData.bagTareKg[material] || packingData.bagTareKg.pp_woven;
  if (table[String(netKg)] !== undefined) return table[String(netKg)];
  const known = Object.keys(table).map(Number).sort((a, b) => a - b);
  const nearest = known.reduce((best, size) => Math.abs(size - netKg) < Math.abs(best - netKg) ? size : best, known[0]);
  return table[String(nearest)] * (netKg / nearest);
}

function readPackingInputs(containerType = selectedContainer, comparison = false) {
  const container = packingData.containers[containerType];
  const productKey = packById('product').value;
  const product = packingData.products[productKey];
  const netBagKg = Math.max(0.1, packNumber('bag-size', 50));
  const material = packById('bag-type').value;
  const measuredGross = packNumber('gross-bag-weight', 0);
  const grossBagKg = measuredGross > netBagKg ? measuredGross : netBagKg + bagTare(netBagKg, material);
  const palletised = packById('palletised').checked;
  const measuredMode = packById('measured-bag').checked;
  const density = Math.max(1, packNumber('bulk-density', product.densityKgCbm));
  const efficiency = Math.min(100, Math.max(40, packNumber('stack-efficiency', packingData.defaultEfficiency[String(netBagKg)] || 88))) / 100;
  const palletCount = palletised ? Math.max(0, Math.round(comparison ? container.palletCount : packNumber('pallet-count', container.palletCount))) : 0;
  const palletTareKg = palletised ? Math.max(0, packNumber('pallet-tare', packingData.defaults.palletTareKg)) : 0;
  const dunnageKg = Math.max(0, packNumber('dunnage-weight', packingData.defaults.dunnageKg));
  const requestedCap = comparison ? container.planningCargoCapKg : Math.max(1, packNumber('cargo-cap', container.planningCargoCapKg));
  const routeCapKg = Math.min(container.equipmentPayloadKg, requestedCap);
  const safetyBuffer = Math.min(15, Math.max(0, packNumber('safety-buffer', packingData.defaults.safetyBufferPct))) / 100;
  let bagVolumeCbm;
  if (measuredMode) {
    const length = Math.max(1, packNumber('bag-length', 80));
    const width = Math.max(1, packNumber('bag-width', 50));
    const height = Math.max(1, packNumber('bag-height', 15));
    bagVolumeCbm = length * width * height / 1_000_000;
  } else {
    bagVolumeCbm = netBagKg / density;
  }
  return { containerType, container, productKey, product, netBagKg, material, grossBagKg, palletised, measuredMode, density, efficiency, palletCount, palletTareKg, dunnageKg, routeCapKg, requestedCap, safetyBuffer, bagVolumeCbm };
}

function computePacking(input) {
  const palletTareTotal = input.palletCount * input.palletTareKg;
  const fixedTareKg = palletTareTotal + input.dunnageKg;
  const availableWithoutBuffer = Math.max(0, input.routeCapKg - fixedTareKg);
  const safeCargoKg = availableWithoutBuffer * (1 - input.safetyBuffer);
  const usableVolumeCbm = input.container.volumeCbm * input.efficiency * (input.palletised ? packingData.defaults.palletVolumeFactor : 1);
  const bagsByWeight = Math.max(0, Math.floor(safeCargoKg / input.grossBagKg));
  const theoreticalByWeight = Math.max(0, Math.floor(availableWithoutBuffer / input.grossBagKg));
  const bagsByVolume = Math.max(0, Math.floor(usableVolumeCbm / input.bagVolumeCbm));
  const bags = Math.min(bagsByWeight, bagsByVolume);
  const theoreticalBags = Math.min(theoreticalByWeight, bagsByVolume);
  const netCargoKg = bags * input.netBagKg;
  const baggedGrossKg = bags * input.grossBagKg;
  const totalPayloadKg = baggedGrossKg + fixedTareKg;
  const volumeUsedCbm = bags * input.bagVolumeCbm;
  const equipmentUtilPct = totalPayloadKg / input.container.equipmentPayloadKg * 100;
  const routeUtilPct = totalPayloadKg / input.routeCapKg * 100;
  const volumeUtilPct = volumeUsedCbm / input.container.volumeCbm * 100;
  const limitedBy = bagsByWeight <= bagsByVolume ? 'Route / weight cap' : 'Volume / stacking';
  const bufferBags = Math.max(0, theoreticalBags - bags);

  let sensitivityLow = bags;
  let sensitivityHigh = bags;
  if (!input.measuredMode) {
    const variation = input.product.rangePct / 100;
    const lowDensityVolume = input.netBagKg / (input.density * (1 - variation));
    const highDensityVolume = input.netBagKg / (input.density * (1 + variation));
    sensitivityLow = Math.min(bagsByWeight, Math.floor(usableVolumeCbm / lowDensityVolume));
    sensitivityHigh = Math.min(bagsByWeight, Math.floor(usableVolumeCbm / highDensityVolume));
  }
  return { ...input, palletTareTotal, fixedTareKg, availableWithoutBuffer, safeCargoKg, usableVolumeCbm, bagsByWeight, theoreticalByWeight, bagsByVolume, bags, theoreticalBags, netCargoKg, baggedGrossKg, totalPayloadKg, volumeUsedCbm, equipmentUtilPct, routeUtilPct, volumeUtilPct, limitedBy, bufferBags, sensitivityLow, sensitivityHigh };
}

function calculatePacking() {
  if (!packingData) return;
  const result = computePacking(readPackingInputs());
  lastPackingResult = result;
  renderPackingResult(result);
  renderContainerComparison();
}

function resultBar(id, percentage) {
  const bar = packById(id);
  bar.style.width = `${Math.min(100, percentage)}%`;
  bar.className = `util-fill${percentage > 95 ? ' danger' : percentage > 85 ? ' warn' : ''}`;
}

function renderPackingResult(result) {
  packById('pack-placeholder').style.display = 'none';
  packById('pack-result-content').classList.add('show');
  packById('result-mode').textContent = result.measuredMode ? 'Measured bag mode' : 'Density benchmark mode';
  packById('result-label').textContent = `${result.container.name} safe planning count`;
  packById('result-bags').textContent = formatNumber(result.bags);
  packById('result-sub').textContent = `${formatNumber(result.netCargoKg / 1000, 2)} MT net product in ${formatNumber(result.netBagKg, result.netBagKg % 1 ? 1 : 0)} kg bags`;
  packById('buffer-text').innerHTML = `<strong>${formatNumber(result.bufferBags)} bags held back</strong> from the theoretical ${formatNumber(result.theoreticalBags)}-bag limit by the ${formatNumber(result.safetyBuffer * 100, 1)}% weight buffer.`;
  packById('stat-gross').textContent = `${formatNumber(result.totalPayloadKg)} kg`;
  packById('stat-route-cap').textContent = `${formatNumber(result.routeCapKg)} kg`;
  packById('stat-equipment').textContent = `${formatNumber(result.container.equipmentPayloadKg)} kg`;
  packById('stat-volume').textContent = `${formatNumber(result.volumeUsedCbm, 1)} / ${formatNumber(result.container.volumeCbm, 1)} CBM`;
  packById('stat-tare').textContent = `${formatNumber(result.fixedTareKg)} kg`;
  packById('stat-limit').textContent = result.limitedBy;
  packById('weight-util-label').textContent = `${formatNumber(result.routeUtilPct, 1)}%`;
  packById('volume-util-label').textContent = `${formatNumber(result.volumeUtilPct, 1)}%`;
  resultBar('weight-util-bar', result.routeUtilPct);
  resultBar('volume-util-bar', result.volumeUtilPct);

  const warning = packById('packing-warning');
  const warnings = [];
  if (result.requestedCap > result.container.equipmentPayloadKg) warnings.push('The entered cargo cap exceeded the equipment reference and was limited to the equipment payload.');
  if (result.routeUtilPct > 97) warnings.push('The plan is close to the route cargo cap. Increase the safety buffer or confirm measured weights before loading.');
  if (result.sensitivityLow !== result.sensitivityHigh) warnings.push(`Density sensitivity suggests approximately ${formatNumber(result.sensitivityLow)}-${formatNumber(result.sensitivityHigh)} bags. Use measured filled-bag dimensions for a firmer plan.`);
  if (result.palletised) warnings.push(`Pallet estimate includes ${result.palletCount} pallets at ${formatNumber(result.palletTareKg, 1)} kg each. Confirm the actual pallet layout and tare.`);
  warning.classList.toggle('show', warnings.length > 0);
  packById('packing-warning-text').textContent = warnings.join(' ');

  const message = encodeURIComponent(`Hi JFT Agro, please confirm a stuffing plan for:\nProduct: ${result.product.name}\nContainer: ${result.container.name}\nPacking: ${result.netBagKg} kg bags\nPlanning result: ${result.bags} bags / ${(result.netCargoKg / 1000).toFixed(2)} MT net\nMode: ${result.measuredMode ? 'Measured bag dimensions' : 'Bulk-density benchmark'}\nRoute cargo cap entered: ${result.routeCapKg} kg\nI understand this is a planning estimate and requires container, route and loading confirmation.`);
  packById('packing-wa').href = `https://wa.me/918425057274?text=${message}`;
}

function renderContainerComparison() {
  const body = packById('comparison-body');
  body.innerHTML = '';
  Object.keys(packingData.containers).forEach((type) => {
    const result = computePacking(readPackingInputs(type, type !== selectedContainer));
    const row = document.createElement('tr');
    if (type === selectedContainer) row.className = 'selected';
    row.innerHTML = `<td><strong>${result.container.name}</strong>${type === selectedContainer ? ' (selected)' : ''}</td><td>${formatNumber(result.bags)}</td><td>${formatNumber(result.netCargoKg / 1000, 2)} MT</td><td>${formatNumber(result.routeCapKg)} kg</td><td>${result.limitedBy}</td>`;
    body.appendChild(row);
  });
}

function copyPackingPlan() {
  if (!lastPackingResult) return;
  const result = lastPackingResult;
  const text = [
    'JFT AGRO OVERSEAS - CONTAINER PACKING PLAN',
    'Planning estimate only; not a verified stuffing instruction or VGM',
    `Product: ${result.product.name}`,
    `Container: ${result.container.name}`,
    `Bag: ${result.netBagKg} kg net / ${result.grossBagKg.toFixed(2)} kg gross`,
    `Safe planning count: ${result.bags} bags`,
    `Net cargo: ${(result.netCargoKg / 1000).toFixed(2)} MT`,
    `Total planned payload: ${result.totalPayloadKg.toFixed(0)} kg`,
    `Route cargo cap: ${result.routeCapKg.toFixed(0)} kg`,
    `Equipment reference payload: ${result.container.equipmentPayloadKg.toFixed(0)} kg`,
    `Fixed tare and dunnage: ${result.fixedTareKg.toFixed(0)} kg`,
    `Limiting factor: ${result.limitedBy}`,
    `Safety buffer: ${(result.safetyBuffer * 100).toFixed(1)}%`,
    'Confirm the assigned container CSC plate, carrier/route limits, actual bag dimensions, pallet layout and verified weights before loading.'
  ].join('\n');
  navigator.clipboard.writeText(text).then(() => {
    packById('copy-status').style.display = 'block';
    setTimeout(() => { packById('copy-status').style.display = 'none'; }, 2500);
  }).catch(() => window.prompt('Copy this packing plan:', text));
}

function bindPackingControls() {
  document.querySelectorAll('.container-option').forEach((button) => button.addEventListener('click', () => containerChanged(button.dataset.container)));
  packById('product').addEventListener('change', productChanged);
  packById('bag-size').addEventListener('change', (event) => {
    const defaultEfficiency = packingData.defaultEfficiency[event.target.value];
    if (defaultEfficiency) packById('stack-efficiency').value = defaultEfficiency;
    calculatePacking();
  });
  document.querySelectorAll('#packing-form select, #packing-form input').forEach((field) => {
    if (!['product', 'bag-size', 'measured-bag', 'palletised'].includes(field.id)) field.addEventListener('input', calculatePacking);
  });
  packById('measured-bag').addEventListener('change', (event) => {
    packById('measured-fields').classList.toggle('show', event.target.checked);
    packById('density-field').style.display = event.target.checked ? 'none' : 'flex';
    calculatePacking();
  });
  packById('palletised').addEventListener('change', (event) => {
    packById('pallet-fields').classList.toggle('show', event.target.checked);
    calculatePacking();
  });
  packById('calculate-packing').addEventListener('click', calculatePacking);
  packById('copy-packing').addEventListener('click', copyPackingPlan);
  packById('print-packing').addEventListener('click', () => window.print());
}

async function initialisePackingCalculator() {
  bindPackingControls();
  try {
    const response = await fetch(PACKING_DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Packing data returned ${response.status}`);
    packingData = validatePackingData(await response.json());
    const product = packingData.products[packById('product').value];
    packById('bulk-density').value = product.densityKgCbm;
    packById('safety-buffer').value = packingData.defaults.safetyBufferPct;
    packById('dunnage-weight').value = packingData.defaults.dunnageKg;
    packById('pallet-tare').value = packingData.defaults.palletTareKg;
    packById('stack-efficiency').value = packingData.defaultEfficiency['50'];
    containerChanged('20ft');
  } catch (error) {
    console.error('Unable to load packing references:', error);
    packById('pack-placeholder').innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i><strong>Calculator temporarily unavailable</strong><p>Reference equipment data could not be loaded. Please request a confirmed stuffing plan.</p>';
  }
}

document.addEventListener('DOMContentLoaded', initialisePackingCalculator);
