from datetime import datetime
from app.core.database import CSVManager
from app.managers.itens import ItensPedidoManager
from app.models.Itens import ItemPedido
from app.models.pedidos import Pedido
from typing import List, Optional

class PedidoManager(CSVManager):
    def __init__(self):
        super().__init__('pedidos.csv')
        self.itens_manager = ItensPedidoManager()
    
    def get_headers(self) -> List[str]:
        return [
            'id',
            'id_cliente',
            'data',
            'status',
            'itens',
            'observacoes',
            'data_previsao_entrega',
            'forma_de_pagamento',
            'valor_pago'
        ]
    
    def get_next_id(self) -> str:
        dados = self.get_all()
        if not dados:
            return '0001'
        max_id = max([int(p['id']) for p in dados if p['id'].isdigit()], default=0)
        return str(max_id + 1).zfill(4)
    
    def criar_pedido(self, pedido: Pedido) -> str:
        from app.services.pedidos import atualizar_previsao_entrega
        pedido.id = self.get_next_id()
        pedido.data = datetime.now()
        novos_dados = pedido.to_dict()
        novos_dados.pop('total', None)
        atualizar_previsao_entrega(novos_dados)
        self.save(novos_dados)

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
        from app.services.pedidos import atualizar_previsao_entrega
        status_old = self.buscar_por_id(pedido_id).status
        atualizar_previsao_entrega(novos_dados, status_old)              
        return self.update(pedido_id, novos_dados)
    
    def atualizar_itens_pedido(self, pedido_id: str, novos_itens: List[ItemPedido]) -> bool:
        self.itens_manager.remover_itens_por_pedido(pedido_id)
        for item in novos_itens:
            item.id_pedido = pedido_id
            self.itens_manager.adicionar_item(item)
        return True

    def cancelar_pedido(self, pedido_id: str) -> bool:
        return self.update(pedido_id, {'status': 'Cancelado','data_previsao_entrega':''})

    def finalizar_pedido(self, pedido_id: str, valor_pago: float) -> bool:
        data_new = datetime.now().strftime("%Y-%m-%d %H:%M")
        pedido = self.buscar_por_id(pedido_id).to_dict()
        if pedido['status'] == 'Finalizado':
            data_new = pedido['data_previsao_entrega']
        return self.update(pedido_id, {'status': 'Finalizado','data_previsao_entrega':data_new, 'valor_pago': valor_pago})

    def gerar_pedido(self, pedido_id: str) -> bool:
        return self.update(pedido_id, {'status': 'Rascunho','data_previsao_entrega':''})

