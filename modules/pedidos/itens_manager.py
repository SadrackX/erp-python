import csv
from core.database import CSVManager
from typing import List
from .models import ItemPedido

class ItensPedidoManager(CSVManager):
    def __init__(self):
        super().__init__('pedido_itens.csv')
    
    def get_headers(self) -> List[str]:
        return [
            'id_item',
            'id_pedido',
            'id_produto',
            'quantidade',
            'preco_unitario',
            'desconto'
        ]
    
    def get_next_id(self) -> str:
        itens = self.get_all()
        if not itens:
            return '0001'
        max_id = max([int(i['id_item']) for i in itens if i.get('id_item', '').isdigit()], default=0)
        return str(max_id + 1).zfill(4)
    
    def adicionar_item(self, item: ItemPedido) -> None:
        # Adiciona id_item sequencial
        d = item.to_dict()
        d['id_item'] = self.get_next_id()
        self.save(d)
    
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