# utils/avatar_utils.py
import arcade
import os
import shutil
from PIL import Image
import tempfile

class AvatarManager:
    def __init__(self, avatars_dir="assets/avatars"):
        self.avatars_dir = avatars_dir
        self.ensure_avatars_dir()
        
    def ensure_avatars_dir(self):
        """Garante que o diretório de avatars existe"""
        if not os.path.exists(self.avatars_dir):
            os.makedirs(self.avatars_dir)
            print(f"✅ Criado diretório: {self.avatars_dir}")
    
    def process_and_save_avatar(self, source_path, username):
        """Processa e salva o avatar de forma segura"""
        try:
            if not os.path.exists(source_path):
                return None, "Arquivo não encontrado"
            
            # Verifica se é imagem válida
            try:
                with Image.open(source_path) as img:
                    img.verify()
            except Exception as e:
                return None, f"Imagem inválida: {e}"
            
            # Gera nome único para o arquivo
            extension = os.path.splitext(source_path)[1].lower()
            if extension not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                extension = '.png'  # Fallback
            
            avatar_filename = f"{username}_{hash(username)}{extension}"
            avatar_path = os.path.join(self.avatars_dir, avatar_filename)
            
            # Processa a imagem (redimensiona e converte)
            with Image.open(source_path) as img:
                # Converte para RGB se necessário
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
                
                # Redimensiona para tamanho padrão (mantém aspect ratio)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                # Salva processada
                img.save(avatar_path, 'PNG' if extension == '.png' else 'JPEG')
            
            print(f"✅ Avatar salvo: {avatar_path}")
            return avatar_path, None
            
        except Exception as e:
            return None, f"Erro ao processar avatar: {e}"
    
    def load_avatar_texture(self, avatar_path):
        """Carrega textura do avatar de forma segura"""
        try:
            if not avatar_path or not os.path.exists(avatar_path):
                return None
                
            return arcade.load_texture(avatar_path)
        except Exception as e:
            print(f"❌ Erro ao carregar textura: {e}")
            return None
    
    def draw_avatar_safe(self, center_x, center_y, avatar_path, size=80):
        """Desenha avatar de forma segura com fallbacks"""
        try:
            texture = self.load_avatar_texture(avatar_path)
            if texture:
                # Método mais compatível com diferentes versões do arcade
                arcade.draw_texture_rectangle(
                    center_x, center_y, 
                    size, size, 
                    texture
                )
                return True
        except Exception as e:
            print(f"❌ Erro ao desenhar avatar: {e}")
        
        # Fallback: avatar padrão
        self.draw_default_avatar(center_x, center_y, size)
        return False
    
    def draw_default_avatar(self, center_x, center_y, size=80):
        """Desenha avatar padrão"""
        # Círculo de fundo
        arcade.draw_circle_filled(center_x, center_y, size/2, arcade.color.DARK_GRAY)
        arcade.draw_circle_filled(center_x, center_y, size/2 - 5, arcade.color.LIGHT_GRAY)
        
        # Ícone padrão
        arcade.draw_text(
            "🎮", center_x, center_y,
            arcade.color.WHITE, size//3,
            anchor_x="center", anchor_y="center"
        )
        
        # Borda
        arcade.draw_circle_outline(
            center_x, center_y, size/2, 
            arcade.color.GOLD, 3
        )