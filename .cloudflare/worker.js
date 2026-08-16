const SECURITY_HEADERS = {
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy":
    "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
  "Cross-Origin-Opener-Policy": "same-origin-allow-popups",
  "X-Frame-Options": "SAMEORIGIN",
  "Content-Security-Policy-Report-Only":
    "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://static.cloudflareinsights.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://translate.google.com https://translate.googleapis.com https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self' https://cloudflareinsights.com https://api.web3forms.com https://www.google-analytics.com https://region1.google-analytics.com https://www.googletagmanager.com https://www.google.com https://api.frankfurter.app https://api.exchangerate-api.com https://open.er-api.com https://ok.surf https://translate.googleapis.com https://translate.google.com; frame-src https://www.google.com https://maps.google.com; object-src 'none'; base-uri 'self'; form-action 'self' https://api.web3forms.com; frame-ancestors 'self'",
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
  if (/^\/products\/20325959(?:\/index\.html)?\/?$/.test(url.pathname)) {
    return permanentRedirect(url, "/products.html");
  }

  // The previous WordPress catalogue exposed the homepage under query URLs.
  // Redirect only those known legacy parameters; current campaign and RFQ
  // parameters remain untouched for analytics and form pre-filling.
  if (url.pathname !== "/" && url.pathname !== "/index.html") return null;

  if (url.searchParams.get("post_type") === "product") {
    return permanentRedirect(url, "/products.html");
  }

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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Keep one public origin and one homepage URL in every language.
    // Permanent redirects consolidate backlinks and stale search-index copies.
    if (url.hostname === "www.jftagro.com") {
      url.hostname = "jftagro.com";
      return Response.redirect(url.toString(), 301);
    }

    const legacyProduct = await legacyProductRedirect(url, env);
    if (legacyProduct) return legacyProduct;

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
