from dataclasses import dataclass
from typing import Optional

@dataclass
class Usuario:
    id: str
    nome: str
    email: str
    nivel_acesso: str  # Ex: "admin", "usuario"

class AuthManager:
    _usuario_atual: Optional[Usuario] = None

    @classmethod
    def set_usuario_atual(cls, usuario: Usuario):
        cls._usuario_atual = usuario

    @classmethod
    def get_usuario_atual(cls) -> Optional[Usuario]:
        return cls._usuario_atual

    @classmethod
    def logout(cls):
        cls._usuario_atual = None