from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta

@dataclass
class ItemPedido:
    id_item: str = ''
    id_pedido: str = ''
    nome: str = ''
    quantidade: int = 1
    preco_unitario: float = 0.0
    data_previsao_entrega: Optional[datetime] = None  # Novo campo
    

    @property
    def total(self) -> float:
        return (self.preco_unitario * self.quantidade)

    def to_dict(self) -> dict:
        return {
            'id_item': self.id_item,
            'id_pedido': self.id_pedido,
            'nome': self.nome,
            'quantidade': str(self.quantidade),
            'preco_unitario': f"{self.preco_unitario:.2f}"
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_item=data.get('id_item', ''),
            id_pedido=data.get('id_pedido', ''),
            nome=data.get('nome', ''),
            quantidade=int(data.get('quantidade', 1)),
            preco_unitario=float(data.get('preco_unitario', 0))
        )



@dataclass
class Pedido:
    def __init__(self, id, id_cliente, data, status, itens, observacoes, desconto_total, data_previsao_entrega, forma_de_pagamento, valor_pago):
        self.id = id
        self.id_cliente = id_cliente
        self.data = data
        self.status = status
        self.itens = itens
        self.observacoes = observacoes
        self.desconto_total = desconto_total
        self.data_previsao_entrega = data_previsao_entrega
        self.forma_de_pagemento = forma_de_pagamento
        self.valor_pago = valor_pago
        #self.total = sum(item.total for item in itens) - desconto_total

    def __post_init__(self):
        """Calcula automaticamente a previsão se não for fornecida"""
        if self.data_previsao_entrega == '' and self.status != 'rascunho':
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
    
        return self.update(pedido_id, {'data_previsao_entrega': pedido.data_previsao_entrega.date()})
    
    def calcular_previsao_entrega(self, dias_uteis: int = 5):
        """
        Calcula a data de previsão de entrega somando dias úteis à data do pedido.
        Por padrão, considera 5 dias úteis.
        """
        def adicionar_dias_uteis(data_inicial, qtd_dias):
            data = data_inicial
            dias_adicionados = 0
            while dias_adicionados < qtd_dias:
                data += timedelta(days=1)
                if data.weekday() < 5:  # Segunda (0) a sexta (4)
                    dias_adicionados += 1
            return data

        self.data_previsao_entrega = adicionar_dias_uteis(self.data, dias_uteis)


    @property
    def total(self) -> float:
        subtotal = sum(item.total for item in self.itens)
        return subtotal - self.desconto_total

    def to_dict(self):
        return {
            'id': self.id,
            'id_cliente': self.id_cliente,
            'data': self.data.isoformat() if isinstance(self.data, datetime) else str(self.data),
            'status': self.status,
            'observacoes': self.observacoes or '',
            'desconto_total': float(self.desconto_total),
            'data_previsao_entrega': self.data_previsao_entrega.strftime("%Y-%m-%d") if isinstance(self.data_previsao_entrega, datetime) else self.data_previsao_entrega or '',
            'forma_de_pagamento': self.forma_de_pagemento,
            'valor_pago': float(self.valor_pago)

        }
        return {k: v for k, v in dados.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict, itens: List[ItemPedido] = None):
        from modules.pedidos.manager import PedidoManager
        # Função auxiliar para converter string para datetime, se necessário
        def parse_data(data_str: Optional[str]) -> Optional[datetime]:
            if data_str is None:
                return None
            try:
                # Tenta como ISO (com ou sem hora)
                return datetime.fromisoformat(data_str)
            except ValueError:
                # Tenta como formato customizado (ex: YYYY-MM-DD)
                try:
                    return datetime.strptime(data_str, "%Y-%m-%d")
                except ValueError:
                    return None

        return cls(
            id = data.get('id') or PedidoManager().get_next_id(),
            id_cliente=data['id_cliente'],
            data=parse_data(data.get('data')) or datetime.now(),
            status=data['status'],
            itens=itens or [],
            observacoes=data.get('observacoes'),
            desconto_total=float(data.get('desconto_total', '0')),
            data_previsao_entrega=parse_data(data.get('data_previsao_entrega')),
            forma_de_pagamento=data.get('forma_de_pagamento'),
            valor_pago=float(data.get('valor_pago','0'))
        )