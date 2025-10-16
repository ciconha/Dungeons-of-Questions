# config2.py - CONFIGURAÇÕES DO MUNDO ABERTO
import os
import random
import hashlib

# ===== CONFIGURAÇÕES DE JANELA =====
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "RPG da Emilly"

# ===== CAMINHOS BASE =====
BASE_PATH = os.path.dirname(__file__)

# ===== ASSETS - MAPAS =====
RAW_MAP_PATH = os.path.join(BASE_PATH, "assets/maps/mapa_inicial.tmx")
TEMP_MAP_PATH = os.path.join(BASE_PATH, "assets/maps/mapa_temp.tmx")

# ===== ASSETS - UI =====
MENU_BACKGROUND = os.path.join(BASE_PATH, "assets/ui/back.png")
EMILLY_SPRITE = os.path.join(BASE_PATH, "assets/ui/Emilly.png")
BUTTON_FONT = os.path.join(BASE_PATH, "assets/ui/Minecraft.ttf")
LOGIN_BACKGROUND = os.path.join(BASE_PATH, "assets/ui/medium.png")
CRYSTAL_IMAGE = os.path.join(BASE_PATH, "assets/ui/cristal.png")

# ===== ASSETS - ÁUDIO =====
LOGIN_MUSIC = os.path.join(BASE_PATH, "assets/sounds/specular_city.mp3")

# ===== MUNDO ABERTO =====
OPEN_WORLD_TILESET = os.path.join(BASE_PATH, "assets/maps/tilesets/Scene Overview.png")
OPEN_WORLD_TEMP_MAP = os.path.join(BASE_PATH, "assets/maps/victorian-preview.tmx")

# ===== TRIGGERS DO MUNDO ABERTO =====
WORLD_TRIGGER_CODES = {
    21: "vila_inicial",
    28: "floresta",
    29: "montanha",
    30: "lago",
    32: "caverna",
    33: "ruinas",
    34: "deserto",
    35: "pantano",
    36: "vulcao",
    37: "cidade",
    38: "castelo",
    39: "torre",
    40: "portal",
    45: "mina",
    46: "templo",
    51: "dungeon_1",
    53: "dungeon_2",
    54: "dungeon_3"
}

# ===== CONFIGURAÇÕES DO MUNDO ABERTO =====
WORLD_TILE_SIZE = 16
WORLD_MAP_WIDTH = 20
WORLD_MAP_HEIGHT = 20

# ===== AVATARS LOCAIS =====
AVATARS_DIR = os.path.join(BASE_PATH, "assets", "avatars")

# Lista de avatares locais - VERIFICANDO QUAIS REALMENTE EXISTEM
def get_available_avatars():
    """Retorna apenas os avatares que realmente existem no sistema de arquivos"""
    avatar_files = [
        "png-transparent-meliodas-the-seven-deadly-sins-anime-anime-cartoon-fictional-character-seven-deadly-sins-thumbnail.png",
        "png-transparent-meliodas-the-seven-deadly-sins-infant-child-nanatsu-no-taizai-child-english-manga-thumbnail.png",
        "png-transparent-meliodas-the-seven-deadly-sins-merlin-king-nanatsu-no-taizai-manga-vertebrate-computer-wallpaper-thumbnail.png",
        "png-transparent-the-seven-deadly-sins-meliodas-sloth-nanatsu-no-taizai-manga-fictional-character-angel-thumbnail.png",
    ]
    
    available = []
    for avatar_file in avatar_files:
        avatar_path = os.path.join(AVATARS_DIR, avatar_file)
        if os.path.exists(avatar_path):
            available.append(avatar_path)
            print(f"✅ Avatar disponível: {avatar_file}")
        else:
            print(f"❌ Avatar não encontrado: {avatar_file}")
    
    return available

# Lista REAL de avatares disponíveis
ANIME_AVATARS = get_available_avatars()

# Fallback garantido
FALLBACK_AVATAR = os.path.join(BASE_PATH, "assets/ui/Emilly.png")
if not os.path.exists(FALLBACK_AVATAR):
    FALLBACK_AVATAR = None

