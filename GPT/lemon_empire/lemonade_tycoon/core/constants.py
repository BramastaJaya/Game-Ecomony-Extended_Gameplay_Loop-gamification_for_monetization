# core/constants.py

SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
TITLE = "Lemon Empire"

# --- Palette ---
COL_BG          = (245, 235, 180)
COL_GROUND      = (120, 190,  80)
COL_ROAD        = (160, 155, 145)
COL_STAND_BODY  = (155, 120,  80)
COL_STAND_ROOF  = (255, 140,  40)
COL_PLAYER      = ( 100, 100, 100)
COL_CUSTOMER    = (200,  90,  90)
COL_TEXT_DARK   = ( 30,  30,  30)
COL_TEXT_LIGHT  = (255, 255, 255)
COL_GOLD        = (255, 195,  30)
COL_RED         = (220,  60,  60)
COL_GREEN       = ( 60, 190,  80)
COL_BLUE        = ( 60, 120, 210)
COL_PANEL       = ( 30,  30,  50)
COL_PANEL_LIGHT = ( 50,  50,  75)
COL_BTN         = ( 60, 160,  80)
COL_BTN_HOV     = ( 80, 200, 100)
COL_BTN_DIS     = ( 90,  90,  90)
COL_XP_BAR      = ( 80, 180, 255)
COL_SHADOW      = (  0,   0,   0, 80)

# --- World ---
TILE  = 32
WORLD_W = SCREEN_W
WORLD_H = SCREEN_H

GROUND_Y    = 520     # y where ground starts
STAND_X     = 560
STAND_Y     = 400

# --- Player ---
PLAYER_SPEED   = 5
PLAYER_W       = 24
PLAYER_H       = 38
INTERACT_DIST  = 80

# --- Economy defaults ---
DEFAULT_LEMON_PRICE     = 0.25
DEFAULT_SUGAR_PRICE     = 0.10
DEFAULT_ICE_PRICE       = 0.05
DEFAULT_CUP_PRICE       = 0.08
DEFAULT_SELL_PRICE      = 1.50
MAX_SELL_PRICE          = 10.0
MIN_SELL_PRICE          = 0.25

# --- Gameplay timing (in seconds) ---
CUSTOMER_SPAWN_INTERVAL = 4.0
WORK_ACTION_DURATION    = 1.2   # seconds to squeeze lemons / mix etc.
DAY_DURATION            = 120.0 # seconds per in-game day
WEATHER_CHANGE_INTERVAL = 30.0

# --- Inventory caps ---
MAX_INV_LEMONS   = 50
MAX_INV_SUGAR    = 50
MAX_INV_ICE      = 50
MAX_INV_CUPS     = 50
MAX_LEMONADE     = 30

# --- Recipe ---
RECIPE = {
    "lemons": 2,
    "sugar":  1,
    "ice":    2,
    "cups":   1,
}
BATCH_YIELD = 1  # cups of lemonade per craft

# --- XP / Levels ---
XP_PER_SALE       = 10
XP_PER_CRAFT      = 3
XP_LEVEL_CURVE    = 100   # base XP per level (scales x level)

# --- Reputation ---
REP_PER_HAPPY     =  1
REP_PER_UNHAPPY   = -2
MAX_REPUTATION    = 100
MIN_REPUTATION    = 0

# --- Weather types ---
WEATHER_SUNNY  = "sunny"
WEATHER_HOT    = "hot"
WEATHER_CLOUDY = "cloudy"
WEATHER_RAINY  = "rainy"

# demand multiplier per weather
WEATHER_DEMAND = {
    WEATHER_SUNNY:  1.0,
    WEATHER_HOT:    1.6,
    WEATHER_CLOUDY: 0.7,
    WEATHER_RAINY:  0.3,
}

# --- Shop unlock costs ---
UPGRADES = {
    "better_squeezer": {
        "cost": 25.0,
        "description": "Craft 2x batches at once",
        "effect": "batch_multiplier",
        "value": 2,
        "requires_level": 2,
    },
    "cooler_box": {
        "cost": 40.0,
        "description": "Ice lasts 2x longer",
        "effect": "ice_efficiency",
        "value": 2,
        "requires_level": 3,
    },
    "marketing_flyers": {
        "cost": 60.0,
        "description": "+20% customer spawn rate",
        "effect": "spawn_bonus",
        "value": 0.20,
        "requires_level": 4,
    },
    "premium_cups": {
        "cost": 80.0,
        "description": "Customers pay up to 20% more",
        "effect": "price_tolerance",
        "value": 0.20,
        "requires_level": 5,
    },
    "second_stand": {
        "cost": 150.0,
        "description": "Auto-serve 1 customer/cycle",
        "effect": "auto_serve",
        "value": 1,
        "requires_level": 7,
    },
}

# --- Monetization (soft-currency IAP simulation) ---
IAP_GEMS_PACKS = [
    {"gems": 50,   "label": "Starter",  "cost_usd": 0.99},
    {"gems": 150,  "label": "Popular",  "cost_usd": 2.99},
    {"gems": 400,  "label": "Value",    "cost_usd": 5.99},
]
GEMS_PER_RESTOCK   = 5    # emergency restock costs gems
GEMS_SKIP_NIGHT    = 10   # skip to next morning
GEMS_DOUBLE_DAY    = 20   # double earnings for one day

# --- UI layout ---
HUD_H        = 80
PANEL_W      = 280
PANEL_X      = SCREEN_W - PANEL_W
