# ui/world.py
"""World rendering: sky, ground, road, stand, trees."""

import pygame, math, random
from core.constants import *


class WorldRenderer:
    def __init__(self, assets):
        self.assets = assets
        self._build_static()
        self._clouds = [
            {"x": random.uniform(0, SCREEN_W - PANEL_W),
             "y": random.uniform(80, 180),
             "speed": random.uniform(8, 20),
             "w": random.randint(60, 130),
             "h": random.randint(20, 40)}
            for _ in range(5)
        ]
        self._tree_xs = [120, 220, 340, 460, 680, 780]
        self._time: float = 0.0

    def _build_static(self):
        pass  # all drawn programmatically

    def update(self, dt: float, weather) -> None:
        self._time += dt
        speed_mult = 0.5 if weather.current == WEATHER_RAINY else 1.0
        for c in self._clouds:
            c["x"] += c["speed"] * dt * speed_mult
            if c["x"] > SCREEN_W:
                c["x"] = -c["w"]

    def draw(self, surface, weather):
        game_x = SCREEN_W - PANEL_W   # drawable world width

        # -- Sky gradient --
        sky_top = self._sky_color(weather)
        sky_bot = (sky_top[0]+30, sky_top[1]+20, sky_top[2]+10)
        for y in range(GROUND_Y):
            t   = y / GROUND_Y
            col = (min(255, max(0, int(sky_top[0]*(1-t)+sky_bot[0]*t))),
                   min(255, max(0, int(sky_top[1]*(1-t)+sky_bot[1]*t))),
                   min(255, max(0, int(sky_top[2]*(1-t)+sky_bot[2]*t))))
            pygame.draw.line(surface, col, (0, y), (game_x, y))

        # -- Clouds --
        for c in self._clouds:
            s = pygame.Surface((c["w"], c["h"]), pygame.SRCALPHA)
            alpha = 140 if weather.current != WEATHER_RAINY else 200
            pygame.draw.ellipse(s, (255,255,255,alpha), (0,0,c["w"],c["h"]))
            surface.blit(s, (int(c["x"]), int(c["y"])))

        # -- Ground --
        pygame.draw.rect(surface, COL_GROUND,
                         (0, GROUND_Y, game_x, SCREEN_H - GROUND_Y))
        # Grass texture lines
        for gx in range(0, game_x, 8):
            off = int(math.sin(gx * 0.3 + self._time * 1.5) * 2)
            pygame.draw.line(surface, (100, 170, 60),
                             (gx, GROUND_Y + off), (gx, GROUND_Y + 6 + off), 1)

        # -- Road --
        road_y = GROUND_Y + 10
        pygame.draw.rect(surface, COL_ROAD,
                         (0, road_y, game_x, 40))
        # Dashes
        dash_phase = int(self._time * 40) % 60
        for dx in range(-60 + dash_phase, game_x, 60):
            pygame.draw.rect(surface, (220, 210, 190),
                             (dx, road_y + 17, 36, 6))

        # -- Trees --
        for tx in self._tree_xs:
            if tx < game_x - 20:
                self._draw_tree(surface, tx, GROUND_Y)

        # -- Stand --
        stand_surf = self.assets.surf("stand")
        surface.blit(stand_surf, (STAND_X - 80, STAND_Y))

        # Stand sign text
        font = self.assets.font("sm")
        sign = font.render("LEMONADE", True, (180, 100, 20))
        surface.blit(sign, (STAND_X - 80 + 80 - sign.get_width()//2, STAND_Y + 10))

        # Interact hint zone (faint circle when player is near)
        hint = pygame.Surface((INTERACT_DIST*2, INTERACT_DIST*2), pygame.SRCALPHA)
        pygame.draw.circle(hint, (255, 255, 100, 20),
                           (INTERACT_DIST, INTERACT_DIST), INTERACT_DIST)
        surface.blit(hint, (STAND_X - INTERACT_DIST, STAND_Y - INTERACT_DIST + 60))

        # Rain overlay
        if weather.current == WEATHER_RAINY:
            self._draw_rain(surface, game_x)

    def _sky_color(self, weather):
        bases = {
            WEATHER_SUNNY:  (135, 206, 250),
            WEATHER_HOT:    (255, 165, 100),
            WEATHER_CLOUDY: (150, 160, 180),
            WEATHER_RAINY:  (100, 110, 140),
        }
        return bases.get(weather.current, (135, 206, 250))

    def _draw_tree(self, surface, x, base_y):
        # Trunk
        pygame.draw.rect(surface, (100, 65, 30), (x - 5, base_y - 50, 10, 50))
        # Foliage
        pygame.draw.circle(surface, (40, 140, 50), (x, base_y - 60), 28)
        pygame.draw.circle(surface, (50, 160, 60), (x - 10, base_y - 75), 20)
        pygame.draw.circle(surface, (50, 160, 60), (x + 12, base_y - 72), 18)

    def _draw_rain(self, surface, max_x):
        rs = pygame.Surface((max_x, SCREEN_H), pygame.SRCALPHA)
        t  = self._time
        for i in range(80):
            rx = int((i * 137 + t * 120) % max_x)
            ry = int((i * 97  + t * 300) % SCREEN_H)
            pygame.draw.line(rs, (180, 210, 255, 120),
                             (rx, ry), (rx - 2, ry + 14), 1)
        surface.blit(rs, (0, 0))
