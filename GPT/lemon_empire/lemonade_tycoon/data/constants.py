# ==============================================================================
# CONSTANTS & GAME CONFIGURATION
# Central config file — tweak values here to balance the economy
# ==============================================================================

# --- Screen ---
SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
TITLE = "Lemon Stand Tycoon"

# --- Colors (pixel-art warm palette) ---
C_BG          = (255, 248, 220)   # cream background
C_GRASS       = (124, 187,  74)
C_ROAD        = (180, 160, 130)
C_STAND_BASE  = (210, 140,  60)
C_STAND_ROOF  = (255, 200,  50)
C_WATER       = (100, 180, 240)
C_WHITE       = (255, 255, 255)
C_BLACK       = (  0,   0,   0)
C_GOLD        = (255, 215,   0)
C_RED         = (220,  50,  50)
C_GREEN       = ( 50, 200,  80)
C_BLUE        = ( 50, 100, 200)
C_DARK        = ( 30,  30,  50)
C_PANEL       = ( 40,  40,  70)
C_PANEL_LIGHT = ( 60,  60,  95)
C_TEXT        = (230, 230, 255)
C_ACCENT      = (255, 180,  30)
C_XP_BAR      = ( 80, 200, 120)
C_HP_BAR      = (220,  60,  60)
C_SHADOW      = (  0,   0,   0, 80)

# --- Tile / World ---
TILE = 32
WORLD_W = 40   # tiles
WORLD_H = 20   # tiles
STAND_X = 15   # tile column where stand sits
STAND_Y = 9

# --- Player ---
PLAYER_SPEED     = 3          # px / frame
PLAYER_REACH     = 80         # px radius to interact
INTERACT_COOLDOWN = 60        # frames
WALK_ANIM_SPEED  = 8          # frames per walk frame

# --- Economy ---------------------------------------------------------------
STARTING_MONEY       = 25.0
STARTING_LEMONS      = 5
STARTING_SUGAR       = 3
STARTING_ICE         = 2

# Resource gather amounts per action
LEMON_GATHER_AMT     = 2
SUGAR_GATHER_AMT     = 2
ICE_GATHER_AMT       = 1
WATER_GATHER_AMT     = 3

# Crafting recipe: 1 cup lemonade = these ingredients
LEMONADE_LEMON_COST  = 1
LEMONADE_SUGAR_COST  = 1
LEMONADE_WATER_COST  = 1
LEMONADE_ICE_COST    = 1

# Base selling price
LEMONADE_BASE_PRICE  = 1.50
PRICE_MIN            = 0.25
PRICE_MAX            = 10.0
PRICE_STEP           = 0.25

# Cost to buy ingredients from shop
SHOP_LEMON_COST      = 0.40
SHOP_SUGAR_COST      = 0.30
SHOP_ICE_COST        = 0.25
SHOP_WATER_COST      = 0.10

# Customer thresholds: if price > threshold, demand drops
CUSTOMER_PRICE_SWEET_SPOT   = 1.75
CUSTOMER_PRICE_TOLERANCE    = 3.50   # above this, almost no customers
CUSTOMER_BASE_RATE          = 12     # customers per in-game minute at sweet spot
CUSTOMER_WEATHER_MULTIPLIER = {
    "sunny":    1.4,
    "cloudy":   0.9,
    "hot":      1.8,
    "rainy":    0.4,
    "perfect":  2.0,
}

# --- Time ---
GAME_MINUTE_FRAMES   = 180   # 1 in-game minute = 180 real frames (3 s at 60fps)
GAME_DAY_MINUTES     = 12    # 12 in-game minutes = 1 day
OPENING_MINUTE       = 0
CLOSING_MINUTE       = 11

# --- XP & Levelling --------------------------------------------------------
XP_PER_SALE          = 5
XP_PER_GATHER        = 2
XP_PER_DAY           = 20
XP_LEVEL_BASE        = 100   # XP needed for level 2
XP_LEVEL_SCALE       = 1.4   # multiplier per level

