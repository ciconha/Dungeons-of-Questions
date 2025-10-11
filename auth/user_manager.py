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
        print(f"🔐 UserManager: Usuário definido -> {username}")
    
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
        """Retorna os dados do usuário atual"""
        return cls._current_user_data
    
    @classmethod
    def update_user_data(cls):
        """Atualiza dados do usuário do auth_system"""
        if cls._current_user:
            cls._current_user_data = auth_system.get_user_data(cls._current_user)
    
    @classmethod
    def clear_current_user(cls):
        """Limpa o usuário atual"""
        cls._current_user = None
        cls._current_xp_bar = None
        cls._current_avatar_path = None
        cls._current_user_data = None
        print("🔐 UserManager: Usuário limpo")

# Instância global
user_manager = UserManager()