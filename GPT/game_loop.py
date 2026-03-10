# core/game_loop.py
"""Main game loop, state machine, system wiring."""

from __future__ import annotations
import sys
import pygame

from core.constants import *
from core.assets    import Assets
from core.events    import bus, EVT_DAY_START, EVT_DAY_END, EVT_LEVEL_UP

from systems.economy       import EconomySystem
from systems.progression   import ProgressionSystem
from systems.weather        import WeatherSystem
from systems.customer       import CustomerSystem
from systems.monetization   import MonetizationSystem
from systems.notification   import NotificationSystem

from entities.player        import Player, ActionState

from ui.hud           import draw_hud
from ui.side_panel    import SidePanel
from ui.upgrade_panel import UpgradePanel
from ui.end_of_day    import EndOfDayPanel
from ui.world         import WorldRenderer


class GameState:
    PLAYING  = "playing"
    END_DAY  = "end_day"
    UPGRADE  = "upgrade"


class GameLoop:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()

        # --- Systems ---
        self.assets        = Assets.get()
        self.economy       = EconomySystem()
        self.progression   = ProgressionSystem(self.economy)
        self.weather       = WeatherSystem()
        self.customers     = CustomerSystem(self.assets)
        self.monetization  = MonetizationSystem(self.economy)
        self.notifications = NotificationSystem(self.assets)

        # --- Entities ---
        self.player = Player(self.assets)

        # --- UI ---
        self.world        = WorldRenderer(self.assets)
        self.side_panel   = SidePanel(self.assets)
        self.upgrade_panel = UpgradePanel(self.assets)
        self.eod_panel    = EndOfDayPanel(self.assets)

        # --- Day state ---
        self.day:       int   = 1
        self.day_timer: float = 0.0
        self.state:     str   = GameState.PLAYING

        # Seed starting inventory so player can immediately craft
        self._seed_start_inventory()
        bus.emit(EVT_DAY_START, day_number=self.day)

        # Floating +$ labels
        self._sale_labels: list = []   # [{x,y,text,timer,alpha}]

    def _seed_start_inventory(self):
        inv = self.economy.inventory
        inv.lemons = 10
        inv.sugar  = 6
        inv.ice    = 12
        inv.cups   = 8

    # ------------------------------------------------------------------
    # Public actions (called by UI)
    # ------------------------------------------------------------------
    def player_craft(self) -> None:
        if self.player.action_state != ActionState.IDLE:
            return
        if not self.player.near_stand():
            bus.emit("notification", text="Get closer to the stand!", color=COL_RED)
            return
        self.player.start_action(self.economy.try_craft)

    def player_serve(self) -> None:
        if not self.player.near_stand():
            return
        self.customers.serve_nearest(self.player.center_x(),
                                      self.economy, self.weather, self.progression)

    def toggle_upgrade_panel(self) -> None:
        self.upgrade_panel.toggle()

    def force_day_end(self) -> None:
        self._end_day()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_c:
                    self.player_craft()
                if event.key == pygame.K_e or event.key == pygame.K_SPACE:
                    self.player_serve()
                if event.key == pygame.K_u:
                    self.toggle_upgrade_panel()

            # UI panels eat events first
            if self.upgrade_panel.visible:
                self.upgrade_panel.handle_event(event, self.progression)
                continue

            if self.state == GameState.END_DAY:
                if self.eod_panel.handle_event(event):
                    self._start_next_day()
                continue

            self.side_panel.handle_event(
                event, self.economy, self.progression,
                self.monetization, self)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def _update(self, dt: float) -> None:
        if self.state != GameState.PLAYING:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(dt)

        self.weather.update(dt)
        self.customers.update(dt, self.economy, self.weather, self.progression)
        self.monetization.update(dt)
        self.notifications.update(dt)
        self.world.update(dt, self.weather)

        # Floating sale labels
        for lbl in self._sale_labels:
            lbl["timer"] -= dt
            lbl["y"]     -= 30 * dt
            lbl["alpha"]  = max(0, int(255 * lbl["timer"] / 1.5))
        self._sale_labels = [l for l in self._sale_labels if l["timer"] > 0]

        # Day timer
        self.day_timer += dt
        if self.day_timer >= DAY_DURATION:
            self._end_day()

    # ------------------------------------------------------------------
    # Day management
    # ------------------------------------------------------------------
    def _end_day(self) -> None:
        self.state = GameState.END_DAY
        ledger     = self.economy.end_day()
        self.eod_panel.show(ledger)
        bus.emit(EVT_DAY_END,
                 day_number=ledger.day,
                 earnings=ledger.revenue)

    def _start_next_day(self) -> None:
        self.day       += 1
        self.day_timer  = 0.0
        self.state      = GameState.PLAYING
        self.monetization.on_new_day()
        self.economy.start_day(self.day)
        bus.emit(EVT_DAY_START, day_number=self.day)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def _draw(self) -> None:
        self.screen.fill(COL_BG)

        # World
        self.world.draw(self.screen, self.weather)

        # Customers
        self.customers.draw(self.screen)

        # Player
        self.player.draw(self.screen)

        # Floating +$ labels
        font_md = self.assets.font("md")
        for lbl in self._sale_labels:
            s = font_md.render(lbl["text"], True, COL_GOLD)
            s.set_alpha(lbl["alpha"])
            self.screen.blit(s, (int(lbl["x"]), int(lbl["y"])))

        # HUD
        draw_hud(self.screen, self.assets,
                 self.economy, self.progression,
                 self.weather, self.day,
                 min(1.0, self.day_timer / DAY_DURATION))

        # Side panel
        self.side_panel.draw(self.screen, self.assets,
                             self.economy, self.progression,
                             self.monetization)

        # Notifications
        self.notifications.draw(self.screen)

        # Overlays
        self.upgrade_panel.draw(self.screen, self.assets, self.progression)
        self.eod_panel.draw(self.screen, self.assets)

        # Controls hint
        self._draw_controls_hint()

        pygame.display.flip()

    def _draw_controls_hint(self):
        if self.state != GameState.PLAYING:
            return
        bar_h = 22
        pygame.draw.rect(self.screen, COL_PANEL,
                         (0, SCREEN_H - bar_h, PANEL_X, bar_h))
        pygame.draw.line(self.screen, (60, 60, 80),
                         (0, SCREEN_H - bar_h), (PANEL_X, SCREEN_H - bar_h), 1)
        font  = self.assets.font("sm")
        hints = "[A/D] Move    [C] Craft    [E/Space] Serve    [U] Upgrades    [Esc] Quit"
        t     = font.render(hints, True, (150, 150, 175))
        self.screen.blit(t, (8, SCREEN_H - bar_h + 4))
