# ui/hud.py
import pygame
from core.constants import *


def draw_hud(surface, assets, economy, progression, weather, day, day_pct):
    font_hud = assets.font("hud")
    font_sm  = assets.font("sm")

    pygame.draw.rect(surface, COL_PANEL, (0, 0, SCREEN_W, HUD_H))
    pygame.draw.line(surface, COL_GOLD, (0, HUD_H), (SCREEN_W, HUD_H), 2)

    surface.blit(assets.surf("coin"), (10, 12))
    surface.blit(font_hud.render(f"${economy.cash:.2f}", True, COL_GOLD), (28, 12))
    surface.blit(assets.surf("gem"), (10, 34))
    surface.blit(font_hud.render(str(economy.gems), True, (140,220,255)), (28, 34))

    day_t = font_hud.render(f"Day {day}", True, COL_TEXT_LIGHT)
    surface.blit(day_t, (SCREEN_W//2 - day_t.get_width()//2, 8))

    bx, by, bw, bh = SCREEN_W//2 - 80, 30, 160, 10
    pygame.draw.rect(surface, (60,60,80), (bx,by,bw,bh), 0, 4)
    pygame.draw.rect(surface, COL_GOLD,  (bx,by,int(bw*day_pct),bh), 0, 4)
    lbl = font_sm.render("Morning" if day_pct < 0.5 else "Afternoon", True, (200,200,180))
    surface.blit(lbl, (bx+bw+6, by-2))

    wt = font_hud.render(f"{weather.icon()} {weather.current.upper()}", True, COL_TEXT_LIGHT)
    surface.blit(wt, (SCREEN_W-210, 8))

    rep_pct = progression.reputation / MAX_REPUTATION
    rx, ry = SCREEN_W-210, 30
    pygame.draw.rect(surface, (60,60,80), (rx,ry,120,8), 0, 4)
    rc = COL_GREEN if rep_pct>0.6 else (COL_GOLD if rep_pct>0.3 else COL_RED)
    pygame.draw.rect(surface, rc, (rx,ry,int(120*rep_pct),8), 0, 4)
    surface.blit(font_sm.render(f"Rep {int(progression.reputation)}", True, (200,200,180)), (rx+125,ry-2))

    xp_pct = progression.xp_progress()
    xx, xy = SCREEN_W-210, 50
    pygame.draw.rect(surface, (40,40,60), (xx,xy,120,8), 0, 4)
    pygame.draw.rect(surface, COL_XP_BAR, (xx,xy,int(120*xp_pct),8), 0, 4)
    surface.blit(font_sm.render(f"Lv {progression.level}", True, COL_XP_BAR), (xx+125,xy-2))
