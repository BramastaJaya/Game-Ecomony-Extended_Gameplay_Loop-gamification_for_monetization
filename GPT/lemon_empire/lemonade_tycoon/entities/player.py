# entities/player.py
"""Player entity: movement, actions, interaction zones."""

from __future__ import annotations
import pygame
from core.constants import *
from core.events import bus, EVT_NOTIFICATION


class ActionState:
    IDLE      = "idle"
    WORKING   = "working"   # crafting animation
    RESTOCKING = "restocking"


class Player:
    def __init__(self, assets):
        self.assets  = assets
        self.x: float = float(STAND_X - 80)
        self.y: float = float(GROUND_Y - PLAYER_H)
        self.vel_x: float = 0.0
        self.facing:  int  = 1   # 1=right, -1=left
        self.action_state: str   = ActionState.IDLE
        self.action_timer: float = 0.0
        self.action_progress: float = 0.0   # 0..1
        self._pending_action = None

        # Bob animation
        self._bob: float   = 0.0
        self._bob_dir: int = 1

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        if self.action_state == ActionState.WORKING:
            return   # locked during action
        self.vel_x = 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x =  PLAYER_SPEED
            self.facing =  1

    def start_action(self, action_fn, duration: float = WORK_ACTION_DURATION) -> None:
        """Begin a timed action (crafting, restocking). action_fn called on complete."""
        if self.action_state != ActionState.IDLE:
            return
        self.action_state    = ActionState.WORKING
        self.action_timer    = 0.0
        self.action_progress = 0.0
        self._pending_action = (action_fn, duration)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        # Movement
        self.x = max(0, min(WORLD_W - PLAYER_W, self.x + self.vel_x))

        # Action
        if self.action_state == ActionState.WORKING:
            fn, dur = self._pending_action
            self.action_timer    += dt
            self.action_progress  = min(1.0, self.action_timer / dur)
            if self.action_timer >= dur:
                fn()
                self.action_state    = ActionState.IDLE
                self._pending_action = None
                self.action_progress = 0.0

        # Bob animation when moving
        if self.vel_x != 0:
            self._bob += self._bob_dir * 0.3
            if abs(self._bob) > 3:
                self._bob_dir *= -1
        else:
            self._bob = 0.0

    # ------------------------------------------------------------------
    # Zones / helpers
    # ------------------------------------------------------------------
    def near_stand(self) -> bool:
        return abs(self.x - STAND_X) < INTERACT_DIST

    def center_x(self) -> float:
        return self.x + PLAYER_W / 2

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        surf = self.assets.surf("player")
        if self.facing == -1:
            surf = pygame.transform.flip(surf, True, False)

        draw_y = int(self.y + self._bob)

        # Action progress arc above head
        if self.action_state == ActionState.WORKING:
            cx = int(self.x + PLAYER_W // 2)
            cy = draw_y - 14
            import math
            angle = -90
            end_a = -90 + int(360 * self.action_progress)
            for a in range(angle, end_a, 6):
                rad = math.radians(a)
                px  = cx + int(10 * math.cos(rad))
                py  = cy + int(10 * math.sin(rad))
                pygame.draw.circle(surface, COL_GREEN, (px, py), 2)

        surface.blit(surf, (int(self.x), draw_y))

        # Shadow
        shadow = pygame.Surface((PLAYER_W + 4, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), (0, 0, PLAYER_W + 4, 6))
        surface.blit(shadow, (int(self.x) - 2, int(self.y) + PLAYER_H - 2))
