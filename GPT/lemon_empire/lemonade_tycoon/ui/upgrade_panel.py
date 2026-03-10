# ui/upgrade_panel.py
"""Full-screen upgrade shop overlay."""

import pygame
from core.constants import *
from ui.side_panel import Button


class UpgradePanel:
    def __init__(self, assets):
        self.assets  = assets
        self.visible = False
        self.buttons: list = []
        self.close_btn = Button((SCREEN_W//2 + 200, SCREEN_H//2 - 180, 80, 30),
                                 "Close", (120,50,50))

    def _rebuild_buttons(self, progression):
        self.buttons = []
        avail = progression.available_upgrades()
        for i, (uid, data) in enumerate(avail):
            y = SCREEN_H//2 - 160 + i * 56
            can = progression.can_afford_upgrade(uid)
            color = COL_BTN if can else COL_BTN_DIS
            btn = Button((SCREEN_W//2 - 200, y, 380, 46),
                          f"[{data['requires_level']}] {data['description']}  ${data['cost']:.0f}",
                          color)
            btn.enabled = can
            btn._uid = uid
            self.buttons.append(btn)

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event, progression) -> None:
        if not self.visible:
            return
        if self.close_btn.is_clicked(event):
            self.visible = False
            return
        self._rebuild_buttons(progression)
        for btn in self.buttons:
            if btn.is_clicked(event):
                progression.buy_upgrade(btn._uid)
                self._rebuild_buttons(progression)

    def draw(self, surface, assets, progression):
        if not self.visible:
            return
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font_lg = assets.font("lg")
        font_md = assets.font("md")
        font_sm = assets.font("sm")

        title = font_lg.render("UPGRADE SHOP", True, COL_GOLD)
        surface.blit(title, (SCREEN_W//2 - title.get_width()//2, SCREEN_H//2 - 200))

        self._rebuild_buttons(progression)
        if not self.buttons:
            t = font_md.render("All upgrades purchased!", True, COL_GREEN)
            surface.blit(t, (SCREEN_W//2 - t.get_width()//2, SCREEN_H//2))
        for btn in self.buttons:
            btn.draw(surface, assets)
            uid = btn._uid
            data = UPGRADES[uid]
            req_t = font_sm.render(
                f"Requires Lv {data['requires_level']}",
                True, COL_XP_BAR if progression.level >= data['requires_level'] else COL_RED)
            surface.blit(req_t, (btn.rect.right + 8, btn.rect.centery - 6))

        self.close_btn.draw(surface, assets)
