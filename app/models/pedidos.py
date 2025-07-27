from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from app.managers import itens
from app.models.Itens import ItemPedido

@dataclass
class Pedido:
    id: str
    id_cliente: str
    data: datetime
    status: str
    itens: List[ItemPedido] = field(default_factory=list)
    observacoes: str = ''
    data_previsao_entrega: Optional[datetime] = None
    forma_de_pagamento: str = ''
    valor_pago: float = 0.0


    @classmethod
    def from_dict(cls, data: dict, itens: List[ItemPedido] = None) -> "Pedido":
        from app.services.pedidos import parse_data         
        from app.managers.pedidos import PedidoManager
   
        return cls(
            id=data.get('id') or PedidoManager().get_next_id(),
            id_cliente=data["id_cliente"],
            data=parse_data(data.get('data')),
            data_previsao_entrega=parse_data(data.get('data_previsao_entrega')),
            status=data["status"],
            itens=itens or [],
            observacoes=data.get("observacoes", ""),
            forma_de_pagamento=data.get("forma_de_pagamento", ""),
            valor_pago=float(data.get('valor_pago','0.0'))
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'id_cliente': self.id_cliente,
            'data': 
                self.data.isoformat()
                if isinstance(self.data, datetime)
                else str(self.data),
            'status': self.status,
            'observacoes': self.observacoes or '',
            'data_previsao_entrega':
                self.data_previsao_entrega.strftime("%Y-%m-%d")
                if isinstance(self.data_previsao_entrega, datetime)
                else self.data_previsao_entrega or '',
            'forma_de_pagamento': self.forma_de_pagamento,
            'valor_pago': float(self.valor_pago)
        }
    
    @property
    def total(self) -> float:
        return sum(getattr(item, "total", 0.0) for item in self.itens or [])

