import uuid
from core.database import CSVManager
from .models import RegistroAuditoria, TipoEvento
from datetime import datetime

class AuditoriaManager(CSVManager):
    def __init__(self):
        super().__init__('auditoria.csv')
    
    def get_headers(self) -> list:
        return [
            'id',
            'usuario_id',
            'evento',
            'tabela',
            'registro_id',
            'dados_anteriores',
            'dados_novos',
            'timestamp'
        ]
    
    def registrar(self, usuario_id: str, evento: TipoEvento, tabela: str, 
                 registro_id: str, dados_anteriores=None, dados_novos=None):
        registro = RegistroAuditoria(
            id=str(uuid.uuid4()),
            usuario_id=usuario_id,
            evento=evento,
            tabela=tabela,
            registro_id=registro_id,
            dados_anteriores=str(dados_anteriores) if dados_anteriores else None,
            dados_novos=str(dados_novos) if dados_novos else None,
            timestamp=datetime.now()
        )
        self.save(registro.__dict__)