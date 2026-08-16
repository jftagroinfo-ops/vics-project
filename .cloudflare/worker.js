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
