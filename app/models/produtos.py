from dataclasses import dataclass
from typing import Optional

@dataclass
class Produto:
    id: str
    nome: str
    preco_custo: float
    preco_venda: float
    observacao: Optional[str] = None
    ativo: bool = True

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'preco_custo': f"{self.preco_custo:.2f}",
            'preco_venda': f"{self.preco_venda:.2f}",
            'observacao': self.observacao or '',
            'ativo': str(self.ativo)
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            nome=data['nome'],
            preco_custo=float(data['preco_custo']),
            preco_venda=float(data['preco_venda']),
            observacao=data.get('observacao') or None,
            ativo=str(data.get('ativo', 'True')).lower() == 'true'
        )