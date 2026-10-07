from src.marketplace_tracking import handoff_state


def test_open_event_moves_order_to_seller_follow_up():
    events = [{"type": "delivered"}, {"type": "open"}]
    assert handoff_state(events) == "seller_follow_up"


def test_bounce_event_requires_delivery_review():
    assert handoff_state([{"type": "bounce"}]) == "delivery_review"

