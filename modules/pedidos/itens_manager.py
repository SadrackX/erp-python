import csv
from core.database import CSVManager
from typing import List
from .models import ItemPedido

class ItensPedidoManager(CSVManager):
    def __init__(self):
        super().__init__('pedido_itens.csv')
    
    def get_headers(self) -> List[str]:
        return [
            'id_pedido',
            'id_produto',
            'quantidade',
            'preco_unitario',
            'desconto'
        ]
    
    def adicionar_item(self, item: ItemPedido) -> None:
        self.save(item.to_dict())
    
    def buscar_itens_por_pedido(self, pedido_id: str) -> List[ItemPedido]:
        itens = []
        for item in self.get_all():
            if item['id_pedido'] == pedido_id:
                itens.append(ItemPedido.from_dict(item))
        return itens
    
    def remover_itens_por_pedido(self, pedido_id: str) -> None:
        itens_restantes = [item for item in self.get_all() if item['id_pedido'] != pedido_id]
        
        with open(self.filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_headers())
            writer.writeheader()
            writer.writerows(itens_restantes)