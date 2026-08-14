(function () {
  'use strict';

  const CONFIG = {
    measurementId: 'G-MWZ2ZWZP4G',
    leadEndpoint: 'https://api.web3forms.com/submit',
    accessKey: '88f6e4fc-7b15-4519-9408-6946321501b6'
  };
  const CONSENT_KEY = 'jft_cookie_choice';
  const ATTRIBUTION_KEY = 'jft_attribution';
  const LAST_SUBMISSION_KEY = 'jft_last_lead_submission';
  let analyticsLoaded = false;
  const trackedOnce = new Set();

  function safePath(value) {
    if (!value) return '';
    try { return new URL(value, location.href).pathname.slice(0, 300); } catch (_) { return ''; }
  }

  function referrerHost() {
    try { return document.referrer ? new URL(document.referrer).hostname.slice(0, 100) : '(direct)'; } catch (_) { return '(unknown)'; }
  }

  function getAttribution() {
    const params = new URLSearchParams(location.search);
    let stored = {};
    try { stored = JSON.parse(sessionStorage.getItem(ATTRIBUTION_KEY) || '{}'); } catch (_) {}
    const campaignFields = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_id', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid', 'msclkid', 'fbclid', 'ttclid', 'li_fat_id'];
    const hasCampaign = campaignFields.some(function (field) { return params.get(field); });
    campaignFields.forEach(function (field) {
      if (params.get(field)) stored[field] = params.get(field).slice(0, 180);
    });
    if (!stored.landing_page) stored.landing_page = location.pathname;
    if (!stored.referrer && document.referrer) stored.referrer = document.referrer.slice(0, 500);
    if (!stored.session_started_at_utc) stored.session_started_at_utc = new Date().toISOString();
    if (hasCampaign) {
      stored.campaign_landing_page = location.pathname;
      stored.campaign_captured_at_utc = new Date().toISOString();
    }
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
    if (window.gtag) window.gtag('event', eventName, Object.assign({
      page_path: location.pathname,
      page_title: document.title.slice(0, 150)
    }, parameters || {}));
  }

  function trackOnce(eventName, parameters, uniqueKey) {
    const key = uniqueKey || eventName;
    if (trackedOnce.has(key) || localStorage.getItem(CONSENT_KEY) !== 'accepted') return false;
    trackedOnce.add(key);
    track(eventName, parameters);
    return true;
  }

  function leadId() {
    const random = window.crypto && crypto.randomUUID ? crypto.randomUUID().slice(0, 8) : Math.random().toString(36).slice(2, 10);
    return 'JFT-' + new Date().toISOString().replace(/\D/g, '').slice(0, 14) + '-' + random.toUpperCase();
  }

  async function submitLead(data) {
    if (data.website || data.company_website) throw new Error('Automated submission rejected');
    const lastSubmission = Number(sessionStorage.getItem(LAST_SUBMISSION_KEY) || 0);
    if (Date.now() - lastSubmission < 8000) throw new Error('Please wait before sending another request');
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
    sessionStorage.setItem(LAST_SUBMISSION_KEY, String(Date.now()));
    track('generate_lead', {
      lead_type: data.lead_type || 'inquiry',
      form_id: data.form_id || 'lead_form',
      lead_source: data.lead_source || getAttribution().utm_source || 'website'
    });
    const leadType = (data.lead_type || 'inquiry').toLowerCase();
    const completionEvent = /sample/.test(leadType) ? 'sample_request' : (/rfq|quote/.test(leadType) ? 'rfq_submit' : 'enquiry_submit');
    track(completionEvent, {
      lead_type: leadType,
      form_id: data.form_id || 'lead_form',
      lead_source: data.lead_source || getAttribution().utm_source || 'website'
    });
    return Object.assign(result, { lead_id: payload.lead_id });
  }

  function enrichForms() {
    const attribution = getAttribution();
    document.querySelectorAll('form').forEach(function (form) {
      if (!form.elements.website) {
        const honeypot = document.createElement('input');
        honeypot.type = 'text'; honeypot.name = 'website'; honeypot.tabIndex = -1;
        honeypot.autocomplete = 'off'; honeypot.setAttribute('aria-hidden', 'true');
        honeypot.style.cssText = 'position:fixed!important;inset:0 auto auto 0!important;width:1px!important;height:1px!important;opacity:0!important;clip-path:inset(50%)!important;pointer-events:none!important';
        form.appendChild(honeypot);
      }
      Object.keys(attribution).forEach(function (name) {
        if (form.elements[name]) return;
        const input = document.createElement('input');
        input.type = 'hidden'; input.name = name; input.value = attribution[name];
        form.appendChild(input);
      });
      form.addEventListener('focusin', function begin() {
        const formId = form.id || form.className || 'form';
        track('form_start', { form_id: formId, page_path: location.pathname });
        if (/sample-request\.html/i.test(location.pathname)) track('sample_request_start', { form_id: formId });
        if (/contact\.html/i.test(location.pathname)) track('rfq_start', { form_id: formId });
        form.removeEventListener('focusin', begin);
      });
    });
  }

  function enrichWhatsAppLinks() {
    const heading = document.querySelector('h1');
    const pageContext = ((heading && heading.textContent) || document.title || 'JFT Agro enquiry').trim().replace(/\s+/g, ' ').slice(0, 120);
    document.querySelectorAll('a[href*="wa.me/"],a[href*="api.whatsapp.com"]').forEach(function (link) {
      try {
        const url = new URL(link.href);
        const existing = url.searchParams.get('text') || 'Hello JFT Agro, I would like export information.';
        if (!/Source page:/i.test(existing)) {
          url.searchParams.set('text', existing + '\n\nProduct/page: ' + pageContext + '\nSource page: ' + location.pathname);
          link.href = url.toString();
        }
        link.dataset.leadContext = pageContext;
      } catch (_) {}
    });
  }

  function articleTopic() {
    const value = (location.pathname + ' ' + document.title).toLowerCase();
    const topics = [
      { match: /psyllium|isabgol/, label: 'Psyllium Husk', product: 'psyllium-husk-exporter.html' },
      { match: /cumin|jeera/, label: 'Cumin Seeds', product: 'cumin-seeds-jeera-exporter.html' },
      { match: /turmeric/, label: 'Turmeric Finger', product: 'turmeric-finger-exporter.html' },
      { match: /chilli|chili/, label: 'Dry Red Chilli', product: 'dry-red-chilli-exporter.html' },
      { match: /sesame/, label: 'Sesame Seeds', product: 'sesame-seeds-naturalhulled-exporter.html' },
      { match: /groundnut|peanut/, label: 'Groundnuts', product: 'groundnuts-peanuts-exporter.html' },
      { match: /mung|moong/, label: 'Green Mung Beans', product: 'green-mung-beans-exporter.html' },
      { match: /toor|pigeon pea/, label: 'Toor Dal', product: 'toor-dal-split-pigeon-pea-exporter.html' },
      { match: /rice|basmati|ir64/, label: 'Indian Rice', product: '1121-basmati-rice-exporter.html' }
    ];
    return topics.find(function (topic) { return topic.match.test(value); }) || { label: 'Indian Agro Products', product: 'products.html' };
  }

  function addArticleBuyerPath() {
    if (!/^blog-.*\.html$/i.test(location.pathname.split('/').pop() || '')) return;
    if (location.pathname.split('/').filter(Boolean).length > 1) return;
    const articleBody = document.querySelector('.article-body, .seo-article, article');
    if (!articleBody || document.getElementById('jft-article-next-step')) return;
    const topic = articleTopic();
    const panel = document.createElement('section');
    panel.id = 'jft-article-next-step';
    panel.className = 'jft-article-next-step';
    panel.setAttribute('aria-labelledby', 'jft-next-step-title');
    panel.innerHTML = '<div class="jft-next-step-copy"><span>Buyer next step</span><h2 id="jft-next-step-title">Turn this research into a verified requirement</h2><p>Review the relevant export specification, build a planning estimate, or send your quantity and destination for a commercial response.</p></div>' +
      '<div class="jft-next-step-actions"><a href="' + topic.product + '" data-track="article_to_product">View ' + topic.label + '</a><a href="quote-calculator.html" data-track="article_to_calculator">Build Reference Estimate</a><a class="primary" href="contact.html?product=' + encodeURIComponent(topic.label) + '&source=article#inquiry-form" data-track="article_to_rfq">Request Export Quote</a></div>';
    articleBody.insertAdjacentElement('afterend', panel);
    if (!document.getElementById('jft-article-next-step-style')) {
      const style = document.createElement('style');
      style.id = 'jft-article-next-step-style';
      style.textContent = '.jft-article-next-step{margin:38px 0;padding:24px;border:1px solid #d8e2dc;border-top:4px solid #eebf45;border-radius:8px;background:#f7faf7;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:center}.jft-next-step-copy span{font:800 .68rem Montserrat,sans-serif;letter-spacing:1.4px;text-transform:uppercase;color:#397531}.jft-next-step-copy h2{font:700 1.25rem Merriweather,serif!important;color:#123a31!important;border:0!important;padding:0!important;margin:7px 0 8px!important}.jft-next-step-copy p{font-size:.94rem!important;line-height:1.6!important;margin:0!important;color:#52645e!important}.jft-next-step-actions{display:grid;gap:8px;min-width:220px}.jft-next-step-actions a{font:800 .7rem Montserrat,sans-serif;letter-spacing:.4px;text-transform:uppercase;text-align:center;text-decoration:none;color:#1a5b37;background:#fff;border:1px solid #cfdcd3;border-radius:6px;padding:11px 14px}.jft-next-step-actions a.primary{color:#fff;background:#397531;border-color:#397531}@media(max-width:720px){.jft-article-next-step{grid-template-columns:1fr;padding:20px}.jft-next-step-actions{min-width:0}}';
      document.head.appendChild(style);
    }
  }

  function addEditorialReviewNote() {
    if (!/^blog-.*\.html$/i.test(location.pathname.split('/').pop() || '')) return;
    if (location.pathname.split('/').filter(Boolean).length > 1) return;
    const body = document.querySelector('.article-body, .seo-article, article');
    if (!body || document.getElementById('jft-editorial-review')) return;
    const note = document.createElement('aside');
    note.id = 'jft-editorial-review';
    note.className = 'jft-editorial-review';
    note.setAttribute('aria-label', 'Editorial review and sources');
    note.innerHTML = '<strong>Reviewed by JFT Agro Trade Desk</strong><span>Commercial and regulatory information was last checked on 14 August 2026. Requirements can change; confirm the current rule with the destination authority and your licensed customs adviser before contracting.</span><span class="jft-source-links"><a href="https://apeda.gov.in/" target="_blank" rel="noopener noreferrer">APEDA</a><a href="https://www.dgft.gov.in/" target="_blank" rel="noopener noreferrer">DGFT</a><a href="https://fssai.gov.in/" target="_blank" rel="noopener noreferrer">FSSAI</a><a href="https://indianspices.com/" target="_blank" rel="noopener noreferrer">Spices Board India</a><a href="mailto:exports@jftagro.com?subject=Editorial%20correction">Suggest a correction</a></span>';
    body.appendChild(note);
    if (!document.getElementById('jft-editorial-review-style')) {
      const style = document.createElement('style');
      style.id = 'jft-editorial-review-style';
      style.textContent = '.jft-editorial-review{margin:34px 0 0;padding:20px;border:1px solid #d4dfd7;border-left:4px solid #397531;border-radius:6px;background:#f7faf7;color:#40534c;font:400 .88rem/1.65 Lato,sans-serif}.jft-editorial-review strong{display:block;color:#1a3c34;font-family:Montserrat,sans-serif;font-size:.78rem;text-transform:uppercase;letter-spacing:.7px;margin-bottom:6px}.jft-editorial-review span{display:block}.jft-source-links{display:flex!important;flex-wrap:wrap;gap:8px 14px;margin-top:10px}.jft-source-links a{color:#285f2a;text-decoration:underline;text-underline-offset:3px;font-weight:700}';
      document.head.appendChild(style);
    }
  }

  function initPageDiagnostics() {
    const isNotFound = document.body.dataset.pageType === '404' || /page not found/i.test(document.title);
    if (isNotFound) trackOnce('page_not_found', {
      requested_path: safePath(location.href),
      referrer_host: referrerHost(),
      referrer_path: safePath(document.referrer) || '(direct)'
    }, 'page_not_found:' + location.pathname);

    if (/^blog-.*\.html$/i.test(location.pathname.split('/').pop() || '')) {
      const topic = articleTopic();
      trackOnce('article_view', { content_group: 'insights', article_topic: topic.label });
      let maximumDepth = 0;
      window.addEventListener('scroll', function () {
        const height = document.documentElement.scrollHeight - window.innerHeight;
        if (height <= 0) return;
        const depth = Math.round((window.scrollY / height) * 100);
        [50, 90].forEach(function (threshold) {
          if (depth >= threshold && maximumDepth < threshold) {
            maximumDepth = threshold;
            trackOnce('article_read_depth', { percent_scrolled: threshold, article_topic: topic.label }, 'article_depth_' + threshold);
          }
        });
      }, { passive: true });
    }

    if (/-exporter\.html$|-supplier\.html$|products\.html$/i.test(location.pathname)) {
      const productContext = {
        item_name: (document.querySelector('h1') || {}).textContent || document.title,
        item_category: document.body.dataset.category || 'agro_products'
      };
      trackOnce('view_item', productContext, 'view_item:' + location.pathname);
      trackOnce('product_view', productContext, 'product_view:' + location.pathname);
    }

    const params = new URLSearchParams(location.search);
    if (/contact\.html$/i.test(location.pathname) && params.get('source') === 'quote_calculator') {
      trackOnce('rfq_prefill_loaded', {
        lead_source: 'quote_calculator',
        product_category: (params.get('product') || 'unspecified').slice(0, 100)
      });
    }
    window.dispatchEvent(new CustomEvent('jft:tracker-ready'));
  }

  function init() {
    getAttribution();
    const choice = localStorage.getItem(CONSENT_KEY);
    if (choice === 'accepted') loadAnalytics();
    const bar = document.getElementById('jft-cookie-bar');
    if (bar && !choice) setTimeout(function () { bar.classList.add('show'); }, 700);
    enrichForms();
    enrichWhatsAppLinks();
    addArticleBuyerPath();
    addEditorialReviewNote();
    initPageDiagnostics();
    window.addEventListener('jft:consent', function (event) {
      if (event.detail === 'accepted') initPageDiagnostics();
    });
    document.addEventListener('click', function (event) {
      const link = event.target.closest('a[href]');
      if (!link) return;
      if (/wa\.me|api\.whatsapp\.com/.test(link.href)) {
        const context = link.dataset.leadContext || document.title.slice(0, 120);
        track('contact_whatsapp', { page_path: location.pathname, product_or_page: context });
        track('whatsapp_click', { page_path: location.pathname, product_or_page: context });
      }
      if (link.protocol === 'tel:') track('contact_phone', { page_path: location.pathname });
      if (link.protocol === 'mailto:') track('contact_email', { page_path: location.pathname });
      if (/\.pdf(?:$|\?)/i.test(link.href)) {
        const fileName = link.pathname.split('/').pop();
        track('file_download', { file_name: fileName, page_path: location.pathname });
        if (/profile|catalog|brochure/i.test(fileName || '')) track('brochure_download', { file_name: fileName });
      }
      if (/contact\.html|sample-request\.html/.test(link.href)) {
        track('conversion_link_click', { destination: link.pathname });
        track(/sample-request\.html/.test(link.href) ? 'sample_request_click' : 'rfq_click', { destination: link.pathname });
      }
      if (link.origin !== location.origin && !/wa\.me|api\.whatsapp\.com/.test(link.href)) {
        track('outbound_click', { destination_host: link.hostname, page_path: location.pathname });
      }
      if (link.dataset.track) track(link.dataset.track, {
        destination_path: safePath(link.href),
        link_text: (link.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 100)
      });
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
  window.JFTConversion = { submitLead: submitLead, track: track, trackOnce: trackOnce, getAttribution: getAttribution };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
