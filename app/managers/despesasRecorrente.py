from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from app.core.database import CSVManager
from app.models.despesasRecorrente import DespesasRecorrente
from dateutil.relativedelta import relativedelta
import logging

class DespesasRecorrenteManager(CSVManager):
    def __init__(self):
        super().__init__('despesas_recorrente.csv')        
    
    def get_headers(self) -> List[str]:
        return [
            'id',
            'status',
            'descricao',
            'valor',
            'dia_vencimento',        
            'recorrencia'
        ]
    
    def get_next_id(self) -> str:
        dados = self.get_all()
        if not dados:
            return '0001'
        max_id = max([int(p['id']) for p in dados if p['id'].isdigit()], default=0)
        return str(max_id + 1).zfill(4)
    
    def cadastrar(self, dados: DespesasRecorrente) -> str:
        if not dados.descricao or dados.valor <= 0 or not dados.dia_vencimento:
            raise ValueError("Dados inválidos para cadastro")        
        if not dados.id:
            dados.id = self.get_next_id()
        self.save(dados.to_dict())
        return dados.id
    
    def buscar_todos(self) -> List[DespesasRecorrente]:
        dados = []
        for f in self.get_all():
            try:               
                dados.append(DespesasRecorrente().from_dict(f))                
            except Exception as e:
                print(f"Erro ao carregar despesa: {e}. Dados: {f}")
        return dados
    
    def buscar_por_id(self, dados_id: str) -> Optional[DespesasRecorrente]:
        dados = self.find_by_id(dados_id)
        return DespesasRecorrente.from_dict(dados) if dados else None
    
    def atualizar(self, dados_id: str, novos_dados: dict) -> bool:
        dados = self.buscar_por_id(dados_id)
        if not dados:
            return False        
        for campo, valor in novos_dados.items():
            if hasattr(dados, campo):
                setattr(dados, campo, valor)        
        return self.update(dados_id, dados.to_dict())    

    def buscar_por_status(self, status: str) -> List[DespesasRecorrente]:
        return [c for c in self.buscar_todos() if c.status == status]
        
    def excluir(self, dados_id: str) -> bool:
        return self.update(dados_id, {'status': 'Excluido'})