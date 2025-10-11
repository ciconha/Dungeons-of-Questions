import os

SCREEN_WIDTH   = 1280
SCREEN_HEIGHT  = 720
SCREEN_TITLE   = "RPG da Emilly"

BASE_PATH       = os.path.dirname(__file__)
RAW_MAP_PATH    = os.path.join(BASE_PATH, "assets/maps/mapa_inicial.tmx")
TEMP_MAP_PATH   = os.path.join(BASE_PATH, "assets/maps/mapa_temp.tmx")

MENU_BACKGROUND = os.path.join(BASE_PATH, "assets/ui/back.png")
EMILLY_SPRITE   = os.path.join(BASE_PATH, "assets/ui/Emilly.png")
BUTTON_FONT     = os.path.join(BASE_PATH, "assets/ui/Minecraft.ttf")
LOGIN_BACKGROUND = os.path.join(BASE_PATH, "assets/ui/medium.png")

TILE_SIZE = 32

# GID no TMX → número da fase
PHASE_TRIGGER_CODES = {
    26: 1,
    13: 2,
    27: 3,
    19: 4,
    25: 5,
    20: 6,
}

# Configurações da API - AJUSTE PARA SUA PORTA
