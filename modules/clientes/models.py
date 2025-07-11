from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import uuid

@dataclass
class Cliente:
    id: str
    nome: str
    tipo: str  # 'PF' ou 'PJ'
    cpf_cnpj: str
    email: Optional[str] = None
    celular: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: bool = True

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'cpf_cnpj': self.cpf_cnpj,
            'email': self.email or '',
            'celular': self.celular or '',
            'observacoes': self.observacoes or '',
            'ativo': str(self.ativo)
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Versão robusta com tratamento de erros"""
        try:
            return cls(
                id=data.get('id', str(uuid.uuid4())),  # Gera novo ID se não existir
                nome=data.get('nome', ''),
                tipo=data.get('tipo', 'PF'),
                cpf_cnpj=data.get('cpf_cnpj', ''),
                email=data.get('email'),
                celular=data.get('celular'),
                observacoes=data.get('observacoes'),
                ativo=str(data.get('ativo', 'True')).lower() == 'true'
            )
        except Exception as e:
            print(f"Erro ao criar cliente: {e}\nDados: {data}")
            return None