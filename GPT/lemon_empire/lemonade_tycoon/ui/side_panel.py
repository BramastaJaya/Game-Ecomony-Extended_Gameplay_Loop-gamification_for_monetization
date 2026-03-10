# ui/side_panel.py
"""Right-side action panel: inventory, price controls, craft button, restock."""

import pygame
from core.constants import *


class Button:
    def __init__(self, rect, label, color=COL_BTN, font=None):
        self.rect  = pygame.Rect(rect)
        self.label = label
        self.color = color
        self._font = font
        self.enabled = True

    def draw(self, surface, assets):
        font  = self._font or assets.font("sm")
        color = self.color if self.enabled else COL_BTN_DIS
        mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse) and self.enabled
        bg    = tuple(min(255, c + 20) for c in color) if hover else color
        pygame.draw.rect(surface, bg, self.rect, 0, 5)
        pygame.draw.rect(surface, COL_TEXT_LIGHT, self.rect, 1, 5)
        txt = font.render(self.label, True, COL_TEXT_LIGHT)
        surface.blit(txt, (self.rect.centerx - txt.get_width()//2,
                           self.rect.centery - txt.get_height()//2))

    def is_clicked(self, event) -> bool:
        return (self.enabled and
                event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


class SidePanel:
    """Inventory display + action buttons."""

    def __init__(self, assets):
        self.assets = assets
        px = PANEL_X + 10
        y  = HUD_H + 10

        # Craft button
        self.btn_craft = Button((px, y, PANEL_W - 20, 36), "CRAFT  [C]", COL_BTN)
        y += 44

        # Price controls
        self.btn_price_up   = Button((px,             y, (PANEL_W-30)//2, 30), "Price +", (80,100,160))
        self.btn_price_down = Button((px+(PANEL_W-30)//2+10, y, (PANEL_W-30)//2, 30), "Price -", (140,80,80))
        y += 38

        # Restock buttons (10 units each)
        self.restock_btns: dict = {}
        for item in ["lemons", "sugar", "ice", "cups"]:
            self.restock_btns[item] = Button((px, y, PANEL_W - 20, 26),
                                              f"Buy {item} x10", (60,70,100))
            y += 30

        y += 8
        # Gem spend buttons
        self.btn_skip_night   = Button((px, y, PANEL_W-20, 26),
                                       f"Skip Night ({GEMS_SKIP_NIGHT}gems)", (80,60,130))
        y += 30
        self.btn_double_day   = Button((px, y, PANEL_W-20, 26),
                                       f"2x Day ({GEMS_DOUBLE_DAY}gems)", (100,60,130))
        y += 30
        self.btn_daily_reward = Button((px, y, PANEL_W-20, 26), "Daily Reward", (130,100,30))
        y += 38

        # Upgrade shop toggle
        self.btn_upgrades = Button((px, y, PANEL_W-20, 32), "UPGRADES [U]",
                                    (50, 90, 140))
        self._y_after_buttons = y + 40

    def handle_event(self, event, economy, progression, monetization, game_loop) -> None:
        if self.btn_craft.is_clicked(event):
            game_loop.player_craft()

        if self.btn_price_up.is_clicked(event):
            economy.pricing.raise_price()

        if self.btn_price_down.is_clicked(event):
            economy.pricing.lower_price()

        for item, btn in self.restock_btns.items():
            if btn.is_clicked(event):
                economy.restock(item, 10)

        if self.btn_skip_night.is_clicked(event):
            monetization.use_skip_night()
            game_loop.force_day_end()

        if self.btn_double_day.is_clicked(event):
            monetization.use_double_day()

        if self.btn_daily_reward.is_clicked(event):
            monetization.daily.claim(economy)

        if self.btn_upgrades.is_clicked(event):
            game_loop.toggle_upgrade_panel()

    def draw(self, surface, assets, economy, progression, monetization):
        # Panel background — full height including bottom strip
        pygame.draw.rect(surface, COL_PANEL,
                         (PANEL_X, 0, PANEL_W, SCREEN_H))
        pygame.draw.rect(surface, COL_PANEL,
                         (PANEL_X, HUD_H, PANEL_W, SCREEN_H - HUD_H))
        pygame.draw.line(surface, COL_GOLD,
                         (PANEL_X, HUD_H), (PANEL_X, SCREEN_H), 2)

        font_md = assets.font("md")
        font_sm = assets.font("sm")

        px  = PANEL_X + 10          # left margin inside panel
        pw  = PANEL_W - 20          # usable width
        y   = HUD_H + 6             # running y cursor

        # ── helper: draw a section divider label ──────────────────────
        def section(label):
            nonlocal y
            y += 6
            pygame.draw.line(surface, (70, 70, 100),
                             (px, y + 8), (px + pw, y + 8), 1)
            t = font_sm.render(label, True, COL_GOLD)
            surface.blit(t, (px, y))
            y += 18

        # ── CRAFT ─────────────────────────────────────────────────────
        section("── CRAFTING ──")
        self.btn_craft.rect.update(px, y, pw, 32)
        self.btn_craft.enabled = economy.inventory.can_craft(economy.batch_multiplier)
        self.btn_craft.draw(surface, assets)
        y += 38

        # ── PRICE ─────────────────────────────────────────────────────
        section("── PRICE ──")
        pt = font_md.render(f"${economy.pricing.sell_price:.2f} / cup",
                            True, COL_TEXT_LIGHT)
        surface.blit(pt, (PANEL_X + PANEL_W//2 - pt.get_width()//2, y))
        y += 22

        half = (pw - 8) // 2
        self.btn_price_up.rect.update(px,              y, half, 28)
        self.btn_price_down.rect.update(px + half + 8, y, half, 28)
        self.btn_price_up.draw(surface, assets)
        self.btn_price_down.draw(surface, assets)
        y += 34

        # ── INVENTORY ─────────────────────────────────────────────────
        section("── INVENTORY ──")
        inv = economy.inventory
        items = [
            ("Lemons",   inv.lemons,   MAX_INV_LEMONS,  (255, 230,  40)),
            ("Sugar",    inv.sugar,    MAX_INV_SUGAR,   (220, 220, 180)),
            ("Ice",      inv.ice,      MAX_INV_ICE,     (180, 220, 255)),
            ("Cups",     inv.cups,     MAX_INV_CUPS,    (200, 170, 130)),
            ("Lemonade", inv.lemonade, MAX_LEMONADE,    (255, 200,  50)),
        ]
        bar_h = 14
        for item_label, qty, cap, color in items:
            ratio = qty / cap if cap > 0 else 0
            # background track
            pygame.draw.rect(surface, (40, 40, 65), (px, y, pw, bar_h), 0, 4)
            # filled portion
            fill_w = max(4, int(pw * ratio)) if ratio > 0 else 0
            if fill_w:
                pygame.draw.rect(surface, color, (px, y, fill_w, bar_h), 0, 4)
            # label centred over bar
            lt = font_sm.render(f"{item_label}: {qty}/{cap}", True, COL_TEXT_LIGHT)
            surface.blit(lt, (px + pw//2 - lt.get_width()//2, y))
            y += bar_h + 6

        # ── RESTOCK ───────────────────────────────────────────────────
        section("── RESTOCK ──")
        for btn in self.restock_btns.values():
            btn.rect.update(px, y, pw, 26)
            btn.draw(surface, assets)
            y += 30

        # ── GEM ACTIONS ───────────────────────────────────────────────
        section("── GEM ACTIONS ──")
        gem_btns = [
            (self.btn_skip_night,   f"Skip Night  ({GEMS_SKIP_NIGHT}💎)"),
            (self.btn_double_day,   f"2x Earnings ({GEMS_DOUBLE_DAY}💎)"),
            (self.btn_daily_reward, "Daily Reward"),
        ]
        for btn, label in gem_btns:
            btn.label = label
            btn.rect.update(px, y, pw, 26)
            btn.draw(surface, assets)
            y += 30

        if monetization.double_day_active:
            at = font_sm.render("★ 2x ACTIVE!", True, COL_GOLD)
            surface.blit(at, (PANEL_X + PANEL_W//2 - at.get_width()//2, y))
            y += 18

        # ── UPGRADES ──────────────────────────────────────────────────
        y += 4
        self.btn_upgrades.rect.update(px, y, pw, 32)
        self.btn_upgrades.draw(surface, assets)
