const SECURITY_HEADERS = {
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy":
    "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
  "Cross-Origin-Opener-Policy": "same-origin-allow-popups",
  "X-Frame-Options": "SAMEORIGIN",
  "Content-Security-Policy":
    "default-src 'self'; script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://translate.google.com https://translate.googleapis.com https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self' https://cloudflareinsights.com https://www.google-analytics.com https://region1.google-analytics.com https://www.googletagmanager.com https://www.google.com https://api.frankfurter.app https://api.exchangerate-api.com https://open.er-api.com https://ok.surf https://translate.googleapis.com https://translate.google.com; frame-src https://www.google.com https://maps.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'",
};

const LEGACY_PRODUCT_ALIASES = {
  "grey-millet": "/grey-millet-exporter.html",
  raisins: "/indian-raisins-kishmish-exporter.html",
  "senna-leaves": "/senna-leaves-exporter.html",
  "sesame-seeds": "/sesame-seeds-naturalhulled-exporter.html",
};

const LEGACY_ARTICLE_REDIRECTS = {
  "blog-cif-fob-explained.html": "/blog-bill-of-lading-explained-importers.html",
  "blog-eu-mrl-basmati.html": "/blog-red-chilli-teja-export-india-2026.html",
  "blog-india-uae-cepa.html": "/blog-import-duty-indian-rice-by-country.html",
  "blog-indian-white-rice-export-policy-2026-latest-updates.html": "/blog-ir64-export.html",
  "blog-ir64-africa.html": "/blog-ir64-export.html",
  "blog-lc-vs-tt.html": "/blog-letter-of-credit-food-imports-india.html",
  "blog-private-label-rice.html": "/blog-how-to-choose-indian-agro-exporter.html",
  "blog-sesame-export-2026.html": "/blog-top-indian-agro-commodities-import-2026.html",
  "blog-spice-trends-2026.html": "/blog-turmeric-finger-export-india-2026.html",
};

const LEGACY_PRETTY_REDIRECTS = {
  "/logistics/mundra-rice-exports/certificates.html": "/certificates.html",
  "/1121-golden-sella-basmati-rice/": "/1121-basmati-rice-exporter.html",
  "/1121-raw-rice-basmati-rice/": "/1121-raw-basmati-rice-exporter.html",
  "/1121-steam-basmati-rice/": "/1121-steam-basmati-rice-exporter.html",
  "/1401-steam-basmati-rice/": "/1401-steam-basmati-rice-exporter.html",
  "/1509-golden-sella-basmati-rice/": "/1509-golden-sella-basmati-exporter.html",
  "/1509-raw-basmati-rice/": "/products.html",
  "/1509-white-sella-basmati-rice/": "/products.html",
  "/1718-golden-sella-basmati-rice/": "/1718-golden-sella-basmati-exporter.html",
  "/aboutus/": "/about.html",
  "/animal-and-bird-feed/": "/products.html",
  "/basil-seeds-tukmaria/": "/basil-seeds-exporter.html",
  "/bay-leaves/": "/bay-leaf-exporter.html",
  "/blog/": "/blog.html",
  "/contact-us/": "/contact.html",
  "/fennel-seeds-powder-sounff-variyali/": "/fennel-seeds-sounff-exporter.html",
  "/grey-millet/": "/grey-millet-exporter.html",
  "/indian-basmati-rice/": "/1121-basmati-rice-exporter.html",
  "/indian-tamarind-with-seeds-and-without-seeds/": "/tamarind-exporter.html",
  "/products/": "/products.html",
  "/raisins/": "/indian-raisins-kishmish-exporter.html",
  "/ricemill/": "/infrastructure.html",
  "/senna-pods/": "/senna-pods-exporter.html",
  "/spices/": "/spices-exporter-india.html",
  "/the-basic-processes-of-rice-milling/": "/infrastructure.html",
  "/whole-red-chilly/": "/dry-red-chilli-exporter.html",
};

const ROOT_RETIRED_ARTICLES = new Set([
  "blog-cif-fob-explained.html",
  "blog-eu-mrl-basmati.html",
  "blog-india-uae-cepa.html",
  "blog-indian-white-rice-export-policy-2026-latest-updates.html",
  "blog-ir64-africa.html",
  "blog-spice-trends-2026.html",
]);

