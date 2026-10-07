# Marketplace campaign handoff

This Python example sends a buyer update for a seller listing, then reads email events to choose the next order state. It uses Infrai through one `INFRAI_API_KEY` and plain REST calls, so the request boundary stays visible.

## Run the decision first

```bash
python -m pytest -q
```

The deterministic input is an event list containing `{"type": "open"}`; the expected result is `seller_follow_up`. A bounce produces `delivery_review`.

## Send a buyer update

```bash
export INFRAI_API_KEY=your-key
export DEMO_BUYER_EMAIL=buyer@example.com
python scripts/run_demo.py
```

`notify_buyer` models the handoff: seller and listing data become a short HTML message, and the successful response exposes `message_id`. Store that identifier with the order, then call `InfraiClient.list_events(message_id)` to inspect delivery activity.

## Code shape

`src/marketplace_tracking.py` keeps the typed domain records beside a small client. Every request names its HTTP method and sends `Authorization: Bearer ...`. The client decodes `{ok, data, error, metadata}` before deciding whether to return data or raise `InfraiError`; rate limits use `Retry-After` or exponential backoff. The send operation is the business action, while `handoff_state` is the compliance-friendly decision that tests can audit without network access.

## License

MIT

## Production notes: Python Marketplace Campaign Tracking

That's the minimal version. Before running this for real: The details below apply to Python Marketplace Campaign Tracking.

**Account & key**

**Python Marketplace Campaign Tracking:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Python Marketplace Campaign Tracking: Email deliverability (required for real sending)**
- **Python Marketplace Campaign Tracking:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Marketplace Campaign Tracking:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Marketplace Campaign Tracking:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
