# core/events.py
"""Minimal publish-subscribe event bus so systems don't import each other."""

from collections import defaultdict
from typing import Callable, Any


class EventBus:
    def __init__(self):
        self._listeners: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable) -> None:
        self._listeners[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        self._listeners[event] = [
            cb for cb in self._listeners[event] if cb is not callback
        ]

    def emit(self, event: str, **kwargs: Any) -> None:
        for cb in self._listeners[event]:
            cb(**kwargs)


# Global singleton
bus = EventBus()

# ---- Event names (string constants so typos are caught) ----
EVT_SALE_MADE        = "sale_made"        # data: amount, customer
EVT_CRAFT_DONE       = "craft_done"       # data: quantity
EVT_CUSTOMER_HAPPY   = "customer_happy"   # data: customer
EVT_CUSTOMER_LEFT    = "customer_left"    # data: customer, reason
EVT_DAY_START        = "day_start"        # data: day_number
EVT_DAY_END          = "day_end"          # data: day_number, earnings
EVT_LEVEL_UP         = "level_up"         # data: new_level
EVT_UPGRADE_BOUGHT   = "upgrade_bought"   # data: upgrade_id
EVT_RESTOCK_DONE     = "restock_done"     # data: item, quantity
EVT_WEATHER_CHANGE   = "weather_change"   # data: weather
EVT_NOTIFICATION     = "notification"     # data: text, color
EVT_IAP_PURCHASE     = "iap_purchase"     # data: pack
EVT_GEM_SPEND        = "gem_spend"        # data: amount, reason
