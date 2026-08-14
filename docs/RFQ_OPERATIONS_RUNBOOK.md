# RFQ operations and failure-control runbook

Last reviewed: 14 August 2026

## Required production flow

1. Website validates required buyer, product, quantity, country, port, packing, Incoterm and target-shipment-month fields.
2. The submission receives a unique `JFT-YYYYMMDDHHMMSS-XXXXXXXX` lead ID plus source, medium, campaign, landing page, referrer and UTC timestamp.
3. The buyer receives an “RFQ received” acknowledgement containing the same lead ID. This must be configured in the production form/CRM account; frontend success text alone is not delivery proof.
4. The internal trade desk receives the complete payload and lead ID.
5. The CRM creates or updates the buyer/company without discarding a distinct new requirement.
6. Sales moves the opportunity through: `New → Contacted → Specification → Quotation → Sample → Negotiation → Contract → Shipment → Completed/Lost`.

## CRM fields

Lead ID; submitted UTC; buyer name; company; email; WhatsApp/phone; company website; country; product; specification; quantity and unit; packing; destination port; Incoterm; target shipment month; payment preference; target price; import/VAT identifier where voluntarily supplied; source; medium; campaign; landing page; referrer; device category; owner; stage; next action; loss reason.

## Release tests after every endpoint or form change

- Required fields, empty values and keyboard-only completion.
- Invalid and international email/phone formats.
- Unicode names, punctuation and safely escaped special characters.
- Maximum lengths and oversized payload rejection.
- Duplicate click, refresh, back navigation and the eight-second client cooldown.
- Honeypot/spam rejection and server-side rate limiting.
- Offline, slow connection, timeout, 4xx and 5xx responses.
- Buyer acknowledgement and internal notification contain the same lead ID.
- CRM record, attribution and stage are correct.
- No personal data appears in analytics event parameters or URLs.

Use a dedicated test recipient/company and prefix test submissions with `TEST—DO NOT QUOTE`. Do not send fake production enquiries without notifying the trade-desk owner.

## Current external dependency

The static site uses a Web3Forms public access identifier. Restrict it to `jftagro.com`, rotate it after suspected abuse, enable provider spam controls, and verify acknowledgement/notification delivery in the account. For stronger protection, move submission to a same-origin Cloudflare Worker, store the provider credential as a Worker secret, verify Turnstile server-side, enforce body/field limits and rate-limit the route before changing the frontend endpoint.
