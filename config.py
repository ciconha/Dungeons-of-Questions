import os

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT =  720
SCREEN_TITLE  = "RPG da Emilly"

BASE_PATH     = os.path.dirname(__file__)
RAW_MAP_PATH  = os.path.join(BASE_PATH, "assets/maps/mapa_inicial.tmx")
TEMP_MAP_PATH = os.path.join(BASE_PATH, "mapa_temp.tmx")

BUTTON_SHEET   = os.path.join(BASE_PATH, "assets/ui/botao_rpg.png")
BUTTON_FONT    = os.path.join(BASE_PATH, "assets/ui/Minecraft.ttf")

MENU_BACKGROUND = os.path.join(BASE_PATH, "assets/ui/menu_background.jpg")
EMILLY_SPRITE   = os.path.join(BASE_PATH, "assets/ui/Emilly.png")

BUTTON_WIDTH   = 238
BUTTON_HEIGHT  =  64
BUTTON_COLUMNS =   4
BUTTON_COUNT   =   4
