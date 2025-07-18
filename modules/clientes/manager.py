import csv
import uuid
from pathlib import Path
from core import logger
from core.auth import AuthManager
from core.database import CSVManager
from modules.auditoria.manager import AuditoriaManager
from modules.auditoria.models import TipoEvento
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
        self.auditoria = AuditoriaManager()
    
    def get_headers(self) -> List[str]:
        return [
            'id',
            'nome',
            'tipo',
            'cpf_cnpj',
            'email',
            'celular',
            'endereco',
            'bairro',
            'cidade',
            'cep',
            'uf',
            'observacoes',
            'ativo'
        ]
    
    def get_next_id(self) -> str:
        clientes = self.get_all()
        if not clientes:
            return '0001'
        max_id = max([int(c['id']) for c in clientes if c['id'].isdigit()], default=0)
        return str(max_id + 1).zfill(4)
    
    def cadastrar_cliente(self, cliente: Cliente) -> str:
        """Garante que cada cliente seja salvo em linha separada"""
        try:
            # Garante que o ID existe
            if not cliente.id:
                cliente.id = self.get_next_id()
            
            # Converte para dict e remove valores None
            #dados = {k: v for k, v in cliente.to_dict().items() if v is not None}
            
            self.save(cliente.to_dict())
            #logger.log(f"Cliente cadastrado - ID: {cliente.id[:8]} | Nome: {cliente.nome}")
            return cliente.id
        except Exception as e:
            logger.log(f"Erro ao cadastrar cliente: {str(e)}", "error")
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
        cliente_antigo = self.buscar_por_id(cliente_id)
        if not cliente_antigo:
            return False

        # Atualiza os dados
        cliente_atualizado = Cliente.from_dict({**cliente_antigo.__dict__, **novos_dados})
        success = self.update(cliente_id, cliente_atualizado.to_dict())

        if success:
            usuario_atual = AuthManager.get_usuario_atual()
            if usuario_atual:  # Só registra se houver usuário logado
                self.auditoria.registrar(
                    usuario_id=usuario_atual.id,
                    evento=TipoEvento.UPDATE,
                    tabela="clientes",
                    registro_id=cliente_id,
                    dados_anteriores=cliente_antigo.to_dict(),
                    dados_novos=cliente_atualizado.to_dict()
                )
        return success
    
    def remover_cliente(self, cliente_id: str) -> bool:
        """Marca cliente como inativo"""
        return self.atualizar_cliente(cliente_id, {'ativo': False})
    
    def total_ativos(self) -> int:
        """Retorna o número total de clientes ativos"""
        return len([
            cliente for cliente in self.buscar_todos() 
            if cliente.ativo
        ])