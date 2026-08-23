'use strict';

let transitData;

function transitById(id) { return document.getElementById(id); }

function addDays(dateString, days) {
  const date = new Date(`${dateString}T12:00:00`);
  date.setDate(date.getDate() + days);
  return date;
}

function formatDate(date) {
  return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(date);
}

function localISODate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function validateTransitData(data) {
  if (!data || data.schemaVersion !== 1 || !data.origins || !Array.isArray(data.destinations)) throw new Error('Invalid transit reference data');
  data.destinations.forEach(destination => {
    if (!destination.id || !destination.port || !destination.transit) throw new Error('Invalid destination reference');
    Object.keys(data.origins).forEach(origin => {
      const range = destination.transit[origin];
      if (!Array.isArray(range) || range.length !== 2 || range[0] <= 0 || range[1] < range[0]) throw new Error('Invalid transit range');
    });
  });
  return data;
}

function selectedInputs(originOverride) {
  const originId = originOverride || transitById('origin-port').value;
  const destinationId = transitById('destination-port').value;
  return {
    originId,
    origin: transitData.origins[originId],
    destination: transitData.destinations.find(item => item.id === destinationId),
    departure: transitById('departure-date').value,
    buffer: Number(transitById('contingency-days').value) || 0
  };
}

function calculateTransit(input) {
  const range = input.destination.transit[input.originId];
  return {
    ...input,
    range,
    earliest: addDays(input.departure, range[0]),
    latest: addDays(input.departure, range[1] + input.buffer),
    totalLow: range[0],
    totalHigh: range[1] + input.buffer
  };
}

function renderComparison(destination, departure, buffer, selectedOrigin) {
  transitById('comparison-body').innerHTML = Object.entries(transitData.origins).map(([id, origin]) => {
    const result = calculateTransit({ originId: id, origin, destination, departure, buffer });
    return `<tr${id === selectedOrigin ? ' class="selected"' : ''}><td><strong>${origin.name}</strong><small>${origin.code}</small></td><td>${result.range[0]}-${result.range[1]} days</td><td>${formatDate(result.earliest)} - ${formatDate(result.latest)}</td><td>${destination.pattern}</td></tr>`;
  }).join('');
}

function updateTransit() {
  if (!transitData) return;
  const input = selectedInputs();
  if (!input.destination || !input.departure) return;
  const result = calculateTransit(input);
  transitById('result-origin-code').textContent = input.origin.code;
  transitById('result-destination-code').textContent = input.destination.code;
  transitById('result-route').textContent = `${input.origin.name} to ${input.destination.port}`;
  transitById('result-pattern').textContent = `${input.destination.city}, ${input.destination.country} | ${input.destination.pattern}`;
  transitById('result-dates').textContent = `${formatDate(result.earliest)} - ${formatDate(result.latest)}`;
  transitById('result-window-days').textContent = `${result.totalLow}-${result.totalHigh} calendar days after intended vessel departure`;
  transitById('result-base').textContent = `${result.range[0]}-${result.range[1]} days`;
  transitById('result-buffer').textContent = `${input.buffer} ${input.buffer === 1 ? 'day' : 'days'}`;
  transitById('review-date').textContent = `Data reviewed ${formatDate(new Date(`${transitData.reviewedAt}T12:00:00`))}`;
  transitById('result-warning-text').textContent = input.buffer
    ? `The later date includes ${input.buffer} contingency days. It still does not account for pre-departure cut-off, customs, inland movement or an actual carrier disruption.`
    : 'No contingency has been added. Use this narrow window only for early comparison and confirm the bookable sailing before setting commercial dates.';
  transitById('route-quote-link').href = `contact.html?port=${encodeURIComponent(`${input.destination.port}, ${input.destination.country}`)}#inquiry-form`;
  transitById('transit-placeholder').hidden = true;
  transitById('transit-content').hidden = false;
  renderComparison(input.destination, input.departure, input.buffer, input.originId);
  transitById('copy-status').textContent = '';
}

async function copyTransitPlan() {
  const input = selectedInputs();
  const result = calculateTransit(input);
  const text = [
    'JFT Agro indicative port transit plan',
    `Route: ${input.origin.name} (${input.origin.code}) to ${input.destination.port}, ${input.destination.country} (${input.destination.code})`,
    `Intended vessel departure: ${formatDate(new Date(`${input.departure}T12:00:00`))}`,
    `Base port-to-port band: ${result.range[0]}-${result.range[1]} days`,
    `Planning arrival window: ${formatDate(result.earliest)} - ${formatDate(result.latest)}`,
    `Contingency added to later date: ${input.buffer} days`,
    'Planning reference only; confirm the actual carrier schedule, routing and ETA.'
  ].join('\n');
  try {
    await navigator.clipboard.writeText(text);
    transitById('copy-status').textContent = 'Transit plan copied';
  } catch (_) {
    transitById('copy-status').textContent = 'Copy unavailable in this browser';
  }
}

function populateTransitControls() {
  transitById('origin-port').innerHTML = Object.entries(transitData.origins).map(([id, origin]) => `<option value="${id}">${origin.name} (${origin.code})</option>`).join('');
  const destinationsByRegion = Object.keys(transitData.regions).map(region => {
    const options = transitData.destinations.filter(item => item.region === region).map(item => `<option value="${item.id}">${item.port}, ${item.country} (${item.code})</option>`).join('');
    return `<optgroup label="${transitData.regions[region]}">${options}</optgroup>`;
  }).join('');
  transitById('destination-port').innerHTML = destinationsByRegion;
  transitById('destination-port').value = 'jebel-ali';
  const today = new Date();
  transitById('departure-date').min = localISODate(today);
  transitById('departure-date').value = localISODate(today);
  transitById('schedule-links').innerHTML = transitData.scheduleLinks.map(item => `<a href="${item.url}" target="_blank" rel="noopener noreferrer"><i class="fa-solid fa-arrow-up-right-from-square"></i><span><strong>${item.name}</strong><small>Official schedule search</small></span></a>`).join('');
}

async function initialiseTransitCalculator() {
  try {
    const response = await fetch('data/port-transit-reference-data.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`Reference data returned ${response.status}`);
    transitData = validateTransitData(await response.json());
    populateTransitControls();
    updateTransit();
  } catch (error) {
    console.error('Unable to load transit references:', error);
    transitById('transit-placeholder').innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i><strong>Transit references unavailable</strong><span>Please contact the trade desk for route planning.</span>';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  ['origin-port', 'destination-port', 'departure-date', 'contingency-days'].forEach(id => transitById(id).addEventListener('change', updateTransit));
  transitById('update-transit').addEventListener('click', updateTransit);
  transitById('copy-transit').addEventListener('click', copyTransitPlan);
  initialiseTransitCalculator();
});
