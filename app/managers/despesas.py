from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from app.core.database import CSVManager
from app.models.despesas import Despesas
from dateutil.relativedelta import relativedelta
import logging

class DespesasManager(CSVManager):
    def __init__(self):
        super().__init__('despesas.csv')        
    
    def get_headers(self) -> List[str]:
        return [
            'id',
            'status',
            'descricao',
            'valor',
            'data_vencimento',
            'data_pagamento',     
            'parcela_atual'
        ]
    
    def get_next_id(self) -> str:
        dados = self.get_all()
        if not dados:
            return '0001'
        max_id = max([int(p['id']) for p in dados if p['id'].isdigit()], default=0)
        return str(max_id + 1).zfill(4)
    
    def cadastrar(self, despesa: Despesas) -> str:
        if not despesa.descricao or despesa.valor <= 0 or not despesa.data_vencimento:
            raise ValueError("Dados inválidos para cadastro")        
        if not despesa.id:
            despesa.id = self.get_next_id()
        self.save(despesa.to_dict())
        return despesa.id
    
    def buscar_todos(self) -> List[Despesas]:
        despesas = []
        for f in self.get_all():
            try:               
                despesas.append(Despesas().from_dict(f))                
            except Exception as e:
                print(f"Erro ao carregar produto: {e}. Dados: {f}")
        return despesas
    
    def buscar_por_id(self, dados_id: str) -> Optional[Despesas]:
        dados = self.find_by_id(dados_id)
        return Despesas.from_dict(dados) if dados else None
    
    def atualizar(self, dados_id: str, novos_dados: dict) -> bool:
        dados = self.buscar_por_id(dados_id)
        if not dados:
            return False        
        for campo, valor in novos_dados.items():
            if hasattr(dados, campo):
                setattr(dados, campo, valor)        
        return self.update(dados_id, dados.to_dict())    

    def buscar_por_status(self, status: str) -> List[Despesas]:
        return [c for c in self.buscar_todos() if c.status == status]
    
    def buscar_proximos_vencimentos(self, dias: int = 7) -> List[Despesas]:
        hoje = datetime.now()
        limite = hoje + timedelta(days=dias)
        return [
            c for c in self.buscar_todos()
            if c.data_vencimento and hoje <= c.data_vencimento <= limite
        ]
    
    def excluir(self, dados_id: str) -> bool:
        return self.update(dados_id, {'status': 'Excluido'})