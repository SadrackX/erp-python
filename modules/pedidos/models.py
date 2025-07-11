from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class ItemPedido:
    id_pedido: str
    id_produto: str
    quantidade: int
    preco_unitario: float
    desconto: float = 0.0

    @property
    def total(self) -> float:
        return (self.preco_unitario * self.quantidade) - self.desconto

    def to_dict(self) -> dict:
        return {
            'id_pedido': self.id_pedido,
            'id_produto': self.id_produto,
            'quantidade': str(self.quantidade),
            'preco_unitario': f"{self.preco_unitario:.2f}",
            'desconto': f"{self.desconto:.2f}"
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_pedido=data['id_pedido'],
            id_produto=data['id_produto'],
            quantidade=int(data['quantidade']),
            preco_unitario=float(data['preco_unitario']),
            desconto=float(data.get('desconto', '0'))
        )

@dataclass
class Pedido:
    id: str
    id_cliente: str
    id_forma_pagamento: str
    data: datetime
    status: str  # 'rascunho', 'finalizado', 'cancelado'
    itens: List[ItemPedido]
    observacoes: Optional[str] = None
    desconto_total: float = 0.0
    valor_frete: float = 0.0

    @property
    def total(self) -> float:
        subtotal = sum(item.total for item in self.itens)
        return subtotal - self.desconto_total + self.valor_frete

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'id_cliente': self.id_cliente,
            'id_forma_pagamento': self.id_forma_pagamento,
            'data': self.data.isoformat(),
            'status': self.status,
            'observacoes': self.observacoes or '',
            'desconto_total': f"{self.desconto_total:.2f}",
            'valor_frete': f"{self.valor_frete:.2f}"
        }

    @classmethod
    def from_dict(cls, data: dict, itens: List[ItemPedido] = None):
        return cls(
            id=data['id'],
            id_cliente=data['id_cliente'],
            id_forma_pagamento=data['id_forma_pagamento'],
            data=datetime.fromisoformat(data['data']),
            status=data['status'],
            itens=itens or [],
            observacoes=data.get('observacoes'),
            desconto_total=float(data.get('desconto_total', '0')),
            valor_frete=float(data.get('valor_frete', '0'))
        )