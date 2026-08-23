'use strict';

const SHIPMENT_CARRIERS = [
  { id: 'msc', name: 'MSC', color: '#173b8f', url: 'https://www.msc.com/en/track-a-shipment', prefixes: ['MSC', 'MED'] },
  { id: 'maersk', name: 'Maersk', color: '#0073ab', url: 'https://www.maersk.com/tracking/', prefixes: ['MAE', 'MSK', 'MRK'] },
  { id: 'cma', name: 'CMA CGM', color: '#d62838', url: 'https://www.cma-cgm.com/ebusiness/tracking', prefixes: ['CMA', 'APL'] },
  { id: 'hapag', name: 'Hapag-Lloyd', color: '#e86f00', url: 'https://www.hapag-lloyd.com/en/online-business/track/track-by-container-solution.html', prefixes: ['HLX', 'HLB'] },
  { id: 'one', name: 'Ocean Network Express (ONE)', color: '#d71970', url: 'https://ecomm.one-line.com/one-ecom/manage-shipment/cargo-tracking', prefixes: ['KKF', 'KOC', 'MOL', 'NYK'] },
  { id: 'evergreen', name: 'Evergreen', color: '#13733b', url: 'https://ct.shipmentlink.com/servlet/TDB1_CargoTracking.do', prefixes: ['EIS', 'EGH', 'EMC', 'EVG'] },
  { id: 'zim', name: 'ZIM', color: '#0088b8', url: 'https://www.zim.com/tools/track-a-shipment', prefixes: ['ZIM', 'ZCS'] },
  { id: 'cosco', name: 'COSCO Shipping', color: '#c61f2b', url: 'https://elines.coscoshipping.com/ebusiness/cargoTracking', prefixes: ['CCC', 'CSN', 'COS'] },
  { id: 'pil', name: 'Pacific International Lines (PIL)', color: '#254b87', url: 'https://www.pilship.com/en-cargo-tracking-pil/151.html', prefixes: ['PIL', 'PCI'] },
  { id: 'oocl', name: 'OOCL', color: '#b61f2f', url: 'https://www.oocl.com/eng/ourservices/eservices/cargotracking/Pages/cargotracking.aspx', prefixes: ['OOL', 'OCL'] },
  { id: 'yangming', name: 'Yang Ming', color: '#315596', url: 'https://www.yangming.com/e-service/Track_Trace/track_trace_cargo_tracking.aspx', prefixes: ['YML', 'YMM', 'YMT'] }
];

const ISO_LETTER_VALUES = {
  A: 10, B: 12, C: 13, D: 14, E: 15, F: 16, G: 17, H: 18, I: 19, J: 20, K: 21, L: 23, M: 24,
  N: 25, O: 26, P: 27, Q: 28, R: 29, S: 30, T: 31, U: 32, V: 34, W: 35, X: 36, Y: 37, Z: 38
};

let referenceType = 'container';
let preparedReference = '';

function shipmentById(id) { return document.getElementById(id); }

function normaliseReference(value) {
  return value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 24);
}

function expectedContainerCheckDigit(firstTen) {
  const sum = firstTen.split('').reduce((total, character, index) => {
    const value = /\d/.test(character) ? Number(character) : ISO_LETTER_VALUES[character];
    return total + value * (2 ** index);
  }, 0);
  return (sum % 11) % 10;
}

function validateContainer(reference) {
  if (!/^[A-Z]{3}[UJZ]\d{7}$/.test(reference)) {
    return { valid: false, message: 'Use three owner letters, U/J/Z, six serial digits and one check digit.' };
  }
  const expected = expectedContainerCheckDigit(reference.slice(0, 10));
  const actual = Number(reference[10]);
  if (expected !== actual) {
    return { valid: false, message: `Check digit does not match. Recheck the number on the container or transport document (expected ${expected}).` };
  }
  return { valid: true, message: 'ISO 6346 structure and check digit are valid.' };
}

function suggestedCarrierFor(reference) {
  if (referenceType !== 'container') return null;
  const ownerPrefix = reference.slice(0, 3);
  return SHIPMENT_CARRIERS.find(carrier => carrier.prefixes.includes(ownerPrefix)) || null;
}

function renderContainerAnatomy(reference) {
  const padded = (reference + '___________').slice(0, 11);
  shipmentById('owner-code').textContent = padded.slice(0, 3).replaceAll('_', '-');
  shipmentById('equipment-code').textContent = padded[3].replace('_', '-');
  shipmentById('serial-code').textContent = padded.slice(4, 10).replaceAll('_', '-');
  shipmentById('check-code').textContent = padded[10].replace('_', '-');
}

function clearValidation() {
  const input = shipmentById('shipment-reference');
  input.removeAttribute('aria-invalid');
  shipmentById('reference-error').textContent = '';
  shipmentById('validation-mark').innerHTML = '';
  shipmentById('validation-mark').className = '';
}

