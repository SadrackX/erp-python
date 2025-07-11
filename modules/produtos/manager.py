from core.database import CSVManager
from .models import Produto
from typing import List, Optional
import uuid

class ProdutoManager(CSVManager):
    def __init__(self):
        super().__init__('produtos.csv')
    
    def get_headers(self) -> list[str]:
        return [
            'id',
            'nome',
            'quantidade',
            'preco_custo',
            'preco_venda',
            'observacao',
            'ativo'
        ]
    
    def cadastrar_produto(self, produto: Produto) -> str:
        """Cadastra um novo produto e retorna o ID"""
        if not produto.id:
            produto.id = str(uuid.uuid4())
        
        try:
            self.save(produto.to_dict())
            return produto.id
        except Exception as e:
            print(f"Erro ao cadastrar produto: {e}")
            return None
    
    def buscar_todos(self) -> List[Produto]:
        """Retorna todos os produtos cadastrados"""
        produtos = []
        for p in self.get_all():
            try:
                # Verifica se todos os campos obrigatórios existem
                required_fields = ['id', 'nome', 'quantidade', 'preco_custo', 'preco_venda']
                if all(field in p for field in required_fields):
                    produtos.append(Produto.from_dict(p))
                else:
                    print(f"Dados incompletos: {p}")
            except Exception as e:
                print(f"Erro ao carregar produto: {e}. Dados: {p}")
        return produtos
    
    def buscar_por_id(self, produto_id: str) -> Optional[Produto]:
        """Busca um produto pelo ID"""
        produto = self.find_by_id(produto_id)
        return Produto.from_dict(produto) if produto else None
    
    def atualizar_produto(self, produto_id: str, novos_dados: dict) -> bool:
        """Atualiza um produto existente"""
        produto = self.buscar_por_id(produto_id)
        if not produto:
            return False
        
        # Atualiza apenas os campos fornecidos
        for campo, valor in novos_dados.items():
            if hasattr(produto, campo):
                setattr(produto, campo, valor)
        
        return self.update(produto_id, produto.to_dict())
    
    def remover_produto(self, produto_id: str) -> bool:
        """Marca um produto como inativo (soft delete)"""
        return self.atualizar_produto(produto_id, {'ativo': False})