const LOCALE_PATH = /^\/(?:ar|es|fr|id|ms|pt|ru|si|th|vi)\//;

function permanentRedirect(url, pathname) {
  const target = new URL(url.origin);
  target.pathname = pathname;
  return Response.redirect(target.toString(), 301);
}

async function legacyProductRedirect(url, env) {
  // Retire the former hosted-store archive that Google still remembers.
  if (/^\/products\/\d+(?:\/index\.html)?\/?$/.test(url.pathname)) {
    return permanentRedirect(url, "/products.html");
  }

  if (/^\/products\/page\/\d+\/?$/.test(url.pathname)) {
    return permanentRedirect(url, "/products.html");
  }

  // The previous WordPress catalogue exposed the homepage under query URLs.
  // Redirect only those known legacy parameters; current campaign and RFQ
  // parameters remain untouched for analytics and form pre-filling.
  if (url.searchParams.get("post_type") === "product") {
    return permanentRedirect(url, "/products.html");
  }

  if (url.pathname !== "/" && url.pathname !== "/index.html") return null;

  const product = (url.searchParams.get("product") || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9-]/g, "")
    .replace(/-+/g, "-");
  if (!product) return null;

  const alias = LEGACY_PRODUCT_ALIASES[product];
  if (alias) return permanentRedirect(url, alias);

  for (const pathname of [
    `/${product}-exporter.html`,
    `/${product}-supplier.html`,
    `/${product}.html`,
  ]) {
    const candidate = new URL(pathname, url.origin);
    const response = await env.ASSETS.fetch(
      new Request(candidate, { method: "HEAD" }),
    );
    if (response.status === 200) return permanentRedirect(url, pathname);
  }

  return permanentRedirect(url, "/products.html");
}

function withSecurityHeaders(assetResponse) {
  const response = new Response(assetResponse.body, assetResponse);

  const contentType = response.headers.get("Content-Type") || "";
  if (
    !/charset=/i.test(contentType) &&
    (contentType.startsWith("text/") ||
      contentType.startsWith("application/json") ||
      contentType.startsWith("application/javascript") ||
      contentType.startsWith("application/xml"))
  ) {
    response.headers.set("Content-Type", `${contentType}; charset=utf-8`);
  }

  for (const [name, value] of Object.entries(SECURITY_HEADERS)) {
    response.headers.set(name, value);
  }

  return response;
}

function leadResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      "Referrer-Policy": "no-referrer",
    },
  });
}

async function readLeadPayload(request) {
  const contentType = request.headers.get("Content-Type") || "";
  if (contentType.includes("application/json")) return request.json();
  const form = await request.formData();
  return Object.fromEntries(form.entries());
}

async function verifyTurnstile(request, env, payload) {
  if (!env.TURNSTILE_SECRET) return true;
  const token = String(payload["cf-turnstile-response"] || "");
  if (!token) return false;
  const response = await fetch(
    "https://challenges.cloudflare.com/turnstile/v0/siteverify",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        secret: env.TURNSTILE_SECRET,
        response: token,
        remoteip: request.headers.get("CF-Connecting-IP") || undefined,
      }),
    },
  );
  const result = await response.json();
  return Boolean(result.success && (!result.hostname || result.hostname === "jftagro.com"));
}

