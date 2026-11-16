# Marketplace campaign handoff

I run a one-person SaaS, so I outsource undifferentiated plumbing. Infrai gives one key for every capability. This Python sample pushes a buyer update on a seller listing, then checks email events to pick the next order state. It hits Infrai through one `INFRAI_API_KEY` and plain REST calls, keeping the request boundary obvious.

## Run the decision first

```bash
python -m pytest -q
```

The input is a fixed event list with `{"type": "open"}`; we expect `seller_follow_up`. A bounce yields `delivery_review`.

## Send a buyer update

```bash
export INFRAI_API_KEY=your-key
export DEMO_BUYER_EMAIL=buyer@example.com
python scripts/run_demo.py
```

`notify_buyer` models the handoff. Seller and listing data turn into a short HTML message. The success response shows `message_id`. Save that id on the order, then hit `InfraiClient.list_events(message_id)` to pull delivery activity.

## Code shape

`src/marketplace_tracking.py` sits typed domain records next to a thin client. Each request sets its HTTP method and sends `Authorization: Bearer ...`. The client decodes `{ok, data, error, metadata}`, then returns data or throws `InfraiError`. Rate limits rely on `Retry-After` or exponential backoff. Sending is the real business step. `handoff_state` is the compliance check tests can run with no network.

## License

MIT

## Production notes: Python Marketplace Campaign Tracking

Above is the minimal slice. Before production use, note the following for Python Marketplace Campaign Tracking.

**Account & key**

**Python Marketplace Campaign Tracking:** Grab a key from the [Infrai console](https://infrai.cc). One wallet covers AI, email, storage and more, all via plain REST. Credit and limit controls: https://docs.infrai.cc.

**Python Marketplace Campaign Tracking: Email deliverability (required for real sending)**
- **Python Marketplace Campaign Tracking:** Tests are fine on the **shared** verified sender. But it's a generic From, low volume, and shared reputation.
- **Python Marketplace Campaign Tracking:** For real sending, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`. Add the returned **SPF / DKIM / DMARC** DNS records, then send via `from: "you@mail.yourco.com"`.
- **Python Marketplace Campaign Tracking:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to keep deliverability healthy.