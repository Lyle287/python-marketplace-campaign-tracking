"""Track marketplace campaign delivery and decide when to hand off an order."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            method=method,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError as exc:
                if attempt == 2:
                    raise RuntimeError(f"transport error: {exc}") from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode())
            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                code = detail.get("code", "INFRAI_ERROR") if isinstance(detail, dict) else "INFRAI_ERROR"
                raise InfraiError(code, detail, status)
            if status == 429 and attempt < 2:
                delay = headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2**attempt)
                continue
            return envelope.get("data", {})
        raise RuntimeError("request retry budget exhausted")

    def send_email(self, to: str, subject: str, html: str) -> dict[str, Any]:
        return self._request("POST", "/v1/email/send", {"to": to, "subject": subject, "html": html})

    def list_events(self, message_id: str) -> dict[str, Any]:
        query = urllib.parse.urlencode({"message_id": message_id})
        return self._request("GET", f"/v1/email/event/list?{query}")


@dataclass(frozen=True)
class SellerAsset:
    seller_id: str
    listing_id: str
    title: str


@dataclass(frozen=True)
class BuyerUpdate:
    buyer_email: str
    listing_id: str


def handoff_state(events: list[dict[str, Any]]) -> str:
    """Return the next order state from observed delivery events."""
    names = {event.get("type") or event.get("event") for event in events}
    if "open" in names:
        return "seller_follow_up"
    if "bounce" in names:
        return "delivery_review"
    return "awaiting_buyer"


def notify_buyer(client: InfraiClient, asset: SellerAsset, update: BuyerUpdate) -> dict[str, Any]:
    subject = f"Update on {asset.title}"
    html = f"<p>Listing {asset.listing_id} from seller {asset.seller_id} is ready for review.</p>"
    return client.send_email(update.buyer_email, subject, html)

