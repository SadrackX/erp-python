import uuid
from core.database import CSVManager
from .models import Fornecedor
from typing import List, Optional

class FornecedorManager(CSVManager):
    def __init__(self):
        super().__init__('fornecedores.csv')
    
    def get_headers(self) -> List[str]:
        return [
            'id',
            'nome',
            'cnpj',
            'telefone',
            'email',
            'produtos_fornecidos',
            'observacoes',
            'ativo'
        ]
    
    def cadastrar_fornecedor(self, fornecedor: Fornecedor) -> str:
        """Cadastra novo fornecedor e retorna o ID"""
        fornecedor.id = str(uuid.uuid4())
        self.save(fornecedor.to_dict())
        return fornecedor.id
    
    def buscar_todos(self) -> List[Fornecedor]:
        """Retorna todos os fornecedores"""
        return [Fornecedor.from_dict(f) for f in self.get_all()]
    
    def buscar_por_id(self, fornecedor_id: str) -> Optional[Fornecedor]:
        """Busca fornecedor por ID"""
        fornecedor = self.find_by_id(fornecedor_id)
        return Fornecedor.from_dict(fornecedor) if fornecedor else None
    
    def atualizar_fornecedor(self, fornecedor_id: str, novos_dados: dict) -> bool:
        """Atualiza fornecedor existente"""
        fornecedor = self.buscar_por_id(fornecedor_id)
        if not fornecedor:
            return False
        
        for campo, valor in novos_dados.items():
            if hasattr(fornecedor, campo):
                setattr(fornecedor, campo, valor)
        
        return self.update(fornecedor_id, fornecedor.to_dict())
    
    def adicionar_produto(self, fornecedor_id: str, produto_id: str) -> bool:
        """Adiciona um produto à lista de fornecidos"""
        fornecedor = self.buscar_por_id(fornecedor_id)
        if not fornecedor:
            return False
        
        if not fornecedor.produtos_fornecidos:
            fornecedor.produtos_fornecidos = []
        
        if produto_id not in fornecedor.produtos_fornecidos:
            fornecedor.produtos_fornecidos.append(produto_id)
            return self.update(fornecedor_id, fornecedor.to_dict())
        
        return False