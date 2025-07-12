from enum import Enum
from dataclasses import dataclass

class NivelAcesso(Enum):
    ADMIN = "admin"
    GERENTE = "gerente"
    OPERADOR = "operador"
    VISITANTE = "visitante"

@dataclass
class Usuario:
    id: str
    nome: str
    email: str
    senha_hash: str
    nivel_acesso: NivelAcesso  # Agora garantido que será o enum
    ativo: bool = True

    def __post_init__(self):
        # Garante que nivel_acesso seja convertido para enum
        if isinstance(self.nivel_acesso, str):
            self.nivel_acesso = NivelAcesso(self.nivel_acesso)