# ==============================================================================
# CUSTOMER SYSTEM
# Demand simulation, customer AI, weather-based modifiers
# ==============================================================================

import pygame
import random
import math
from data.constants import (
    CUSTOMER_BASE_RATE, CUSTOMER_PRICE_SWEET_SPOT, CUSTOMER_PRICE_TOLERANCE,
    CUSTOMER_WEATHER_MULTIPLIER, GAME_MINUTE_FRAMES, TILE,
    C_WHITE, C_RED, C_GREEN, C_DARK,
)


WEATHERS = ["sunny", "cloudy", "hot", "rainy", "perfect"]
WEATHER_ICONS = {
    "sunny":   "☀",
    "cloudy":  "☁",
    "hot":     "🌡",
    "rainy":   "🌧",
    "perfect": "✨",
}

# Customer visual palette  (skin tones + shirt colors)
CUSTOMER_SKINS  = [(255, 210, 170), (200, 150, 100), (140, 90, 50), (255, 230, 190)]
CUSTOMER_SHIRTS = [(200, 80, 80), (80, 120, 200), (80, 180, 80), (200, 180, 50),
                   (150, 80, 200), (200, 120, 50)]


class WeatherSystem:
    """
    Drives day-by-day weather variation.
    Weather multipliers directly affect customer demand.
    """

    def __init__(self):
        self.current = "sunny"
        self.next    = "sunny"
        self._day    = 0

    def new_day(self, day: int):
        self._day    = day
        self.current = self.next
        # Tease tomorrow's weather (80% random, 20% same)
        self.next    = random.choice(WEATHERS) if random.random() < 0.8 else self.current

    def multiplier(self, upgrades_owned: list[str]) -> float:
        base = CUSTOMER_WEATHER_MULTIPLIER.get(self.current, 1.0)
        # Umbrella upgrade bonus on hot days
        if self.current == "hot" and "umbrella" in upgrades_owned:
            base += 0.2
        return base

    def icon(self) -> str:
        return WEATHER_ICONS.get(self.current, "?")


def demand_multiplier(price: float) -> float:
    """
    Demand curve:
    - At sweet spot price → 1.0
    - Below sweet spot    → slightly increased (bargain hunters)
    - Above sweet spot    → decreasing toward 0 at tolerance ceiling
    """
    if price <= CUSTOMER_PRICE_SWEET_SPOT:
        # Below or at sweet spot: gentle bonus
        return 1.0 + 0.2 * (1 - price / CUSTOMER_PRICE_SWEET_SPOT)
    elif price <= CUSTOMER_PRICE_TOLERANCE:
        ratio = (price - CUSTOMER_PRICE_SWEET_SPOT) / (CUSTOMER_PRICE_TOLERANCE - CUSTOMER_PRICE_SWEET_SPOT)
        return max(0.0, 1.0 - ratio ** 1.5)
    else:
        return 0.0


