# auth/user_manager.py

import os
import json
from typing import Dict, Optional
from auth.simple_auth import auth_system

class UserManager:
    """Gerenciador global do estado do usuário"""
    
    _current_user = None
    _current_xp_bar = None
    _current_avatar_path = None
    _current_user_data = None
    
    @classmethod
    def set_current_user(cls, username: str, xp_bar=None, avatar_path=None):
        """Define o usuário atual com todos os dados"""
        cls._current_user = username
        cls._current_xp_bar = xp_bar
        cls._current_avatar_path = avatar_path
        cls._current_user_data = auth_system.get_user_data(username) if username else None
        
        # GARANTE QUE TODOS OS USUÁRIOS TENHAM DIREITO À EMILY COMPLETA
        cls._ensure_emily_character_complete()
        
        print(f"🔐 UserManager: Usuário definido -> {username}")
    
    @classmethod
    def _ensure_emily_character_complete(cls):
        """GARANTE que todos os usuários tenham a Emily com animações completas"""
        try:
            if cls._current_user_data and "character" in cls._current_user_data:
                character_data = cls._current_user_data["character"]
                
                # VERIFICA E CORRIGE ANIMAÇÕES DA EMILY
                required_animations = {
                    "up": "assets/characters/Emillywhite_down.png",
                    "down": "assets/characters/Emillywhite_front.png", 
                    "left": "assets/characters/Emillywhite_left.png",
                    "right": "assets/characters/Emillywhite_right.png"
                }
                
                # Garante que todas as animações existam
                if "animations" not in character_data:
                    character_data["animations"] = {}
                
                animations = character_data["animations"]
                needs_update = False
                
                for direction, default_path in required_animations.items():
                    if direction not in animations or not os.path.exists(animations.get(direction, "")):
                        # Usa o caminho padrão da Emily
                        animations[direction] = default_path
                        needs_update = True
                        print(f"🔄 UserManager: Animação {direction} definida para Emily padrão")
                
                # Garante nome da Emily
                if character_data.get("name") != "Emily":
                    character_data["name"] = "Emily"
                    needs_update = True
                    print("🔄 UserManager: Nome do personagem definido como Emily")
                
                # Se houve atualizações, salva no auth_system
                if needs_update and cls._current_user:
                    try:
                        auth_system.update_user_data(cls._current_user, cls._current_user_data)
                        print("✅ UserManager: Dados da Emily atualizados no auth_system")
                    except Exception as e:
                        print(f"⚠️ UserManager: Não foi possível salvar no auth_system: {e}")
            
            # SE NÃO HÁ DADOS DE PERSONAGEM, CRIA EMILY PADRÃO
            elif cls._current_user_data and "character" not in cls._current_user_data:
                cls._create_default_emily_character()
                
        except Exception as e:
            print(f"❌ UserManager: Erro ao garantir Emily completa: {e}")
    
    @classmethod
    def _create_default_emily_character(cls):
        """Cria personagem Emily padrão para usuário"""
        try:
            default_emily = {
                "name": "Emily",
                "animations": {
                    "up": "assets/characters/Emillywhite_down.png",
                    "down": "assets/characters/Emillywhite_front.png",
                    "left": "assets/characters/Emillywhite_left.png", 
                    "right": "assets/characters/Emillywhite_right.png"
                },
                "position": {"x": 64, "y": 64}
            }
            
            if cls._current_user_data:
                cls._current_user_data["character"] = default_emily
                
                # Tenta salvar no auth_system
                if cls._current_user:
                    try:
                        auth_system.update_user_data(cls._current_user, cls._current_user_data)
                        print("✅ UserManager: Emily padrão criada e salva no auth_system")
                    except Exception as e:
                        print(f"⚠️ UserManager: Não foi possível salvar Emily no auth_system: {e}")
            
            print("🆕 UserManager: Personagem Emily padrão criado")
            
        except Exception as e:
            print(f"❌ UserManager: Erro ao criar Emily padrão: {e}")
    
    @classmethod
    def get_current_user(cls) -> Optional[str]:
        """Retorna o usuário atual"""
        return cls._current_user
    
    @classmethod
    def get_current_xp_bar(cls):
        """Retorna a XP bar atual"""
        return cls._current_xp_bar
    
    @classmethod
    def get_current_avatar_path(cls):
        """Retorna o avatar atual"""
        return cls._current_avatar_path
    
    @classmethod
    def get_current_user_data(cls):
        """Retorna os dados do usuário atual - GARANTE EMILY COMPLETA"""
        # Sempre verifica se os dados estão completos antes de retornar
        if cls._current_user_data and "character" not in cls._current_user_data:
            cls._create_default_emily_character()
        
        return cls._current_user_data
    
    @classmethod
    def get_character_data_safe(cls):
        """Retorna dados do personagem com GARANTIA de Emily completa"""
        user_data = cls.get_current_user_data()
        
        if user_data and "character" in user_data:
            return user_data["character"]
        else:
            # Retorna Emily padrão se não houver dados
            return {
                "name": "Emily",
                "animations": {
                    "up": "assets/characters/Emillywhite_down.png",
                    "down": "assets/characters/Emillywhite_front.png",
                    "left": "assets/characters/Emillywhite_left.png",
                    "right": "assets/characters/Emillywhite_right.png"
                },
                "position": {"x": 64, "y": 64}
            }
    
    @classmethod
    def update_user_data(cls):
        """Atualiza dados do usuário do auth_system"""
        if cls._current_user:
            cls._current_user_data = auth_system.get_user_data(cls._current_user)
            # GARANTE Emily completa após atualização
            cls._ensure_emily_character_complete()
    
    @classmethod
    def clear_current_user(cls):
        """Limpa o usuário atual"""
        cls._current_user = None
        cls._current_xp_bar = None
        cls._current_avatar_path = None
        cls._current_user_data = None
        print("🔐 UserManager: Usuário limpo")
    
    @classmethod
    def validate_character_images(cls):
        """VALIDA que todas as imagens da Emily existem e são acessíveis"""
        try:
            character_data = cls.get_character_data_safe()
            animations = character_data.get("animations", {})
            
            missing_images = []
            for direction, image_path in animations.items():
                if not os.path.exists(image_path):
                    missing_images.append(f"{direction}: {image_path}")
                    print(f"❌ UserManager: Imagem faltando - {direction}: {image_path}")
            
            if missing_images:
                print(f"⚠️ UserManager: {len(missing_images)} imagens da Emily faltando")
                # Tenta corrigir automaticamente
                cls._ensure_emily_character_complete()
            else:
                print("✅ UserManager: Todas as imagens da Emily estão presentes")
                
            return len(missing_images) == 0
            
        except Exception as e:
            print(f"❌ UserManager: Erro ao validar imagens da Emily: {e}")
            return False

# Instância global
user_manager = UserManager()