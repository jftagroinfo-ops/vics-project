export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Preserve existing explicit .html URLs while supporting directory homes.
    if (url.pathname.endsWith("/")) {
      url.pathname += "index.html";
      return env.ASSETS.fetch(new Request(url, request));
    }

    return env.ASSETS.fetch(request);
  },
};
