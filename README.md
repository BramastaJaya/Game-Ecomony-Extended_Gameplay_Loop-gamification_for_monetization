# 🍋 Lemon Empire

A 2D pixel-art lemonade stand tycoon game built with Python and pygame. Manage your stand, craft lemonade, serve customers, grow your reputation, and build a lemon empire — one cup at a time.

---

## Screenshot

```
┌─────────────────────────────────────────────────────────────┐
│  $10.00  💎 0        Day 1  [=========] Morning   ☀ SUNNY  │
├──────────────────────────────────────────┬──────────────────┤
│                                          │  ── CRAFTING ──  │
│    🌳   🌳      🌳  🌳                   │  [ CRAFT  [C]  ] │
│              🟨🟨🟨🟨🟨                  │  ── PRICE ──     │
│              🟧 LEMONADE                 │    $1.50 / cup   │
│                 🟨🟨🟨🟨                 │  [Price+][Price-]│
│              👤 player                   │  ── INVENTORY ── │
│  ════════════════════════════════════    │  Lemons  10/50   │
│                                          │  ...             │
└──────────────────────────────────────────┴──────────────────┘
```

---

## Requirements

- Python 3.10+
- pygame 2.0+

```bash
pip install pygame
```

---

## Running the Game

```bash
# From inside the lemonade_tycoon/ folder
python main.py
```

> Make sure you run from inside `lemonade_tycoon/`, not the parent folder.

---

## Controls

| Key | Action |
|---|---|
| `A` / `D` or `←` / `→` | Move player left / right |
| `C` | Craft lemonade (must be near the stand) |
| `E` or `Space` | Serve the nearest waiting customer |
| `U` | Open / close the Upgrade Shop |
| `Esc` | Quit |

> All buttons in the right panel are also fully clickable with the mouse.

---

## How to Play

### The Core Loop

1. **Restock** — Buy ingredients from the side panel (Lemons, Sugar, Ice, Cups)
2. **Craft** — Walk near the stand and press `C` to mix a batch of lemonade
3. **Serve** — When a customer walks up and waits, press `E` to serve them
4. **Manage your price** — Use `Price +` / `Price -` to find the sweet spot
5. **Survive the day** — Each day lasts 2 minutes. At the end, review your profit report
6. **Reinvest** — Use earnings to restock and buy upgrades

### Pricing Strategy

Customer price acceptance is calculated as:

```
max_acceptable_price = (2.00 + reputation_bonus) × weather_demand_multiplier
```

- Charge **too much** → customers walk away → reputation drops → harder to sell
- Charge **too little** → sales are easy but margins are thin
- **Hot weather** multiplies demand by 1.6× — raise your price on hot days
- **Rainy days** cut demand to 0.3× — lower your price or you'll lose everyone

### Recipe

Each craft action consumes:

| Ingredient | Amount |
|---|---|
| Lemons | 2 |
| Sugar | 1 |
| Ice | 2 |
| Cups | 1 |

And produces **1 cup of lemonade**. Unlock the **Better Squeezer** upgrade to craft 2 at once.

---

## Weather System

Weather changes every 30 seconds and directly affects how many customers appear and what they'll pay.

| Weather | Demand Multiplier | Strategy |
|---|---|---|
| ☀ Sunny | 1.0× | Normal — steady trade |
| 🔥 Hot | 1.6× | Peak hours — raise price, stock up |
| ☁ Cloudy | 0.7× | Slower — keep price competitive |
| 🌧 Rainy | 0.3× | Very slow — save ingredients for tomorrow |

---

## Progression

### XP & Levels

- Earn **10 XP** per sale, **3 XP** per cup crafted
- XP required per level scales: `Level × 100 XP`
- Higher levels unlock upgrades in the shop

### Reputation (0–100)

- Starts at 50
- **+1** each time a customer is happy and served
- **−2** each time a customer leaves (out of stock or price too high)
- Higher reputation = customers tolerate higher prices

---

## Upgrades

Open the upgrade shop with `U`. Upgrades are permanent and level-gated.

| Upgrade | Cost | Requires | Effect |
|---|---|---|---|
| Better Squeezer | $25 | Level 2 | Craft 2 cups per action |
| Cooler Box | $40 | Level 3 | Ice efficiency ×2 |
| Marketing Flyers | $60 | Level 4 | +20% customer spawn rate |
| Premium Cups | $80 | Level 5 | Customers accept 20% higher prices |
| Second Stand | $150 | Level 7 | Auto-serves 1 customer per cycle |

---

## Gem Currency

Gems are the premium currency. They can be used for convenience actions:

| Action | Cost |
|---|---|
| Emergency restock (10 units of any item) | 5 💎 |
| Skip to next morning | 10 💎 |
| 2× earnings for the current day | 20 💎 |

### Daily Reward

Click **Daily Reward** once per day to collect free gems. Streaks increase the reward:

| Streak Day | Gems |
|---|---|
| Day 1–2 | 5 💎 |
| Day 3–4 | 10 💎 |
| Day 5 | 15 💎 |
| Day 6 | 20 💎 |
| Day 7+ | 30 💎 |

---

## Project Structure

```
lemonade_tycoon/
├── main.py                    ← Entry point
├── core/
│   ├── constants.py           ← All tunable game values
│   ├── events.py              ← Publish-subscribe EventBus
│   ├── assets.py              ← Fonts + procedural pixel-art surfaces
│   └── game_loop.py           ← Main loop & game state machine
├── systems/
│   ├── economy.py             ← Inventory, pricing, crafting, P&L ledger
│   ├── progression.py         ← XP, levelling, reputation, upgrade logic
│   ├── weather.py             ← Weather state + demand multipliers
│   ├── customer.py            ← Customer FSM (walk → wait → served/leave)
│   ├── monetization.py        ← Gem sinks, IAP simulation, daily reward
│   └── notification.py        ← Floating toast message queue
├── entities/
│   └── player.py              ← Movement, timed action system, rendering
└── ui/
    ├── hud.py                 ← Top bar (cash, gems, day, weather, rep, XP)
    ├── side_panel.py          ← Right panel (craft, price, inventory, buttons)
    ├── upgrade_panel.py       ← Full-screen upgrade shop overlay
    ├── end_of_day.py          ← Day summary report overlay
    └── world.py               ← Sky, clouds, ground, road, trees, stand
```

### Architecture Notes

- **EventBus** (`core/events.py`) decouples all systems — nothing imports each other directly; they communicate only via `bus.emit()` / `bus.subscribe()`
- All tunable values (prices, timing, XP rates, upgrade costs) live in `core/constants.py` — tweak the game feel without touching logic
- No external assets — all graphics are drawn programmatically via pygame primitives in `core/assets.py`

---

## Customising the Game

All balance values are in `core/constants.py`:

```python
DAY_DURATION            = 120.0   # seconds per day
CUSTOMER_SPAWN_INTERVAL = 4.0     # seconds between customer spawns
DEFAULT_SELL_PRICE      = 1.50    # starting cup price
XP_PER_SALE             = 10      # XP earned per sale
XP_LEVEL_CURVE          = 100     # base XP needed per level
RECIPE                  = {"lemons": 2, "sugar": 1, "ice": 2, "cups": 1}
```

---

## License

NOTE. The entire code structure was generated with the help of AI. use wisely
