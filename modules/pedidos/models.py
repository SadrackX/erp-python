from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta

@dataclass
class ItemPedido:
    id_item: str = ''
    id_pedido: str = ''
    id_produto: str = ''
    quantidade: int = 1
    preco_unitario: float = 0.0
    desconto: float = 0.0

    @property
    def total(self) -> float:
        return (self.preco_unitario * self.quantidade) - self.desconto

    def to_dict(self) -> dict:
        return {
            'id_item': self.id_item,
            'id_pedido': self.id_pedido,
            'id_produto': self.id_produto,
            'quantidade': str(self.quantidade),
            'preco_unitario': f"{self.preco_unitario:.2f}",
            'desconto': f"{self.desconto:.2f}"
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_item=data.get('id_item', ''),
            id_pedido=data.get('id_pedido', ''),
            id_produto=data.get('id_produto', ''),
            quantidade=int(data.get('quantidade', 1)),
            preco_unitario=float(data.get('preco_unitario', 0)),
            desconto=float(data.get('desconto', '0'))
        )



@dataclass
class Pedido:
    id: str
    id_cliente: str
    id_forma_pagamento: str
    data: datetime
    status: str  # 'rascunho', 'finalizado', 'cancelado'
    itens: List[ItemPedido] = field(default_factory=list)
    observacoes: Optional[str] = None
    desconto_total: float = 0.0
    data_previsao_entrega: Optional[datetime] = None  # Novo campo

    def __post_init__(self):
        """Calcula automaticamente a previsão se não for fornecida"""
        if self.data_previsao_entrega is None and self.status != 'rascunho':
            self.calcular_previsao_entrega()

    def definir_prazo_entrega(self, pedido_id: str, dias_uteis: int = None, data_manual: datetime = None) -> bool:
        """Define a previsão de entrega por dias úteis ou data fixa"""
        pedido = self.buscar_por_id(pedido_id)
        if not pedido:
            return False
    
        if data_manual:
            pedido.data_previsao_entrega = data_manual
        elif dias_uteis:
            pedido.calcular_previsao_entrega(dias_uteis)
        else:
            pedido.calcular_previsao_entrega()  # Usa o padrão (5 dias)
    
        return self.update(pedido_id, {'data_previsao_entrega': pedido.data_previsao_entrega.isoformat()})

    @property
    def total(self) -> float:
        subtotal = sum(item.total for item in self.itens)
        return subtotal - self.desconto_total

    def to_dict(self) -> dict:
        dados = {
            'id': self.id,
            'id_cliente': self.id_cliente,
            'id_forma_pagamento': self.id_forma_pagamento,
            'data': self.data.isoformat(),
            'status': self.status,
            'observacoes': self.observacoes or '',
            'desconto_total': f"{self.desconto_total:.2f}",
            'data_previsao_entrega': self.data_previsao_entrega.isoformat() 
                if self.data_previsao_entrega else None
        }
        return {k: v for k, v in dados.items() if v is not None}

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
            data_previsao_entrega=datetime.fromisoformat(data['data_previsao_entrega']) 
                if data.get('data_previsao_entrega') else None
        )