def get_consistent_hash(username: str) -> int:
    """Gera um hash consistente para o username (sempre o mesmo resultado)"""
    # Usar hashlib para hash mais consistente que o hash() built-in
    hash_object = hashlib.md5(username.encode())
    hash_hex = hash_object.hexdigest()
    return int(hash_hex, 16)

def get_random_avatar() -> str:
    """Retorna um avatar local aleatório que existe"""
    if ANIME_AVATARS:
        return random.choice(ANIME_AVATARS)
    elif FALLBACK_AVATAR:
        print("⚠️  Usando fallback: Emilly.png")
        return FALLBACK_AVATAR
    else:
        print("❌ Nenhum avatar disponível!")
        return ""

def get_avatar_by_username(username: str) -> str:
    """Retorna SEMPRE o MESMO avatar para o MESMO usuário"""
    if not ANIME_AVATARS:
        if FALLBACK_AVATAR:
            print(f"⚠️  {username}: Usando fallback (nenhum avatar disponível)")
            return FALLBACK_AVATAR
        else:
            return ""
    
    # Hash consistente para sempre retornar o mesmo avatar
    hash_value = get_consistent_hash(username)
    index = hash_value % len(ANIME_AVATARS)
    selected_avatar = ANIME_AVATARS[index]
    
    avatar_name = os.path.basename(selected_avatar)
    print(f"🎯 Avatar atribuído para '{username}': {avatar_name}")
    
    return selected_avatar

# ===== CONFIGURAÇÕES DO JOGO =====
TILE_SIZE = 32

# ===== SISTEMA DE FASES =====
PHASE_TRIGGER_CODES = {
    26: 1,
    13: 2,
    27: 3,
    19: 4,
    25: 5,
    20: 6,
}

# ===== CONFIGURAÇÕES DA API =====
API_HOST = "127.0.0.1"
API_PORT = 8000
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

# ===== CONFIGURAÇÕES DO MONGODB =====
MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DB_NAME = "rpg_emilly"

# ===== CONFIGURAÇÕES DO JOGADOR =====
PLAYER_START_X = 100
PLAYER_START_Y = 100
PLAYER_SPEED = 5

# ===== CORES DO JOGO (Tema Roxo) =====
COLORS = {
    'PURPLE_DARK': (30, 20, 50),
    'PURPLE_MEDIUM': (70, 40, 100),
    'PURPLE_LIGHT': (120, 80, 200),
    'PURPLE_NEON': (160, 100, 255),
    'PURPLE_CRYSTAL': (180, 120, 255),
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GOLD': (255, 215, 0)
}

# ===== CONFIGURAÇÕES DE XP =====
XP_BASE_REQUIRED = 100  # XP base necessária por nível
XP_MULTIPLIER = 1.0     # Multiplicador de XP (pode ajustar para dificuldade)

# ===== CONFIGURAÇÕES DE FONTE =====
FONT_SIZES = {
    'SMALL': 12,
    'MEDIUM': 16,
    'LARGE': 20,
    'TITLE': 24
}

# ===== CONFIGURAÇÕES DE ÁUDIO =====
SOUND_ENABLED = True
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.7

# ===== CONFIGURAÇÕES DE DESEMPENHO =====
FRAME_RATE = 50
USE_SPATIAL_HASH = True  # Otimização de colisão

# ===== CONFIGURAÇÕES DE DEBUG =====
DEBUG_MODE = False
SHOW_COLLISION_BOXES = False
SHOW_FPS = True

# ===== CONFIGURAÇÕES DE AVATAR =====
AVATAR_SIZE = 58  # Tamanho do avatar no círculo (68px para caber no círculo de 80px)
AVATAR_CIRCLE_RADIUS = 30  # Raio do círculo do avatar

# Verificação inicial
print("🔍 Verificando configurações de avatar...")
print(f"📁 Pasta de avatares: {AVATARS_DIR}")
print(f"✅ Avatares disponíveis: {len(ANIME_AVATARS)}")
if FALLBACK_AVATAR:
    print(f"🔄 Fallback disponível: {os.path.basename(FALLBACK_AVATAR)}")