function validateReference(showRequired) {
  const input = shipmentById('shipment-reference');
  const reference = normaliseReference(input.value);
  input.value = reference;
  if (referenceType === 'container') renderContainerAnatomy(reference);
  clearValidation();

  if (!reference) {
    if (showRequired) {
      input.setAttribute('aria-invalid', 'true');
      shipmentById('reference-error').textContent = 'Enter a shipment reference.';
    }
    return false;
  }

  const outcome = referenceType === 'container'
    ? validateContainer(reference)
    : { valid: reference.length >= 5, message: reference.length >= 5 ? 'Reference is ready.' : 'Enter at least five letters or numbers.' };
  input.setAttribute('aria-invalid', String(!outcome.valid));
  shipmentById('reference-error').textContent = outcome.valid ? '' : outcome.message;
  shipmentById('validation-mark').className = outcome.valid ? 'valid' : 'invalid';
  shipmentById('validation-mark').innerHTML = `<i class="fa-solid fa-${outcome.valid ? 'check' : 'xmark'}"></i>`;
  return outcome.valid;
}

function switchReferenceType(type) {
  referenceType = type;
  document.querySelectorAll('.reference-tab').forEach(button => {
    const active = button.dataset.type === type;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  const settings = {
    container: ['Container number', 'Example: MSCU1234566', 'Four letters followed by seven digits. Spaces and hyphens are accepted.'],
    bl: ['Bill of Lading number', 'Enter the BL number exactly as issued', 'BL formats differ by carrier. Select the shipping line shown on the document.'],
    booking: ['Carrier booking number', 'Enter the carrier booking reference', 'Booking formats differ by carrier. Select the shipping line shown on the confirmation.']
  }[type];
  shipmentById('reference-label').textContent = settings[0];
  shipmentById('shipment-reference').placeholder = settings[1];
  shipmentById('reference-help').textContent = settings[2];
  shipmentById('container-anatomy').hidden = type !== 'container';
  shipmentById('shipment-reference').value = '';
  renderContainerAnatomy('');
  clearValidation();
  shipmentById('result-ready').hidden = true;
  shipmentById('result-empty').hidden = false;
}

function prepareTracking(event) {
  event.preventDefault();
  const validReference = validateReference(true);
  const carrierId = shipmentById('carrier-select').value;
  const carrier = SHIPMENT_CARRIERS.find(item => item.id === carrierId);
  if (!validReference) return;
  if (!carrier) {
    shipmentById('carrier-select').focus();
    shipmentById('carrier-select').setAttribute('aria-invalid', 'true');
    shipmentById('carrier-error').textContent = 'Select the shipping carrier shown on your BL or booking confirmation.';
    return;
  }
  shipmentById('carrier-select').removeAttribute('aria-invalid');
  shipmentById('carrier-error').textContent = '';
  preparedReference = normaliseReference(shipmentById('shipment-reference').value);
  const suggested = suggestedCarrierFor(preparedReference);

  shipmentById('result-reference').textContent = preparedReference;
  shipmentById('result-type').textContent = referenceType === 'bl' ? 'Bill of Lading' : referenceType === 'booking' ? 'Booking reference' : 'ISO container number';
  shipmentById('result-carrier').textContent = carrier.name;
  shipmentById('result-status-text').textContent = referenceType === 'container' ? 'Container number validated' : 'Reference prepared';
  shipmentById('official-link-title').textContent = `Open ${carrier.name} Tracking`;
  shipmentById('official-track-link').href = carrier.url;

  const ownerHint = shipmentById('owner-hint');
  if (suggested) {
    ownerHint.hidden = false;
    ownerHint.querySelector('span').textContent = `The ${preparedReference.slice(0, 3)} owner prefix is associated with ${suggested.name}. This is an equipment-owner hint, not proof of the carrying line.`;
  } else {
    ownerHint.hidden = true;
  }
  shipmentById('result-empty').hidden = true;
  shipmentById('result-ready').hidden = false;
  shipmentById('copy-status').textContent = '';
  shipmentById('result-ready').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function copyReference() {
  if (!preparedReference) return;
  try {
    await navigator.clipboard.writeText(preparedReference);
    shipmentById('copy-status').textContent = 'Reference copied';
  } catch (_) {
    shipmentById('copy-status').textContent = `Reference: ${preparedReference}`;
  }
}

function populateCarriers() {
  const select = shipmentById('carrier-select');
  SHIPMENT_CARRIERS.forEach(carrier => {
    const option = document.createElement('option');
    option.value = carrier.id;
    option.textContent = carrier.name;
    select.appendChild(option);
  });
  shipmentById('carrier-grid').innerHTML = SHIPMENT_CARRIERS.map(carrier => `
    <a class="carrier-portal" href="${carrier.url}" target="_blank" rel="noopener noreferrer">
      <span class="carrier-mark" style="--carrier-color:${carrier.color}">${carrier.name.split(' ').map(word => word[0]).join('').slice(0, 3)}</span>
      <span><strong>${carrier.name}</strong><small>Official tracking portal</small></span>
      <i class="fa-solid fa-arrow-up-right-from-square"></i>
    </a>`).join('');
}

document.addEventListener('DOMContentLoaded', () => {
  populateCarriers();
  renderContainerAnatomy('');
  document.querySelectorAll('.reference-tab').forEach(button => button.addEventListener('click', () => switchReferenceType(button.dataset.type)));
  shipmentById('shipment-reference').addEventListener('input', () => validateReference(false));
  shipmentById('carrier-select').addEventListener('change', event => {
    event.target.removeAttribute('aria-invalid');
    shipmentById('carrier-error').textContent = '';
  });
  shipmentById('shipment-form').addEventListener('submit', prepareTracking);
  shipmentById('copy-reference').addEventListener('click', copyReference);
});
