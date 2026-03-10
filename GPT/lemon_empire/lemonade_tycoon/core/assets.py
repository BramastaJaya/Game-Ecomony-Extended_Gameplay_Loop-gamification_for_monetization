# core/assets.py
"""Centralised asset manager. Creates pixel-art surfaces programmatically
so the game runs with zero external files."""

import pygame
from core.constants import *


class Assets:
    _instance = None

    @classmethod
    def get(cls) -> "Assets":
        if cls._instance is None:
            cls._instance = Assets()
        return cls._instance

    def __init__(self):
        self.fonts: dict[str, pygame.font.Font] = {}
        self.surfaces: dict[str, pygame.Surface] = {}
        self._load_fonts()
        self._build_surfaces()

    # ------------------------------------------------------------------
    # Fonts
    # ------------------------------------------------------------------
    def _load_fonts(self):
        self.fonts["sm"]  = pygame.font.SysFont("monospace", 13, bold=False)
        self.fonts["md"]  = pygame.font.SysFont("monospace", 16, bold=True)
        self.fonts["lg"]  = pygame.font.SysFont("monospace", 22, bold=True)
        self.fonts["xl"]  = pygame.font.SysFont("monospace", 32, bold=True)
        self.fonts["hud"] = pygame.font.SysFont("monospace", 14, bold=True)

    def font(self, size: str) -> pygame.font.Font:
        return self.fonts.get(size, self.fonts["md"])

    # ------------------------------------------------------------------
    # Programmatic pixel art surfaces
    # ------------------------------------------------------------------
    def _build_surfaces(self):
        self.surfaces["player"]   = self._make_player()
        self.surfaces["customer"] = self._make_customer()
        self.surfaces["stand"]    = self._make_stand()
        self.surfaces["lemon"]    = self._make_lemon()
        self.surfaces["coin"]     = self._make_coin()
        self.surfaces["gem"]      = self._make_gem()

    def _make_player(self) -> pygame.Surface:
        s = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
        # body
        pygame.draw.rect(s, COL_PLAYER, (4, 14, 16, 20))
        # head
        pygame.draw.ellipse(s, (255, 220, 180), (5, 0, 14, 14))
        # hat (lemon yellow)
        pygame.draw.rect(s, (255, 230, 50), (4, 0, 16, 6))
        # legs
        pygame.draw.rect(s, (50, 80, 150), (4, 34, 6, 4))
        pygame.draw.rect(s, (50, 80, 150), (14, 34, 6, 4))
        return s

    def _make_customer(self) -> pygame.Surface:
        s = pygame.Surface((20, 32), pygame.SRCALPHA)
        pygame.draw.rect(s, COL_CUSTOMER, (3, 10, 14, 18))
        pygame.draw.ellipse(s, (255, 210, 170), (4, 0, 12, 12))
        pygame.draw.rect(s, (120, 60, 40), (3, 28, 5, 4))
        pygame.draw.rect(s, (120, 60, 40), (12, 28, 5, 4))
        return s

    def _make_stand(self) -> pygame.Surface:
        w, h = 160, 100
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        # base counter
        pygame.draw.rect(s, COL_STAND_BODY, (0, 40, w, 60))
        pygame.draw.rect(s, (200, 170, 50), (0, 40, w, 8))
        # roof
        pts = [(0, 40), (w, 40), (w - 10, 0), (10, 0)]
        pygame.draw.polygon(s, COL_STAND_ROOF, pts)
        # sign
        pygame.draw.rect(s, (255, 255, 200), (20, 8, w - 40, 20))
        return s

    def _make_lemon(self) -> pygame.Surface:
        s = pygame.Surface((18, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (255, 230, 40), (1, 2, 14, 12))
        pygame.draw.circle(s, (255, 200, 20), (14, 4), 3)
        return s

    def _make_coin(self) -> pygame.Surface:
        s = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(s, COL_GOLD, (7, 7), 7)
        pygame.draw.circle(s, (220, 160, 20), (7, 7), 5)
        return s

    def _make_gem(self) -> pygame.Surface:
        s = pygame.Surface((14, 14), pygame.SRCALPHA)
        pts = [(7, 0), (14, 5), (11, 14), (3, 14), (0, 5)]
        pygame.draw.polygon(s, (100, 200, 255), pts)
        pygame.draw.polygon(s, (180, 230, 255), [(7, 2), (12, 6), (9, 12)], 0)
        return s

    def surf(self, name: str) -> pygame.Surface:
        return self.surfaces.get(name)
