from typing import Dict
from app.core.database import CSVManager

class EmpresaManager(CSVManager):
    def __init__(self):
        super().__init__('empresa.csv')
    
    def get_headers(self) -> list[str]:
        return [
            'id',
            'nome',
            'cnpj',
            'email',
            'celular',
            'logo_path',
            'cep',
            'endereco',
            'numero',
            'bairro',
            'complemento',
            'cidade',
            'uf'
        ]
    
    def cadastrar_empresa(self, dados: Dict) -> bool:
        """Cadastra uma nova empresa"""
        if not self.get_all():  # Verifica se já existe cadastro
            self.save(dados)
            return True
        return False
    
    def atualizar_dados(self, novos_dados: Dict) -> bool:
        """Atualiza dados da empresa"""
        records = self.get_all()
        if records:
            return self.update(records[0]['id'], novos_dados)
        return False