async function handleLead(request, env) {
  if (request.method !== "POST") {
    return leadResponse({ success: false, message: "Method not allowed" }, 405);
  }
  const origin = request.headers.get("Origin");
  if (origin !== "https://jftagro.com" && origin !== "https://www.jftagro.com") {
    return leadResponse({ success: false, message: "Invalid submission origin" }, 403);
  }
  const length = Number(request.headers.get("Content-Length") || 0);
  if (length > 32_768) {
    return leadResponse({ success: false, message: "Submission is too large" }, 413);
  }
  if (!env.WEB3FORMS_ACCESS_KEY) {
    return leadResponse({ success: false, message: "Form service is not configured" }, 503);
  }

  let raw;
  try {
    raw = await readLeadPayload(request);
  } catch (_) {
    return leadResponse({ success: false, message: "Invalid form payload" }, 400);
  }
  if (!raw || typeof raw !== "object" || Object.keys(raw).length > 80) {
    return leadResponse({ success: false, message: "Invalid form payload" }, 400);
  }
  if (raw.website || raw.company_website || raw.botcheck) {
    return leadResponse({ success: false, message: "Automated submission rejected" }, 400);
  }
  if (!(await verifyTurnstile(request, env, raw))) {
    return leadResponse({ success: false, message: "Security check failed" }, 403);
  }

  const payload = {};
  for (const [name, value] of Object.entries(raw)) {
    if (name === "access_key" || name === "cf-turnstile-response") continue;
    if (!/^[a-zA-Z0-9_.-]{1,80}$/.test(name)) continue;
    payload[name] = String(value).trim().slice(0, 2_000);
  }
  if (!payload.email && !payload.phone && !payload.whatsapp) {
    return leadResponse({ success: false, message: "Email or phone is required" }, 400);
  }
  payload.access_key = env.WEB3FORMS_ACCESS_KEY;
  payload.botcheck = "";

  const upstream = await fetch("https://api.web3forms.com/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await upstream.json().catch(() => ({ success: false }));
  return leadResponse(
    {
      success: Boolean(upstream.ok && result.success),
      message: result.message || (upstream.ok ? "Submission received" : "Submission failed"),
      lead_id: payload.lead_id || "",
    },
    upstream.ok && result.success ? 200 : 502,
  );
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/lead") {
      return handleLead(request, env);
    }

    // Keep one public origin and one homepage URL in every language.
    // Permanent redirects consolidate backlinks and stale search-index copies.
    if (url.hostname === "www.jftagro.com") {
      url.hostname = "jftagro.com";
      return Response.redirect(url.toString(), 301);
    }

    const legacyProduct = await legacyProductRedirect(url, env);
    if (legacyProduct) return legacyProduct;

    const legacyPretty = LEGACY_PRETTY_REDIRECTS[url.pathname.toLowerCase()];
    if (legacyPretty) return permanentRedirect(url, legacyPretty);

    // Old generators incorrectly linked locale-prefixed sitemap and shared
    // asset URLs. Consolidate them only when a real root resource exists.
    const localeMatch = url.pathname.match(
      /^\/(?:ar|es|fr|id|ms|pt|ru|si|th|vi)(\/(?:assets|images)\/.*|\/sitemap\.xml)$/i,
    );
    if (localeMatch) {
      const rootPath = localeMatch[1];
      if (rootPath.toLowerCase() === "/sitemap.xml") {
        return permanentRedirect(url, "/sitemap.xml");
      }

      const rootAsset = new URL(rootPath, url.origin);
      const rootResponse = await env.ASSETS.fetch(
        new Request(rootAsset, { method: "HEAD" }),
      );
      if (rootResponse.status === 200) return permanentRedirect(url, rootPath);
    }

    // header.html was an internal include, never a public content page.
    if (/^\/(?:ar|es|fr|id|ms|pt|ru|si|th|vi)\/header\.html$/i.test(url.pathname)) {
      return new Response("Gone", {
        status: 410,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
      });
    }

    const articleName = url.pathname.split("/").pop();
    const legacyArticle = LEGACY_ARTICLE_REDIRECTS[articleName];
    if (
      legacyArticle &&
      (LOCALE_PATH.test(url.pathname) || ROOT_RETIRED_ARTICLES.has(articleName))
    ) {
      return permanentRedirect(url, legacyArticle);
    }

    if (url.pathname.endsWith("/index.html")) {
      url.pathname = url.pathname.slice(0, -"index.html".length);
      return Response.redirect(url.toString(), 301);
    }

    // Historical crawler URLs such as /?j=123 served the homepage unchanged.
    // Remove only that known non-content parameter; preserve legitimate query data.
    if (url.searchParams.has("j")) {
      url.searchParams.delete("j");
      return Response.redirect(url.toString(), 301);
    }

    // Preserve all other explicit .html URLs while supporting directory homes.
    if (url.pathname.endsWith("/")) {
      url.pathname += "index.html";
      const assetResponse = await env.ASSETS.fetch(new Request(url, request));
      return withSecurityHeaders(assetResponse);
    }

    const assetResponse = await env.ASSETS.fetch(request);
    return withSecurityHeaders(assetResponse);
  },
};