# --- Achievements ----------------------------------------------------------
ACHIEVEMENT_DEFINITIONS = [
    {"id": "first_sale",     "name": "First Pour",      "desc": "Sell your first cup",          "xp": 50},
    {"id": "sales_10",       "name": "Getting Popular", "desc": "Sell 10 cups total",           "xp": 80},
    {"id": "sales_50",       "name": "Lemon Legend",    "desc": "Sell 50 cups total",           "xp": 200},
    {"id": "sales_100",      "name": "Squeeze King",    "desc": "Sell 100 cups total",          "xp": 500},
    {"id": "day_5",          "name": "Veteran",         "desc": "Survive 5 days",               "xp": 100},
    {"id": "rich_100",       "name": "First C-Note",    "desc": "Accumulate $100",              "xp": 150},
    {"id": "rich_500",       "name": "Lemon Mogul",     "desc": "Accumulate $500",              "xp": 400},
    {"id": "level_5",        "name": "Level Up!",       "desc": "Reach level 5",                "xp": 200},
    {"id": "upgrade_stand",  "name": "Renovation Day",  "desc": "Buy your first upgrade",       "xp": 100},
    {"id": "gather_50",      "name": "Forager",         "desc": "Gather 50 total resources",    "xp": 120},
    {"id": "profit_perfect", "name": "Perfect Day",     "desc": "Earn $30+ in a single day",    "xp": 250},
]

# --- Upgrades --------------------------------------------------------------
UPGRADE_DEFINITIONS = [
    {
        "id": "blender",
        "name": "Electric Blender",
        "desc": "2x crafting speed",
        "cost": 30.0,
        "requires_level": 2,
        "effect": {"craft_speed": 2},
    },
    {
        "id": "umbrella",
        "name": "Sun Umbrella",
        "desc": "+20% customers on hot days",
        "cost": 20.0,
        "requires_level": 2,
        "effect": {"hot_bonus": 0.2},
    },
    {
        "id": "sign",
        "name": "Big Sign",
        "desc": "+15% base customer rate",
        "cost": 40.0,
        "requires_level": 3,
        "effect": {"base_rate_bonus": 0.15},
    },
    {
        "id": "cooler",
        "name": "Ice Cooler",
        "desc": "Ice lasts 2x longer (use 0.5x ice)",
        "cost": 50.0,
        "requires_level": 4,
        "effect": {"ice_efficiency": 2},
    },
    {
        "id": "recipe_mint",
        "name": "Mint Recipe",
        "desc": "Unlock Mint Lemonade — premium product",
        "cost": 75.0,
        "requires_level": 5,
        "effect": {"unlock_product": "mint_lemonade"},
    },
    {
        "id": "cart",
        "name": "Roaming Cart",
        "desc": "+25% all customer rates",
        "cost": 100.0,
        "requires_level": 6,
        "effect": {"global_rate_bonus": 0.25},
    },
]

# --- Products --------------------------------------------------------------
PRODUCT_DEFINITIONS = {
    "lemonade": {
        "name": "Classic Lemonade",
        "base_price": 1.50,
        "recipe": {"lemons": 1, "sugar": 1, "water": 1, "ice": 1},
        "xp_per_sale": 5,
        "unlocked_by_default": True,
    },
    "mint_lemonade": {
        "name": "Mint Lemonade",
        "base_price": 2.50,
        "recipe": {"lemons": 1, "sugar": 1, "water": 1, "ice": 1, "mint": 1},
        "xp_per_sale": 12,
        "unlocked_by_default": False,
    },
}

# --- Shop stock ---
SHOP_ITEMS = [
    {"id": "lemons",  "name": "Lemons (×5)",  "cost": SHOP_LEMON_COST * 5, "gives": {"lemons":  5}},
    {"id": "sugar",   "name": "Sugar (×5)",   "cost": SHOP_SUGAR_COST * 5, "gives": {"sugar":   5}},
    {"id": "ice",     "name": "Ice (×3)",     "cost": SHOP_ICE_COST   * 3, "gives": {"ice":     3}},
    {"id": "water",   "name": "Water (×5)",   "cost": SHOP_WATER_COST * 5, "gives": {"water":   5}},
    {"id": "mint",    "name": "Mint (×3)",    "cost": 0.60,                "gives": {"mint":    3}},
]
