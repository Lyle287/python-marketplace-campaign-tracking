import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.marketplace_tracking import BuyerUpdate, InfraiClient, SellerAsset, notify_buyer


def main() -> None:
    recipient = os.environ.get("DEMO_BUYER_EMAIL")
    if not recipient:
        raise SystemExit("Set DEMO_BUYER_EMAIL before running the demo")
    result = notify_buyer(
        InfraiClient(),
        SellerAsset("seller-17", "listing-204", "Wholesale coffee beans"),
        BuyerUpdate(recipient, "listing-204"),
    )
    print("message_id:", result.get("message_id"))


if __name__ == "__main__":
    main()
