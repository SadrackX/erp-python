import uuid

from core.auth import AuthManager
from core.database import CSVManager
from modules.auditoria.manager import TipoEvento
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
    
    def get_next_id(self) -> str:
        fornecedores = self.get_all()
        if not fornecedores:
            return '0001'
        max_id = max([int(f['id']) for f in fornecedores if f['id'].isdigit()], default=0)
        return str(max_id + 1).zfill(4)
    
    def cadastrar_fornecedor(self, fornecedor: Fornecedor) -> str:
        """Cadastra novo fornecedor e retorna o ID"""
        fornecedor.id = self.get_next_id()
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
        fornecedor_antigo = self.buscar_por_id(fornecedor_id)
        if not fornecedor_antigo:
            return False

        fornecedor_atualizado = Fornecedor.from_dict({**fornecedor_antigo.__dict__, **novos_dados})
        success = self.update(fornecedor_id, fornecedor_atualizado.to_dict())

        if success:
            usuario_atual = AuthManager.get_usuario_atual()
            if usuario_atual:  # Só registra se houver usuário logado
                self.auditoria.registrar(
                    usuario_id=usuario_atual.id,
                    evento=TipoEvento.UPDATE,
                    tabela="fornecedor",
                    registro_id=fornecedor_id,
                    dados_anteriores=fornecedor_antigo.to_dict(),
                    dados_novos=fornecedor_atualizado.to_dict()
                )
        return success
    
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