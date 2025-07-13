import uuid
from datetime import datetime
from core.database import CSVManager
from .models import Pedido, ItemPedido
from .itens_manager import ItensPedidoManager
from typing import List, Optional

class PedidoManager(CSVManager):
    def __init__(self):
        super().__init__('pedidos.csv')
        self.itens_manager = ItensPedidoManager()
    
    def get_headers(self) -> List[str]:
        return [
            'id',
            'id_cliente',
            'id_forma_pagamento',
            'data',
            'status',
            'observacoes',
            'desconto_total',
            'valor_frete'
        ]
    
    def get_next_id(self) -> str:
        pedidos = self.get_all()
        if not pedidos:
            return '0001'
        max_id = max([int(p['id']) for p in pedidos if p['id'].isdigit()], default=0)
        return str(max_id + 1).zfill(4)
    
    def criar_pedido(self, pedido: Pedido) -> str:
        pedido.id = self.get_next_id()
        pedido.data = datetime.now()
        self.save(pedido.to_dict())
        for item in pedido.itens:
            item.id_pedido = pedido.id
            self.itens_manager.adicionar_item(item)
        return pedido.id
    
    def buscar_por_id(self, pedido_id: str) -> Optional[Pedido]:
        pedido_data = self.find_by_id(pedido_id)
        if not pedido_data:
            return None
        itens = self.itens_manager.buscar_itens_por_pedido(pedido_id)
        return Pedido.from_dict(pedido_data, itens)
    
    def buscar_todos(self) -> List[Pedido]:
        pedidos = []
        for pedido_data in self.get_all():
            itens = self.itens_manager.buscar_itens_por_pedido(pedido_data['id'])
            pedidos.append(Pedido.from_dict(pedido_data, itens))
        return pedidos
    
    def atualizar_pedido(self, pedido_id: str, novos_dados: dict) -> bool:
        return self.update(pedido_id, novos_dados)
    
    def atualizar_itens_pedido(self, pedido_id: str, novos_itens: List[ItemPedido]) -> bool:
        self.itens_manager.remover_itens_por_pedido(pedido_id)
        for item in novos_itens:
            item.id_pedido = pedido_id
            self.itens_manager.adicionar_item(item)
        return True
    
    def cancelar_pedido(self, pedido_id: str) -> bool:
        return self.update(pedido_id, {'status': 'cancelado'})
    
    def total_este_mes(self) -> float:
        """Retorna o valor total de pedidos deste mês"""
        hoje = datetime.now()
        return sum(
            pedido.total for pedido in self.buscar_todos()
            if pedido.data.month == hoje.month and pedido.data.year == hoje.year
        )