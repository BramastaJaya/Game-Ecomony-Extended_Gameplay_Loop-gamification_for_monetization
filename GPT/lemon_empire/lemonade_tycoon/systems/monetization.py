# systems/monetization.py
"""Soft-currency (gems) monetization: IAP simulation, gem sinks, daily rewards."""

from __future__ import annotations
import pygame
from core.constants import *
from core.events import bus, EVT_IAP_PURCHASE, EVT_GEM_SPEND, EVT_NOTIFICATION


class DailyReward:
    """Login streak tracker with escalating gem rewards."""
    REWARDS = [5, 5, 10, 10, 15, 20, 30]   # gems per streak day

    def __init__(self):
        self.streak:       int   = 0
        self.claimed_today: bool = False

    def claim(self, economy) -> int:
        if self.claimed_today:
            return 0
        reward = self.REWARDS[min(self.streak, len(self.REWARDS) - 1)]
        economy.add_gems(reward)
        self.claimed_today = True
        self.streak       += 1
        bus.emit(EVT_NOTIFICATION,
                 text=f"Daily reward: +{reward} gems! (Day {self.streak})",
                 color=COL_GOLD)
        return reward

    def reset_day(self) -> None:
        self.claimed_today = False


class MonetizationSystem:
    """Handles IAP packs (simulated), gem sinks, and daily reward."""

    def __init__(self, economy):
        self.economy     = economy
        self.daily       = DailyReward()
        self.iap_packs   = IAP_GEMS_PACKS
        self._double_day_active: bool  = False
        self._double_day_timer: float  = 0.0

    # ------------------------------------------------------------------
    # IAP simulation (in real game: call platform billing API)
    # ------------------------------------------------------------------
    def simulate_iap(self, pack_index: int) -> None:
        if pack_index < 0 or pack_index >= len(self.iap_packs):
            return
        pack = self.iap_packs[pack_index]
        self.economy.add_gems(pack["gems"])
        bus.emit(EVT_IAP_PURCHASE, pack=pack)
        bus.emit(EVT_NOTIFICATION,
                 text=f"Purchased {pack['gems']} gems! (${pack['cost_usd']})",
                 color=COL_GOLD)

    # ------------------------------------------------------------------
    # Gem sinks
    # ------------------------------------------------------------------
    def use_emergency_restock(self, item: str) -> bool:
        """Spend gems to instantly restock 10 units without cash."""
        return self.economy.restock(item, qty=10, use_gems=True)

    def use_skip_night(self) -> bool:
        """Spend gems to fast-forward to next morning."""
        ok = self.economy.spend_gems(GEMS_SKIP_NIGHT, "(skip night)")
        if ok:
            bus.emit(EVT_NOTIFICATION, text="Skipped to next morning!", color=COL_XP_BAR)
        return ok

    def use_double_day(self) -> bool:
        """Spend gems to double earnings for current day session."""
        if self._double_day_active:
            bus.emit(EVT_NOTIFICATION, text="Already active!", color=COL_RED)
            return False
        ok = self.economy.spend_gems(GEMS_DOUBLE_DAY, "(double day)")
        if ok:
            self._double_day_active = True
            self._double_day_timer  = DAY_DURATION
            bus.emit(EVT_NOTIFICATION, text="2x Earnings ACTIVE!", color=COL_GOLD)
        return ok

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        if self._double_day_active:
            self._double_day_timer -= dt
            if self._double_day_timer <= 0:
                self._double_day_active = False
                bus.emit(EVT_NOTIFICATION, text="2x Earnings ended.", color=COL_TEXT_DARK)

    @property
    def double_day_active(self) -> bool:
        return self._double_day_active

    def on_new_day(self) -> None:
        self.daily.reset_day()
