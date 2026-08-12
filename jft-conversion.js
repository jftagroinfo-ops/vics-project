(function () {
  'use strict';

  const CONFIG = {
    measurementId: 'G-MWZ2ZWZP4G',
    leadEndpoint: 'https://api.web3forms.com/submit',
    accessKey: '88f6e4fc-7b15-4519-9408-6946321501b6'
  };
  const CONSENT_KEY = 'jft_cookie_choice';
  const ATTRIBUTION_KEY = 'jft_attribution';
  let analyticsLoaded = false;

  function getAttribution() {
    const params = new URLSearchParams(location.search);
    let stored = {};
    try { stored = JSON.parse(sessionStorage.getItem(ATTRIBUTION_KEY) || '{}'); } catch (_) {}
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid'].forEach(function (field) {
      if (params.get(field)) stored[field] = params.get(field).slice(0, 180);
    });
    if (!stored.landing_page) stored.landing_page = location.pathname;
    if (!stored.referrer && document.referrer) stored.referrer = document.referrer.slice(0, 500);
    try { sessionStorage.setItem(ATTRIBUTION_KEY, JSON.stringify(stored)); } catch (_) {}
    return stored;
  }

  function loadAnalytics() {
    if (analyticsLoaded || localStorage.getItem(CONSENT_KEY) !== 'accepted') return;
    analyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', CONFIG.measurementId, {
      anonymize_ip: true,
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(CONFIG.measurementId);
    document.head.appendChild(script);
  }

  function setConsent(choice) {
    localStorage.setItem(CONSENT_KEY, choice);
    const bar = document.getElementById('jft-cookie-bar');
    if (bar) bar.classList.remove('show');
    if (choice === 'accepted') loadAnalytics();
    window.dispatchEvent(new CustomEvent('jft:consent', { detail: choice }));
  }

  function track(eventName, parameters) {
    if (localStorage.getItem(CONSENT_KEY) !== 'accepted') return;
    loadAnalytics();
    if (window.gtag) window.gtag('event', eventName, parameters || {});
  }

  function leadId() {
    const random = window.crypto && crypto.randomUUID ? crypto.randomUUID().slice(0, 8) : Math.random().toString(36).slice(2, 10);
    return 'JFT-' + new Date().toISOString().replace(/\D/g, '').slice(0, 14) + '-' + random.toUpperCase();
  }

  async function submitLead(data) {
    const payload = Object.assign({}, data, getAttribution(), {
      access_key: CONFIG.accessKey,
      lead_id: data.lead_id || leadId(),
      page_url: location.href.slice(0, 900),
      submitted_at_utc: new Date().toISOString(),
      botcheck: ''
    });
    const response = await fetch(CONFIG.leadEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await response.json().catch(function () { return {}; });
    if (!response.ok || !result.success) throw new Error(result.message || 'Lead submission failed');
    track('generate_lead', { lead_type: data.lead_type || 'inquiry', page_path: location.pathname });
    return Object.assign(result, { lead_id: payload.lead_id });
  }

  function enrichForms() {
    const attribution = getAttribution();
    document.querySelectorAll('form').forEach(function (form) {
      Object.keys(attribution).forEach(function (name) {
        if (form.elements[name]) return;
        const input = document.createElement('input');
        input.type = 'hidden'; input.name = name; input.value = attribution[name];
        form.appendChild(input);
      });
      form.addEventListener('focusin', function begin() {
        track('form_start', { form_id: form.id || form.className || 'form', page_path: location.pathname });
        form.removeEventListener('focusin', begin);
      });
    });
  }

  function init() {
    getAttribution();
    const choice = localStorage.getItem(CONSENT_KEY);
    if (choice === 'accepted') loadAnalytics();
    const bar = document.getElementById('jft-cookie-bar');
    if (bar && !choice) setTimeout(function () { bar.classList.add('show'); }, 700);
    enrichForms();
    document.addEventListener('click', function (event) {
      const link = event.target.closest('a[href]');
      if (!link) return;
      if (/wa\.me|api\.whatsapp\.com/.test(link.href)) track('contact_whatsapp', { page_path: location.pathname });
      if (link.protocol === 'tel:') track('contact_phone', { page_path: location.pathname });
      if (link.protocol === 'mailto:') track('contact_email', { page_path: location.pathname });
      if (/\.pdf(?:$|\?)/i.test(link.href)) track('file_download', { file_name: link.pathname.split('/').pop(), page_path: location.pathname });
      if (/contact\.html|sample-request\.html/.test(link.href)) track('conversion_link_click', { destination: link.pathname });
      if (link.origin !== location.origin && !/wa\.me|api\.whatsapp\.com/.test(link.href)) {
        track('outbound_click', { destination_host: link.hostname, page_path: location.pathname });
      }
      if (link.dataset.track) track(link.dataset.track, { page_path: location.pathname });
    });
    document.addEventListener('securitypolicyviolation', function (event) {
      let blockedHost = '';
      try { blockedHost = new URL(event.blockedURI || location.href, location.href).host; } catch (_) {}
      track('csp_violation', { directive: event.violatedDirective, blocked_host: blockedHost });
    });
  }

  window.jftCookieAccept = function () { setConsent('accepted'); };
  window.jftCookieDecline = function () { setConsent('essential'); };
  window.jftCookiePreferences = function () {
    localStorage.removeItem(CONSENT_KEY);
    if (window.gtag) window.gtag('consent', 'update', { analytics_storage: 'denied' });
    const bar = document.getElementById('jft-cookie-bar');
    if (bar) bar.classList.add('show');
  };
  window.JFTConversion = { submitLead: submitLead, track: track, getAttribution: getAttribution };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
