from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Fornecedor:
    id: str
    nome: str
    cnpj: str
    telefone: str
    email: Optional[str] = None
    produtos_fornecidos: Optional[List[str]] = None  # IDs dos produtos
    observacoes: Optional[str] = None
    ativo: bool = True

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'telefone': self.telefone,
            'email': self.email or '',
            'produtos_fornecidos': ','.join(self.produtos_fornecidos) if self.produtos_fornecidos else '',
            'observacoes': self.observacoes or '',
            'ativo': str(self.ativo)
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            nome=data['nome'],
            cnpj=data['cnpj'],
            telefone=data['telefone'],
            email=data['email'] or None,
            produtos_fornecidos=data['produtos_fornecidos'].split(',') if data['produtos_fornecidos'] else None,
            observacoes=data['observacoes'] or None,
            ativo=data.get('ativo', 'True').lower() == 'true'
        )