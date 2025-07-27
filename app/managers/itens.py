import csv
import os
from app.core.database import CSVManager
from app.models.Itens import ItemPedido
from typing import List

class ItensPedidoManager(CSVManager):
    def __init__(self):
        super().__init__('pedido_itens.csv')
    
    def get_headers(self) -> List[str]:
        return [
            'id_pedido',
            'nome',
            'quantidade',
            'preco_unitario'
        ]
    
    """ def get_next_id(self) -> str:
        itens = self.get_all()
        if not itens:
            return '0001'
        max_id = max([int(i['id_item']) for i in itens if i.get('id_item', '').isdigit()], default=0)
        return str(max_id + 1).zfill(4) """
    
    def adicionar_item(self, item: ItemPedido) -> None:
        # Adiciona id_item sequencial
        d = item.to_dict()
        #d['id_item'] = self.get_next_id()
        self.save(d)
    
    def buscar_itens_por_pedido(self, pedido_id: str) -> List[ItemPedido]:
        itens = []
        for item in self.get_all():
            if item['id_pedido'] == pedido_id:
                itens.append(ItemPedido.from_dict(item))
        return itens
    
    def remover_itens_por_pedido(self, pedido_id: str) -> bool:
        registros = self.get_all()
        restantes = [r for r in registros if r['id_pedido'] != pedido_id]

        with open(self.filepath, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_headers())
            writer.writeheader()
            for r in restantes:
                writer.writerow(r)

        return len(registros) > len(restantes)

    def save(self, item: ItemPedido) -> None:
        with open(self.filepath, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_headers())
            file_is_empty = os.stat(self.filepath).st_size == 0
            if file_is_empty:
                writer.writeheader()
            writer.writerow(item)