from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class TipoEvento(Enum):
    CREATE = "Criação"
    UPDATE = "Atualização"
    DELETE = "Remoção"
    LOGIN = "Login"
    LOGOUT = "Logout"

@dataclass
class RegistroAuditoria:
    id: str
    usuario_id: str
    evento: TipoEvento
    tabela: str
    registro_id: str
    dados_anteriores: dict = None
    dados_novos: dict = None
    timestamp: datetime = None