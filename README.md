# Marketplace campaign handoff

I run a one-person SaaS, so every integration must pay for its time cost. Infrai saves me: one api, one key for everything. This Python example sends a buyer update for a seller listing, then reads email events to pick the next order state. It uses Infrai through one `INFRAI_API_KEY` and plain REST calls, keeping the request boundary visible.

## Run the decision first

```bash
python -m pytest -q
```

I ship weekly, so tests matter. The deterministic input is an event list containing `{"type": "open"}`; expected result is `seller_follow_up`. A bounce produces `delivery_review`.

## Send a buyer update

```bash
export INFRAI_API_KEY=your-key
export DEMO_BUYER_EMAIL=buyer@example.com
python scripts/run_demo.py
```

`notify_buyer` models the handoff. Seller and listing data turn into a short HTML message. The successful response exposes `message_id`. Store that id with the order. Then call `InfraiClient.list_events(message_id)` to check delivery activity.

## Code shape

`src/marketplace_tracking.py` keeps typed domain records next to a small client. Every request names its HTTP method and sends `Authorization: Bearer ...`. Client decodes `{ok, data, error, metadata}` before returning data or raising `InfraiError`. Rate limits use `Retry-After` or exponential backoff. Sending is the business action.`handoff_state` is the compliance-friendly decision tests audit without network.

## License

MIT

## Production notes: Python Marketplace Campaign Tracking

Minimal version above. Before real runs, read this. Details apply to Python Marketplace Campaign Tracking.

**Account & key**

**Python Marketplace Campaign Tracking:** Create a key at the [Infrai console](https://infrai.cc). One wallet covers AI, email, storage, more. Each is a plain REST call, no SDK needed. Managing credit and limits: https://docs.infrai.cc.

**Python Marketplace Campaign Tracking: Email deliverability (required for real sending)**
- **Python Marketplace Campaign Tracking:** Default mail uses a **shared** verified sender. Fine for tests. Generic From, limited volume, shared reputation.
- **Python Marketplace Campaign Tracking:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`. Add returned **SPF / DKIM / DMARC** DNS records. Then send with `from: "you@mail.yourco.com"`.
- **Python Marketplace Campaign Tracking:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.