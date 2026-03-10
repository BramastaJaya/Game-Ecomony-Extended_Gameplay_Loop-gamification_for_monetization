# ==============================================================================
# GAMIFICATION SYSTEM
# Achievements, milestone rewards, daily goals, progression pacing
# ==============================================================================

import pygame
from data.constants import (
    ACHIEVEMENT_DEFINITIONS, C_GOLD, C_WHITE, C_DARK, C_PANEL, C_PANEL_LIGHT,
    C_GREEN, C_ACCENT, C_TEXT,
)


class Achievement:
    def __init__(self, definition: dict):
        self.id       = definition["id"]
        self.name     = definition["name"]
        self.desc     = definition["desc"]
        self.xp_reward = definition["xp"]
        self.unlocked  = False
        self.unlock_day = -1

    def check(self, stats: dict) -> bool:
        """Return True if newly unlocked."""
        if self.unlocked:
            return False
        trigger = self._evaluate(stats)
        if trigger:
            self.unlocked = True
            self.unlock_day = stats.get("day", 0)
        return trigger

    def _evaluate(self, s: dict) -> bool:
        if self.id == "first_sale":       return s.get("total_sales", 0) >= 1
        if self.id == "sales_10":         return s.get("total_sales", 0) >= 10
        if self.id == "sales_50":         return s.get("total_sales", 0) >= 50
        if self.id == "sales_100":        return s.get("total_sales", 0) >= 100
        if self.id == "day_5":            return s.get("day", 0) >= 5
        if self.id == "rich_100":         return s.get("balance", 0) >= 100
        if self.id == "rich_500":         return s.get("balance", 0) >= 500
        if self.id == "level_5":          return s.get("level", 1) >= 5
        if self.id == "upgrade_stand":    return s.get("upgrades_owned", 0) >= 1
        if self.id == "gather_50":        return s.get("total_gathered", 0) >= 50
        if self.id == "profit_perfect":   return s.get("daily_revenue", 0) >= 30
        return False


class DailyGoal:
    """
    One-per-day short goal that gives XP bonus on completion.
    Adds session-level engagement driver.
    """

    TEMPLATES = [
        {"desc": "Sell {n} cups today",     "key": "daily_sales",   "n_range": (5, 15),  "xp": 80},
        {"desc": "Earn ${n} today",         "key": "daily_revenue",  "n_range": (8, 25),  "xp": 100},
        {"desc": "Gather {n} resources",    "key": "daily_gathered", "n_range": (4, 10),  "xp": 60},
    ]

    def __init__(self, day: int):
        import random
        template = random.choice(self.TEMPLATES)
        n = random.randint(*template["n_range"])
        self.desc      = template["desc"].format(n=n)
        self.key       = template["key"]
        self.target    = n
        self.xp_reward = template["xp"]
        self.completed = False
        self.day       = day

    def check(self, daily_stats: dict) -> bool:
        if self.completed:
            return False
        val = daily_stats.get(self.key, 0)
        if val >= self.target:
            self.completed = True
            return True
        return False

    def progress(self, daily_stats: dict) -> float:
        val = daily_stats.get(self.key, 0)
        return min(1.0, val / max(1, self.target))


class ToastNotification:
    """Screen-edge popup for achievement unlocks and level ups."""

    def __init__(self, title: str, subtitle: str, duration: int = 240,
                 color=C_GOLD):
        self.title    = title
        self.subtitle = subtitle
        self.duration = duration
        self.timer    = 0
        self.color    = color
        self.slide_x  = -320   # starts off-screen left

    def update(self):
        self.timer += 1
        # Slide in quickly, hold, slide out
        if self.timer < 20:
            self.slide_x = int(-320 + (320 + 16) * (self.timer / 20))
        elif self.timer > self.duration - 30:
            t = (self.timer - (self.duration - 30)) / 30
            self.slide_x = int(16 - (320 + 16) * t)
        else:
            self.slide_x = 16

    def is_dead(self) -> bool:
        return self.timer >= self.duration

    def draw(self, surface: pygame.Surface, y_offset: int,
             font_large: pygame.font.Font, font_small: pygame.font.Font):
        w, h = 300, 54
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((*C_PANEL, 230))
        pygame.draw.rect(panel, self.color, (0, 0, 4, h))   # left accent bar

        # Trophy icon area
        pygame.draw.rect(panel, self.color, (10, 10, 30, 30))
        icon = font_large.render("★", True, C_DARK)
        panel.blit(icon, (10 + 15 - icon.get_width() // 2, 10 + 15 - icon.get_height() // 2))

        # Text
        title_surf = font_large.render(self.title,    True, C_GOLD)
        sub_surf   = font_small.render(self.subtitle, True, C_TEXT)
        panel.blit(title_surf, (50, 6))
        panel.blit(sub_surf,   (50, 28))

        surface.blit(panel, (self.slide_x, y_offset))


class GamificationSystem:
    """
    Owns all achievements, daily goals, and notification queue.
    Game loop calls evaluate() each frame with current stats.
    """

    def __init__(self):
        self.achievements: list[Achievement] = [
            Achievement(d) for d in ACHIEVEMENT_DEFINITIONS
        ]
        self.daily_goal: DailyGoal | None = None
        self.toasts: list[ToastNotification] = []
        self._toast_y_slots = [16, 88, 160]   # stacked notification rows

    # --- Per-frame evaluation ---
    def evaluate(self, stats: dict, daily_stats: dict) -> list[tuple[str, int]]:
        """
        Returns list of (achievement_name, xp) for newly unlocked achievements.
        Also checks daily goal.
        """
        rewards = []

        for ach in self.achievements:
            if ach.check(stats):
                rewards.append((ach.name, ach.xp_reward))
                self.push_toast(f"Achievement: {ach.name}",
                                f"+{ach.xp_reward} XP  —  {ach.desc}")

        if self.daily_goal and self.daily_goal.check(daily_stats):
            rewards.append((f"Daily: {self.daily_goal.desc}", self.daily_goal.xp_reward))
            self.push_toast("Daily Goal Complete!",
                            f"+{self.daily_goal.xp_reward} XP", color=C_GREEN)

        return rewards

    def new_day(self, day: int):
        self.daily_goal = DailyGoal(day)

    def push_toast(self, title: str, subtitle: str, color=C_GOLD):
        self.toasts.append(ToastNotification(title, subtitle, color=color))

    def update_toasts(self):
        for t in self.toasts:
            t.update()
        self.toasts = [t for t in self.toasts if not t.is_dead()]

    def draw_toasts(self, surface: pygame.Surface,
                    font_large: pygame.font.Font, font_small: pygame.font.Font):
        for i, toast in enumerate(self.toasts[:3]):
            y = 16 + i * 72
            toast.draw(surface, y, font_large, font_small)

    def unlocked_count(self) -> int:
        return sum(1 for a in self.achievements if a.unlocked)

    def total_count(self) -> int:
        return len(self.achievements)
