# systems/notification.py
"""Floating toast notifications."""

from __future__ import annotations
import pygame
from core.constants import *
from core.events import bus, EVT_NOTIFICATION


class Toast:
    def __init__(self, text: str, color: tuple, font):
        self.text   = text
        self.color  = color
        self.font   = font
        self.life   = 2.8      # seconds
        self.timer  = 0.0
        self.y_off  = 0.0      # rises upward

    @property
    def alpha(self) -> int:
        t = self.timer / self.life
        if t < 0.15:
            return int(255 * (t / 0.15))
        if t > 0.7:
            return int(255 * (1.0 - (t - 0.7) / 0.3))
        return 255

    def update(self, dt: float) -> None:
        self.timer  += dt
        self.y_off  -= 28 * dt   # float upward

    @property
    def is_done(self) -> bool:
        return self.timer >= self.life

    def draw(self, surface: pygame.Surface, base_y: int, index: int) -> None:
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        x = SCREEN_W // 2 - text_surf.get_width() // 2
        y = base_y + int(self.y_off) - index * 22
        surface.blit(text_surf, (x, y))


class NotificationSystem:
    def __init__(self, assets):
        self.font   = assets.font("md")
        self.toasts: list[Toast] = []
        bus.subscribe(EVT_NOTIFICATION, self._on_notification)

    def _on_notification(self, text: str, color: tuple, **_):
        self.toasts.append(Toast(text, color, self.font))
        if len(self.toasts) > 6:
            self.toasts.pop(0)

    def update(self, dt: float) -> None:
        for t in self.toasts:
            t.update(dt)
        self.toasts = [t for t in self.toasts if not t.is_done]

    def draw(self, surface: pygame.Surface) -> None:
        base_y = SCREEN_H - HUD_H - 60
        for i, t in enumerate(reversed(self.toasts)):
            t.draw(surface, base_y, i)
