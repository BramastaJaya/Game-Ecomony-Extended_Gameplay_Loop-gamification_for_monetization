# systems/economy.py
"""Core economy: inventory, pricing, crafting, revenue, cost tracking."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional
from core.constants import *
from core.events import bus, EVT_CRAFT_DONE, EVT_SALE_MADE, EVT_NOTIFICATION


@dataclass
class Inventory:
    lemons:   int = 0
    sugar:    int = 0
    ice:      int = 0
    cups:     int = 0
    lemonade: int = 0

    def as_dict(self) -> Dict[str, int]:
        return {
            "lemons":   self.lemons,
            "sugar":    self.sugar,
            "ice":      self.ice,
            "cups":     self.cups,
            "lemonade": self.lemonade,
        }

    def can_craft(self, batch_mult: int = 1) -> bool:
        r = RECIPE
        n = batch_mult
        return (self.lemons >= r["lemons"] * n and
                self.sugar  >= r["sugar"]  * n and
                self.ice    >= r["ice"]    * n and
                self.cups   >= r["cups"]   * n and
                self.lemonade < MAX_LEMONADE)


@dataclass
class PriceSettings:
    sell_price: float = DEFAULT_SELL_PRICE

    def raise_price(self, step: float = 0.25) -> None:
        self.sell_price = min(MAX_SELL_PRICE, self.sell_price + step)

    def lower_price(self, step: float = 0.25) -> None:
        self.sell_price = max(MIN_SELL_PRICE, self.sell_price - step)


@dataclass
class DayLedger:
    day: int = 1
    revenue:       float = 0.0
    restock_cost:  float = 0.0
    units_sold:    int   = 0
    units_crafted: int   = 0
    customers_served:  int = 0
    customers_lost:    int = 0

    @property
    def profit(self) -> float:
        return self.revenue - self.restock_cost

    @property
    def cogs_per_unit(self) -> float:
        raw = (RECIPE["lemons"] * DEFAULT_LEMON_PRICE +
               RECIPE["sugar"]  * DEFAULT_SUGAR_PRICE +
               RECIPE["ice"]    * DEFAULT_ICE_PRICE   +
               RECIPE["cups"]   * DEFAULT_CUP_PRICE)
        return raw


class EconomySystem:
    def __init__(self):
        self.cash:      float         = 10.0
        self.gems:      int           = 0
        self.inventory: Inventory     = Inventory()
        self.pricing:   PriceSettings = PriceSettings()
        self.ledger:    DayLedger     = DayLedger()
        self.history:   list          = []
        self.batch_multiplier: int    = 1
        self.ice_efficiency:   int    = 1
        self.price_tolerance:  float  = 0.0
        bus.subscribe(EVT_SALE_MADE, self._on_sale)

    def try_craft(self) -> bool:
        mult = self.batch_multiplier
        if not self.inventory.can_craft(mult):
            bus.emit(EVT_NOTIFICATION, text="Not enough ingredients!", color=COL_RED)
            return False
        inv = self.inventory
        r   = RECIPE
        inv.lemons   -= r["lemons"] * mult
        inv.sugar    -= r["sugar"]  * mult
        inv.ice      -= r["ice"]    * mult
        inv.cups     -= r["cups"]   * mult
        produced      = BATCH_YIELD * mult
        inv.lemonade  = min(MAX_LEMONADE, inv.lemonade + produced)
        self.ledger.units_crafted += produced
        bus.emit(EVT_CRAFT_DONE, quantity=produced)
        bus.emit(EVT_NOTIFICATION,
                 text=f"Crafted {produced} lemonade{'s' if produced>1 else ''}!",
                 color=COL_GREEN)
        return True

    def sell_one(self) -> Optional[float]:
        if self.inventory.lemonade <= 0:
            return None
        price = self.pricing.sell_price
        self.inventory.lemonade -= 1
        self.cash  += price
        self.ledger.revenue    += price
        self.ledger.units_sold += 1
        self.ledger.customers_served += 1
        bus.emit(EVT_SALE_MADE, amount=price)
        return price

    def restock(self, item: str, qty: int, use_gems: bool = False) -> bool:
        prices = {"lemons": DEFAULT_LEMON_PRICE, "sugar": DEFAULT_SUGAR_PRICE,
                  "ice": DEFAULT_ICE_PRICE, "cups": DEFAULT_CUP_PRICE}
        caps   = {"lemons": MAX_INV_LEMONS, "sugar": MAX_INV_SUGAR,
                  "ice": MAX_INV_ICE, "cups": MAX_INV_CUPS}
        if item not in prices:
            return False
        if use_gems:
            if self.gems < GEMS_PER_RESTOCK:
                bus.emit(EVT_NOTIFICATION, text="Not enough gems!", color=COL_RED)
                return False
            self.gems -= GEMS_PER_RESTOCK
            cost = 0.0
        else:
            cost = prices[item] * qty
            if self.cash < cost:
                bus.emit(EVT_NOTIFICATION, text="Not enough cash!", color=COL_RED)
                return False
            self.cash -= cost
            self.ledger.restock_cost += cost
        current = getattr(self.inventory, item)
        new_val  = min(caps[item], current + qty)
        actual   = new_val - current
        setattr(self.inventory, item, new_val)
        bus.emit(EVT_NOTIFICATION,
                 text=f"Restocked {actual} {item}  (${cost:.2f})", color=COL_BLUE)
        return True

    def end_day(self) -> DayLedger:
        closed = self.ledger
        self.history.append(closed)
        self.ledger = DayLedger(day=closed.day + 1)
        return closed

    def start_day(self, day: int) -> None:
        self.ledger.day = day

    def _on_sale(self, amount: float, **_):
        pass

    def add_gems(self, amount: int) -> None:
        self.gems += amount

    def spend_gems(self, amount: int, reason: str = "") -> bool:
        if self.gems < amount:
            bus.emit(EVT_NOTIFICATION, text="Not enough gems!", color=COL_RED)
            return False
        self.gems -= amount
        bus.emit(EVT_NOTIFICATION, text=f"Spent {amount} gems  {reason}", color=COL_XP_BAR)
        return True

    def customer_price_acceptance(self, weather_demand: float, reputation: float) -> bool:
        base_tolerance  = 2.00 + (reputation / 100.0) * 1.50
        base_tolerance += self.price_tolerance
        base_tolerance *= weather_demand
        return self.pricing.sell_price <= base_tolerance
