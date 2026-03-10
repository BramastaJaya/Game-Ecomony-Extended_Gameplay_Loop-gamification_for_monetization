# ui/end_of_day.py
"""End-of-day summary overlay."""

import pygame
from core.constants import *
from ui.side_panel import Button


class EndOfDayPanel:
    def __init__(self, assets):
        self.assets  = assets
        self.visible = False
        self.ledger  = None
        self.btn_next = Button(
            (SCREEN_W//2 - 70, SCREEN_H//2 + 110, 140, 40),
            "Next Day", COL_BTN)

    def show(self, ledger):
        self.visible = True
        self.ledger  = ledger

    def handle_event(self, event) -> bool:
        """Returns True when player confirms next day."""
        if self.visible and self.btn_next.is_clicked(event):
            self.visible = False
            return True
        return False

    def draw(self, surface, assets):
        if not self.visible or not self.ledger:
            return
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        font_xl = assets.font("xl")
        font_lg = assets.font("lg")
        font_md = assets.font("md")

        cx = SCREEN_W // 2
        y  = SCREEN_H // 2 - 140

        title = font_xl.render(f"Day {self.ledger.day} Results", True, COL_GOLD)
        surface.blit(title, (cx - title.get_width()//2, y)); y += 50

        rows = [
            (f"Revenue",       f"${self.ledger.revenue:.2f}",     COL_GREEN),
            (f"Restock Cost",  f"${self.ledger.restock_cost:.2f}", COL_RED),
            (f"Net Profit",    f"${self.ledger.profit:.2f}",
             COL_GREEN if self.ledger.profit >= 0 else COL_RED),
            ("",               "",                                   COL_TEXT_LIGHT),
            (f"Cups Sold",     str(self.ledger.units_sold),         COL_TEXT_LIGHT),
            (f"Cups Crafted",  str(self.ledger.units_crafted),      COL_TEXT_LIGHT),
            (f"Served",        str(self.ledger.customers_served),   COL_TEXT_LIGHT),
            (f"Lost",          str(self.ledger.customers_lost),     COL_RED),
        ]

        for label, value, color in rows:
            if not label:
                y += 10
                continue
            lt = font_md.render(label + ":", True, (180,180,180))
            vt = font_md.render(value,      True, color)
            surface.blit(lt, (cx - 160, y))
            surface.blit(vt, (cx +  60, y))
            y += 24

        self.btn_next.draw(surface, assets)
