# Form security deployment gate

The browser submits lead forms to the same-origin `/api/lead` Worker endpoint.
The Worker validates origin, payload size, field names, honeypots and required
contact details before forwarding to Web3Forms.

Before deployment, configure the existing Web3Forms key as a Worker secret:

```powershell
npx wrangler secret put WEB3FORMS_ACCESS_KEY
```

Do not put the value in `wrangler.jsonc`, HTML, JavaScript or this document.

Turnstile support is server-ready through the optional `TURNSTILE_SECRET`
binding. Do not configure that secret until a production widget/site key has
been created and its client widget has been added to the lead forms. Turnstile
tokens are single-use and must always be validated by the Worker.

After deployment, submit one controlled test lead, confirm delivery, and check
that requests with an invalid Origin, oversized body or populated honeypot are
rejected.
