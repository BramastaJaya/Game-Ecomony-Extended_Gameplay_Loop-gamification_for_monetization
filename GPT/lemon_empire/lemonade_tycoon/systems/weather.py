# systems/weather.py
"""Weather system that modulates customer demand."""

import random
from core.constants import *
from core.events import bus, EVT_WEATHER_CHANGE, EVT_NOTIFICATION


class WeatherSystem:
    def __init__(self):
        self.current:   str   = WEATHER_SUNNY
        self.timer:     float = 0.0
        self.interval:  float = WEATHER_CHANGE_INTERVAL

    @property
    def demand_multiplier(self) -> float:
        return WEATHER_DEMAND.get(self.current, 1.0)

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= self.interval:
            self.timer = 0.0
            self._change_weather()

    def _change_weather(self) -> None:
        options = [WEATHER_SUNNY, WEATHER_HOT, WEATHER_CLOUDY, WEATHER_RAINY]
        weights = [0.35, 0.25, 0.25, 0.15]
        new_w   = random.choices(options, weights=weights, k=1)[0]
        if new_w != self.current:
            self.current = new_w
            bus.emit(EVT_WEATHER_CHANGE, weather=new_w)
            labels = {
                WEATHER_SUNNY:  ("Sunny day!", COL_GOLD),
                WEATHER_HOT:    ("Hot wave! Demand up!", (255, 100, 50)),
                WEATHER_CLOUDY: ("Cloudy. Slow traffic.", (160, 160, 180)),
                WEATHER_RAINY:  ("Raining! Few customers.", (80, 130, 200)),
            }
            text, color = labels.get(new_w, ("Weather changed", COL_TEXT_DARK))
            bus.emit(EVT_NOTIFICATION, text=text, color=color)

    def icon(self) -> str:
        return {
            WEATHER_SUNNY:  "☀",
            WEATHER_HOT:    "🔥",
            WEATHER_CLOUDY: "☁",
            WEATHER_RAINY:  "🌧",
        }.get(self.current, "?")