class Customer:
    """
    Autonomous customer NPC that walks to the stand, buys, and leaves.
    State machine: SPAWNING → WALKING → WAITING → SERVED/REJECTED → LEAVING
    """

    SPAWN_DISTANCE = 500   # px off-screen

    STATE_WALK    = "walk"
    STATE_WAIT    = "wait"
    STATE_SERVED  = "served"
    STATE_LEAVE   = "leave"
    STATE_REJECT  = "reject"

    SIZE = (16, 24)

    def __init__(self, stand_pos: tuple[int, int], spawn_side: str = "right"):
        # Spawn off-screen
        if spawn_side == "right":
            sx = stand_pos[0] + self.SPAWN_DISTANCE + random.randint(0, 100)
        else:
            sx = stand_pos[0] - self.SPAWN_DISTANCE - random.randint(0, 100)
        sy = stand_pos[1] + random.randint(-4, 8)

        self.rect       = pygame.Rect(sx, sy, *self.SIZE)
        self.stand_pos  = stand_pos
        self.state      = self.STATE_WALK
        self.speed      = random.uniform(1.2, 2.2)
        self.wait_timer = random.randint(40, 90)
        self.dead       = False

        # Visual
        self.skin_color  = random.choice(CUSTOMER_SKINS)
        self.shirt_color = random.choice(CUSTOMER_SHIRTS)
        self.spawn_side  = spawn_side

        # Reaction bubble
        self.bubble_text  = ""
        self.bubble_timer = 0

    def update(self, stand_rect: pygame.Rect, on_sale_callback, on_reject_callback):
        if self.state == self.STATE_WALK:
            # Walk toward stand
            tx = self.stand_pos[0] - self.SIZE[0] // 2
            ty = self.stand_pos[1]
            dx = tx - self.rect.x
            dy = ty - self.rect.y
            dist = max(1, math.hypot(dx, dy))
            self.rect.x += int(self.speed * dx / dist)
            self.rect.y += int(self.speed * dy / dist)
            if dist < 10:
                self.state = self.STATE_WAIT

        elif self.state == self.STATE_WAIT:
            self.wait_timer -= 1
            if self.wait_timer <= 0:
                # Attempt purchase
                result = on_sale_callback()
                if result:
                    self.state        = self.STATE_SERVED
                    self.bubble_text  = random.choice(["Yum!", "Refreshing!", "😊", "Delicious!"])
                    self.bubble_timer = 50
                else:
                    self.state        = self.STATE_REJECT
                    on_reject_callback()
                    self.bubble_text  = random.choice(["Sold out!", "😢", "Next time..."])
                    self.bubble_timer = 50

        elif self.state in (self.STATE_SERVED, self.STATE_REJECT):
            self.bubble_timer -= 1
            if self.bubble_timer <= 0:
                self.state = self.STATE_LEAVE

        elif self.state == self.STATE_LEAVE:
            # Walk off-screen in origin direction
            if self.spawn_side == "right":
                self.rect.x += int(self.speed * 1.5)
                if self.rect.x > self.stand_pos[0] + self.SPAWN_DISTANCE + 200:
                    self.dead = True
            else:
                self.rect.x -= int(self.speed * 1.5)
                if self.rect.x < self.stand_pos[0] - self.SPAWN_DISTANCE - 200:
                    self.dead = True

        if self.bubble_timer > 0:
            self.bubble_timer -= 1

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int], font: pygame.font.Font):
        ox, oy = camera_offset
        dx = self.rect.x - ox
        dy = self.rect.y - oy

        # Body
        pygame.draw.rect(surface, self.shirt_color, (dx + 2, dy + 10, 12, 10))
        # Head
        pygame.draw.rect(surface, self.skin_color,  (dx + 3, dy,      10, 10))
        # Legs
        pygame.draw.rect(surface, (60, 60, 100),    (dx + 2, dy + 20,  5,  4))
        pygame.draw.rect(surface, (60, 60, 100),    (dx + 9, dy + 20,  5,  4))

        # Bubble
        if self.bubble_timer > 0 and self.bubble_text:
            alpha   = min(255, self.bubble_timer * 5)
            txt     = font.render(self.bubble_text, True, C_DARK)
            bubble  = pygame.Surface((txt.get_width() + 8, txt.get_height() + 4), pygame.SRCALPHA)
            bubble.fill((255, 255, 255, 200))
            bubble.blit(txt, (4, 2))
            bubble.set_alpha(alpha)
            surface.blit(bubble, (dx - 10, dy - 20))


class CustomerManager:
    """
    Spawns customers based on demand calculations.
    Mediates between customers and the Economy system.
    """

    MAX_CUSTOMERS = 15

    def __init__(self, stand_pos: tuple[int, int], weather: WeatherSystem):
        self.stand_pos   = stand_pos
        self.weather     = weather
        self.customers:  list[Customer] = []
        self.spawn_timer = 0
        self.spawn_interval = GAME_MINUTE_FRAMES  # recalculated each minute
        self.rejected_today = 0
        self.served_today   = 0

    def _compute_spawn_interval(self, price: float, upgrades: list[str]) -> float:
        """
        Lower interval = more frequent spawns = higher demand.
        Accounts for price, weather, and upgrade bonuses.
        """
        demand   = demand_multiplier(price)
        weather  = self.weather.multiplier(upgrades)
        rate_bonus = 1.0
        if "sign"  in upgrades:  rate_bonus += 0.15
        if "cart"  in upgrades:  rate_bonus += 0.25

        effective_rate = CUSTOMER_BASE_RATE * demand * weather * rate_bonus
        if effective_rate <= 0:
            return 99999   # nobody comes

        # customers per minute → frames per customer
        return GAME_MINUTE_FRAMES / effective_rate

    def update(self, price: float, upgrades: list[str],
               on_sale_callback, on_reject_callback):

        self.spawn_interval = self._compute_spawn_interval(price, upgrades)
        self.spawn_timer   += 1

        # Spawn
        if (self.spawn_timer >= self.spawn_interval
                and len(self.customers) < self.MAX_CUSTOMERS):
            self.spawn_timer = 0
            side = random.choice(["left", "right"])
            c    = Customer(self.stand_pos, side)
            self.customers.append(c)

        # Update each customer
        for c in self.customers:
            c.update(
                pygame.Rect(self.stand_pos[0] - 8, self.stand_pos[1] - 8, 16, 16),
                on_sale_callback,
                on_reject_callback,
            )

        # Purge dead customers
        self.customers = [c for c in self.customers if not c.dead]

    def new_day(self):
        self.rejected_today = 0
        self.served_today   = 0
        self.customers.clear()
        self.spawn_timer = 0

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int], font: pygame.font.Font):
        for c in self.customers:
            c.draw(surface, camera_offset, font)
