import csv
import uuid
from pathlib import Path
from core.database import CSVManager
from .models import Cliente
from typing import List, Optional

def __init__(self):
    super().__init__('clientes.csv')
    if not self.filepath.exists():
        with open(self.filepath, 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_headers())
            writer.writeheader()

class ClienteManager(CSVManager):
    def __init__(self):
        super().__init__('clientes.csv')
    
    def get_headers(self) -> List[str]:
        return [
            'id',
            'nome',
            'tipo',
            'cpf_cnpj',
            'email',
            'celular',
            'observacoes',
            'ativo'
        ]
    
    def cadastrar_cliente(self, cliente: Cliente) -> str:
        """Garante que cada cliente seja salvo em linha separada"""
        try:
            # Garante que o ID existe
            if not cliente.id:
                cliente.id = str(uuid.uuid4())
            
            # Converte para dict e remove valores None
            dados = {k: v for k, v in cliente.to_dict().items() if v is not None}
            
            self.save(dados)
            return cliente.id
        except Exception as e:
            print(f"Erro ao cadastrar cliente: {str(e)}")
            return None
    
    def buscar_todos(self) -> List[Cliente]:
        """Versão com debug"""
        clientes = []
        print("DEBUG - Iniciando busca de clientes...")
        
        for data in self.get_all():
            print("DEBUG - Dados brutos do CSV:", data)
            try:
                cliente = Cliente.from_dict(data)
                clientes.append(cliente)
                print("DEBUG - Cliente convertido:", cliente.__dict__)
            except Exception as e:
                print(f"DEBUG - Erro ao converter cliente: {e}")
    
        print(f"DEBUG - Total de clientes encontrados: {len(clientes)}")
        return clientes
    
    def buscar_por_id(self, cliente_id: str) -> Optional[Cliente]:
        """Busca cliente por ID"""
        cliente = self.find_by_id(cliente_id)
        return Cliente.from_dict(cliente) if cliente else None
    
    def atualizar_cliente(self, cliente_id: str, novos_dados: dict) -> bool:
        """Atualiza cliente existente"""
        cliente = self.buscar_por_id(cliente_id)
        if not cliente:
            return False
        
        for campo, valor in novos_dados.items():
            if hasattr(cliente, campo):
                setattr(cliente, campo, valor)
        
        return self.update(cliente_id, cliente.to_dict())
    
    def remover_cliente(self, cliente_id: str) -> bool:
        """Marca cliente como inativo"""
        return self.atualizar_cliente(cliente_id, {'ativo': False})