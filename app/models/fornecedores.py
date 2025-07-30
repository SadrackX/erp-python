from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Fornecedor:
    id: str
    nome: str
    cnpj: str
    telefone: str
    email: Optional[str] = None
    produtos_fornecidos: Optional[str] = None  # IDs dos produtos
    observacoes: Optional[str] = None
    ativo: bool = True

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'telefone': self.telefone,
            'email': self.email or '',
            'produtos_fornecidos': self.produtos_fornecidos or '',
            'observacoes': self.observacoes or '',
            'ativo': str(self.ativo)
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            nome=data.get('nome','').upper(),
            cnpj=data['cnpj'],
            telefone=data['telefone'],
            email=data.get('email','').upper() or None,
            produtos_fornecidos=data.get('produtos_fornecidos','').upper() or None,
            observacoes=data.get('observacoes','').upper() or None,
            ativo=str(data.get('ativo', 'True')).lower() == 'true'
        )