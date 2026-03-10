# systems/progression.py
"""XP, levelling, reputation and upgrade system."""

from __future__ import annotations
from core.constants import *
from core.events import (bus, EVT_CRAFT_DONE, EVT_SALE_MADE,
                         EVT_CUSTOMER_HAPPY, EVT_CUSTOMER_LEFT,
                         EVT_LEVEL_UP, EVT_UPGRADE_BOUGHT, EVT_NOTIFICATION)


class ProgressionSystem:
    def __init__(self, economy):
        self.economy    = economy
        self.xp:        int   = 0
        self.level:     int   = 1
        self.reputation: float = 50.0
        self.unlocked_upgrades: set = set()

        bus.subscribe(EVT_CRAFT_DONE,     self._on_craft)
        bus.subscribe(EVT_SALE_MADE,      self._on_sale)
        bus.subscribe(EVT_CUSTOMER_HAPPY, self._on_happy)
        bus.subscribe(EVT_CUSTOMER_LEFT,  self._on_left)

    # ------------------------------------------------------------------
    def xp_for_next_level(self) -> int:
        return XP_LEVEL_CURVE * self.level

    def xp_progress(self) -> float:
        return self.xp / self.xp_for_next_level()

    def _add_xp(self, amount: int) -> None:
        self.xp += amount
        while self.xp >= self.xp_for_next_level():
            self.xp -= self.xp_for_next_level()
            self.level += 1
            bus.emit(EVT_LEVEL_UP, new_level=self.level)
            bus.emit(EVT_NOTIFICATION,
                     text=f"LEVEL UP!  Now level {self.level}",
                     color=COL_GOLD)

    def _clamp_rep(self) -> None:
        self.reputation = max(MIN_REPUTATION, min(MAX_REPUTATION, self.reputation))

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_craft(self, quantity: int, **_):
        self._add_xp(XP_PER_CRAFT * quantity)

    def _on_sale(self, amount: float, **_):
        self._add_xp(XP_PER_SALE)

    def _on_happy(self, **_):
        self.reputation += REP_PER_HAPPY
        self._clamp_rep()

    def _on_left(self, reason: str = "", **_):
        if reason in ("no_stock", "price_too_high"):
            self.reputation += REP_PER_UNHAPPY
            self._clamp_rep()

    # ------------------------------------------------------------------
    # Upgrade shop
    # ------------------------------------------------------------------
    def available_upgrades(self) -> list:
        result = []
        for uid, data in UPGRADES.items():
            if uid not in self.unlocked_upgrades:
                result.append((uid, data))
        return result

    def can_afford_upgrade(self, uid: str) -> bool:
        data = UPGRADES.get(uid)
        if not data:
            return False
        return (self.economy.cash >= data["cost"] and
                self.level >= data["requires_level"])

    def buy_upgrade(self, uid: str) -> bool:
        if uid in self.unlocked_upgrades:
            return False
        data = UPGRADES.get(uid)
        if not data:
            return False
        if not self.can_afford_upgrade(uid):
            bus.emit(EVT_NOTIFICATION,
                     text=f"Need lvl {data['requires_level']} & ${data['cost']:.0f}",
                     color=COL_RED)
            return False

        self.economy.cash -= data["cost"]
        self.unlocked_upgrades.add(uid)
        self._apply_upgrade(uid, data)
        bus.emit(EVT_UPGRADE_BOUGHT, upgrade_id=uid)
        bus.emit(EVT_NOTIFICATION,
                 text=f"Upgrade: {data['description']}", color=COL_GOLD)
        return True

    def _apply_upgrade(self, uid: str, data: dict) -> None:
        effect = data["effect"]
        val    = data["value"]
        eco    = self.economy
        if effect == "batch_multiplier":
            eco.batch_multiplier = val
        elif effect == "ice_efficiency":
            eco.ice_efficiency = val
        elif effect == "spawn_bonus":
            pass   # CustomerSystem reads this via progression ref
        elif effect == "price_tolerance":
            eco.price_tolerance += val
        elif effect == "auto_serve":
            pass   # GameLoop reads this
