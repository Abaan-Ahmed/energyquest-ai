# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  config/settings.py
# ─────────────────────────────────────────────────────────────

SCREEN_WIDTH  = 1400
SCREEN_HEIGHT = 900
FPS           = 60

GRID_ROWS    = 15
GRID_COLS    = 15
CELL_SIZE    = 52

GRID_OFFSET_X = 18
GRID_OFFSET_Y = 82

START_ENERGY   = 40
MOVE_COST      = 1
TRAP_COST      = 5
NUM_GEMS       = 10   # total gems; split evenly between human and AI
MAX_GEM_ENERGY = 8

C_BLACK = (  0,   0,   0)
C_WHITE = (255, 255, 255)

BG_BASE      = (  8,  11,  22)
BG_SURFACE   = ( 13,  17,  32)
BG_ELEVATED  = ( 18,  24,  44)
BG_PANEL     = ( 11,  14,  26)

GRID_CELL_BG  = ( 16,  20,  36)
GRID_CELL_ALT = ( 14,  18,  32)
GRID_LINE     = ( 24,  30,  52)
GRID_BORDER   = ( 42,  54,  95)

WALL_BASE  = ( 36,  42,  68)
WALL_FACE  = ( 50,  58,  90)
WALL_HI    = ( 78,  90, 130)
WALL_SHADE = ( 22,  27,  48)
WALL_TOP   = ( 88, 102, 148)
WALL_CRACK = ( 30,  36,  60)

# Human gems (gold)
GEM_CORE   = (255, 215,  55)
GEM_BRIGHT = (255, 248, 150)
GEM_GLOW   = (255, 175,  25)
GEM_DEEP   = (155,  98,   8)
GEM_EDGE   = (230, 180,  40)

# AI gems (purple)
GEM_A_CORE   = (195,  85, 255)
GEM_A_BRIGHT = (230, 160, 255)
GEM_A_GLOW   = (148,  45, 215)
GEM_A_DEEP   = ( 85,  18, 148)
GEM_A_EDGE   = (175,  75, 240)

TRAP_CORE   = (212,  42,  42)
TRAP_BRIGHT = (255,  88,  88)
TRAP_GLOW   = (155,  18,  18)
TRAP_BG     = ( 26,   8,   8)
TRAP_TICK   = (255, 140,  55)

GOAL_CORE   = ( 38, 210, 108)
GOAL_BRIGHT = ( 95, 255, 165)
GOAL_GLOW   = ( 22, 158,  82)
GOAL_BG     = (  8,  28,  18)
GOAL_RING   = ( 62, 232, 138)

START_CORE = (195, 202, 255)
START_DIM  = ( 95, 108, 168)
START_BG   = ( 14,  18,  34)

H_CORE   = ( 55, 135, 255)
H_BRIGHT = (125, 188, 255)
H_GLOW   = ( 35, 100, 215)
H_DEEP   = ( 22,  68, 160)

A_CORE   = (175,  68, 255)
A_BRIGHT = (215, 135, 255)
A_GLOW   = (130,  45, 200)
A_DEEP   = ( 80,  22, 148)

HUD_BG       = ( 10,  13,  24)
HUD_CARD_BG  = ( 16,  21,  38)
HUD_CARD_HI  = ( 24,  32,  58)
HUD_BORDER   = ( 36,  46,  80)
HUD_BORDER_B = ( 52,  68, 115)
HUD_TEXT     = (218, 224, 248)
HUD_MUTED    = (105, 118, 158)
HUD_ACCENT   = ( 72, 128, 255)
HUD_DIM      = ( 58,  68, 100)

E_HIGH     = ( 45, 200,  95)
E_MID      = (218, 172,  40)
E_LOW      = (208,  48,  48)
E_BAR_BG   = ( 22,  28,  50)
E_BAR_BORD = ( 42,  54,  88)

BTN_BG        = ( 22,  28,  52)
BTN_BORDER    = ( 44,  56,  95)
BTN_HOVER_BG  = ( 34,  44,  78)
BTN_SEL_BG    = ( 34,  68, 162)
BTN_SEL_BOR   = ( 62, 115, 255)
BTN_TEXT      = (190, 200, 230)
BTN_SEL_TEXT  = (175, 210, 255)
BTN_ACTION    = ( 48, 112, 235)
BTN_ACTION_H  = ( 68, 138, 255)
BTN_DANGER    = (165,  44,  44)
BTN_DANGER_H  = (205,  65,  65)
BTN_SUCCESS   = ( 38, 152,  84)
BTN_SUCCESS_H = ( 55, 188, 105)

PATH_DOT  = ( 72,  95, 185)
TRAIL_H   = ( 55, 135, 255)
TRAIL_A   = (175,  68, 255)
