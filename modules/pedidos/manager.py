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
    
    def criar_pedido(self, pedido: Pedido) -> str:
        """Cria um novo pedido e retorna o ID"""
        pedido.id = str(uuid.uuid4())
        pedido.data = datetime.now()
        self.save(pedido.to_dict())
        
        for item in pedido.itens:
            self.itens_manager.adicionar_item(item)
        
        return pedido.id
    
    def buscar_por_id(self, pedido_id: str) -> Optional[Pedido]:
        """Busca um pedido completo com seus itens"""
        pedido_data = self.find_by_id(pedido_id)
        if not pedido_data:
            return None
        
        itens = self.itens_manager.buscar_itens_por_pedido(pedido_id)
        return Pedido.from_dict(pedido_data, itens)
    
    def buscar_todos(self) -> List[Pedido]:
        """Retorna todos os pedidos com seus itens"""
        pedidos = []
        for pedido_data in self.get_all():
            itens = self.itens_manager.buscar_itens_por_pedido(pedido_data['id'])
            pedidos.append(Pedido.from_dict(pedido_data, itens))
        return pedidos
    
    def atualizar_pedido(self, pedido_id: str, novos_dados: dict) -> bool:
        """Atualiza os dados do pedido (não inclui itens)"""
        return self.update(pedido_id, novos_dados)
    
    def atualizar_itens_pedido(self, pedido_id: str, novos_itens: List[ItemPedido]) -> bool:
        """Substitui todos os itens de um pedido"""
        self.itens_manager.remover_itens_por_pedido(pedido_id)
        for item in novos_itens:
            item.id_pedido = pedido_id
            self.itens_manager.adicionar_item(item)
        return True
    
    def cancelar_pedido(self, pedido_id: str) -> bool:
        """Marca um pedido como cancelado"""
        return self.update(pedido_id, {'status': 'cancelado'})