# systems/customer.py
"""Customer spawning, AI state machine and serving logic."""

from __future__ import annotations
import random
import pygame
from core.constants import *
from core.events import (bus, EVT_CUSTOMER_HAPPY, EVT_CUSTOMER_LEFT,
                         EVT_NOTIFICATION)


class CustomerState:
    WALKING   = "walking"
    WAITING   = "waiting"
    SERVED    = "served"
    LEAVING   = "leaving"


class Customer:
    _id_counter = 0

    def __init__(self, surf: pygame.Surface):
        Customer._id_counter += 1
        self.id      = Customer._id_counter
        self.surf    = surf
        self.state   = CustomerState.WALKING
        self.patience: float = random.uniform(8.0, 18.0)   # seconds will wait
        self.wait_timer: float = 0.0
        self.speed   = random.uniform(1.5, 2.8)
        # Spawn off-screen left or right
        side = random.choice([-1, 1])
        self.x: float = -30.0 if side == -1 else SCREEN_W + 30.0
        self.y: float = float(GROUND_Y - 32)
        self.target_x: float = float(STAND_X + random.randint(-20, 20))
        self.alpha    = 255
        self.satisfied: bool = False

    def update(self, dt: float, economy, weather, progression) -> None:
        if self.state == CustomerState.WALKING:
            dx = self.target_x - self.x
            if abs(dx) < 2:
                self.state = CustomerState.WAITING
            else:
                self.x += self.speed * (1 if dx > 0 else -1)

        elif self.state == CustomerState.WAITING:
            self.wait_timer += dt
            if self.wait_timer >= self.patience:
                self._leave("timeout")

        elif self.state in (CustomerState.SERVED, CustomerState.LEAVING):
            # Walk off screen
            self.x += self.speed * 1.5
            self.alpha = max(0, self.alpha - 3)

    def serve(self, economy, weather, progression) -> bool:
        """Returns True if customer accepts and buys."""
        accepted = economy.customer_price_acceptance(
            weather.demand_multiplier, progression.reputation)
        if accepted and economy.inventory.lemonade > 0:
            economy.sell_one()
            self.satisfied = True
            self.state     = CustomerState.SERVED
            bus.emit(EVT_CUSTOMER_HAPPY, customer=self)
            return True
        elif economy.inventory.lemonade <= 0:
            self._leave("no_stock")
        else:
            self._leave("price_too_high")
        return False

    def _leave(self, reason: str) -> None:
        self.state     = CustomerState.LEAVING
        self.satisfied = False
        bus.emit(EVT_CUSTOMER_LEFT, customer=self, reason=reason)
        if reason == "no_stock":
            bus.emit(EVT_NOTIFICATION, text="Customer left — out of stock!", color=COL_RED)
        elif reason == "price_too_high":
            bus.emit(EVT_NOTIFICATION, text="Too pricey! Customer left.", color=(220, 140, 30))

    @property
    def is_done(self) -> bool:
        return self.alpha <= 0 or (
            self.state in (CustomerState.SERVED, CustomerState.LEAVING) and
            (self.x > SCREEN_W + 40 or self.x < -40)
        )

    def draw(self, surface: pygame.Surface, assets) -> None:
        s = self.surf.copy()
        s.set_alpha(self.alpha)
        surface.blit(s, (int(self.x), int(self.y)))

        # Patience bar above customer while waiting
        if self.state == CustomerState.WAITING:
            bar_w = 28
            ratio = 1.0 - self.wait_timer / self.patience
            pygame.draw.rect(surface, COL_RED,
                             (int(self.x) - 4, int(self.y) - 8, bar_w, 5))
            pygame.draw.rect(surface, COL_GREEN,
                             (int(self.x) - 4, int(self.y) - 8,
                              int(bar_w * ratio), 5))


class CustomerSystem:
    def __init__(self, assets):
        self.assets    = assets
        self.customers: list[Customer] = []
        self.spawn_timer: float = 0.0
        self.base_interval: float = CUSTOMER_SPAWN_INTERVAL

    def _spawn_interval(self, progression) -> float:
        bonus = 0.0
        if "marketing_flyers" in progression.unlocked_upgrades:
            bonus = UPGRADES["marketing_flyers"]["value"]
        return self.base_interval / (1.0 + bonus)

    def update(self, dt: float, economy, weather, progression) -> None:
        # Spawn
        self.spawn_timer += dt
        interval = self._spawn_interval(progression) / weather.demand_multiplier
        if self.spawn_timer >= interval:
            self.spawn_timer = 0.0
            if len(self.customers) < 6:   # max 6 on screen
                self.customers.append(
                    Customer(self.assets.surf("customer")))

        # Update + auto-serve customers at stand
        for c in self.customers:
            c.update(dt, economy, weather, progression)
            if c.state == CustomerState.WAITING:
                dist = abs(c.x - STAND_X)
                if dist < INTERACT_DIST * 0.6:
                    # auto-serve if player is near, else wait for player click
                    pass

        # Auto-serve via upgrade
        if "second_stand" in progression.unlocked_upgrades:
            waiting = [c for c in self.customers
                       if c.state == CustomerState.WAITING]
            if waiting:
                waiting[0].serve(economy, weather, progression)

        # Prune finished customers
        self.customers = [c for c in self.customers if not c.is_done]

    def serve_nearest(self, px: float, economy, weather, progression) -> bool:
        """Player manually serves nearest waiting customer."""
        waiting = [c for c in self.customers
                   if c.state == CustomerState.WAITING]
        if not waiting:
            return False
        nearest = min(waiting, key=lambda c: abs(c.x - px))
        return nearest.serve(economy, weather, progression)

    def draw(self, surface: pygame.Surface) -> None:
        for c in self.customers:
            c.draw(surface, self.assets)
