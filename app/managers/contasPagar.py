from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from app.core.database import CSVManager
from app.models.contasPagar import ContasPagar

class contasPagarManager(CSVManager):
    def __init__(self):
        super().__init__('contasPagar.csv')        
    
    def get_headers(self) -> List[str]:
        return [
            'id',
            'status',
            'descricao',
            'valor',
            'data_vencimento',
            'data_pagamento',
            'recorrencia'
        ]
    
    def get_next_id(self) -> str:
        dados = self.get_all()
        if not dados:
            return '0001'
        max_id = max([int(p['id']) for p in dados if p['id'].isdigit()], default=0)
        return str(max_id + 1).zfill(4)
    
    def cadastrar(self, dados: ContasPagar) -> str:
        dados.id = self.get_next_id()
        self.save(dados.to_dict())
        return dados.id
    
    def buscar_todos(self) -> List[ContasPagar]:
        return [ContasPagar.from_dict(f) for f in self.get_all()]
    
    def buscar_por_id(self, dados_id: str) -> Optional[ContasPagar]:
        dados = self.find_by_id(dados_id)
        return ContasPagar.from_dict(dados) if dados else None
    
    def atualizar(self, dados_id: str, novos_dados: dict) -> bool:
        dados = self.buscar_por_id(dados_id)
        if not dados:
            return False        
        for campo, valor in novos_dados.items():
            if hasattr(dados, campo):
                setattr(dados, campo, valor)        
        return self.update(dados_id, dados.to_dict())