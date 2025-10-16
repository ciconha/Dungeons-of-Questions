# auth/simple_auth.py

import json
import os
import requests
from typing import Dict, Optional
from urllib.parse import urlparse

USER_DATA_FILE = "data/users.json"

class SimpleAuth:
    def __init__(self):
        self.users: Dict = {}
        self.load_users()
    
    def load_users(self):
        """Carrega usuários do arquivo JSON"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            else:
                # Cria diretório se não existir
                os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
                self.users = {}
                self.save_users()
        except Exception as e:
            print(f"❌ Erro ao carregar usuários: {e}")
            self.users = {}
    
    def save_users(self):
        """Salva usuários no arquivo JSON"""
        try:
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar usuários: {e}")
    
    def user_exists(self, username: str) -> bool:
        """Verifica se usuário existe"""
        return username.lower() in [u.lower() for u in self.users.keys()]
    
    def is_valid_url(self, url: str) -> bool:
        """Verifica se a URL é válida"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def download_avatar(self, url: str, username: str) -> Optional[str]:
        """Faz download do avatar da URL e salva localmente"""
        try:
            if not self.is_valid_url(url):
                return None
                
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Verifica se é uma imagem
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return None
            
            # Cria diretório de avatares se não existir
            avatar_dir = "data/avatars"
            os.makedirs(avatar_dir, exist_ok=True)
            
            # Determina extensão do arquivo
            ext = '.jpg'  # padrão
            if 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'jpeg' in content_type:
                ext = '.jpeg'
            elif 'webp' in content_type:
                ext = '.webp'
            
            # Salva arquivo
            filename = f"{username}{ext}"
            filepath = os.path.join(avatar_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Avatar baixado: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Erro ao baixar avatar: {e}")
            return None
    
    def register_user(self, username: str, password: str, nome: str, avatar_url: str = None, character_data: dict = None) -> bool:
        """Registra novo usuário com URL do avatar e dados do personagem"""
        if self.user_exists(username):
            return False
        
        avatar_path = None
        if avatar_url and self.is_valid_url(avatar_url):
            avatar_path = self.download_avatar(avatar_url, username)
        
        # Dados padrão do personagem se não for fornecido
        if not character_data:
            character_data = {
                "name": "Emily",
                "sprite": "assets/ui/Emilly.png",
                "game_sprite": "assets/characters/Emillywhite.png"  # Usando o caminho que você forneceu
            }
        
        self.users[username] = {
            "nome": nome,
            "password": password,
            "avatar_path": avatar_path,
            "avatar_url": avatar_url,
            "xp": 0,
            "level": 1,
            "max_xp": 100,  # XP máxima inicial
            "character": character_data,  # Salva dados do personagem escolhido
            "campaign_progress": {
                "fase_atual": 1,
                "fases": {
                    1: "liberada",
                    2: "bloqueada", 
                    3: "bloqueada",
                    4: "bloqueada",
                    5: "bloqueada",
                    6: "bloqueada"
                }
            }
        }
        self.save_users()
        return True
    
    def authenticate(self, username: str, password: str) -> bool:
        """Autentica usuário"""
        if not self.user_exists(username):
            return False
        
        # Encontra o usuário (case insensitive)
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if not actual_username:
            return False
        
        return self.users[actual_username]["password"] == password
    
    def get_user_data(self, username: str) -> Optional[Dict]:
        """Obtém dados do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            return self.users[actual_username]
        return None
    
    def update_user_xp(self, username: str, xp: int, level: int):
        """Atualiza XP e nível do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            self.users[actual_username]["xp"] = xp
            self.users[actual_username]["level"] = level
            # Atualiza XP máxima baseada no nível
            self.users[actual_username]["max_xp"] = self._calculate_max_xp(level)
            self.save_users()
            return True
        return False
    
    def update_user_character(self, username: str, character_data: dict):
        """Atualiza o personagem do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            self.users[actual_username]["character"] = character_data
            self.save_users()
            return True
        return False
    
    def _calculate_max_xp(self, level: int) -> int:
        """Calcula XP máxima para o nível (progressão exponencial)"""
        # Fórmula: 100 * level^1.5 (cresce mais rápido)
        return int(100 * (level ** 1.5))

# Instância global do auth
auth_system = SimpleAuth()