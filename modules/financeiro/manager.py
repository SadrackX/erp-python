from datetime import date
from core.database import CSVManager
from .models import MovimentoFinanceiro, TipoMovimento
import uuid

class FinanceiroManager(CSVManager):
    def __init__(self):
        super().__init__('financeiro.csv')

    def get_headers(self) -> list[str]:
        return [
            'id',
            'tipo',
            'valor',
            'descricao',
            'data_vencimento',
            'data_pagamento',
            'pago'
        ]

    def criar_movimento(self, tipo: TipoMovimento, valor: float, descricao: str,
                       data_vencimento: date, data_pagamento: date = None,
                       pago: bool = False) -> str:
        movimento = MovimentoFinanceiro(
            id=str(uuid.uuid4()),
            tipo=tipo,
            valor=valor,
            descricao=descricao,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            pago=pago
        )
        self.save(movimento.__dict__)
        return movimento.id
    
    def saldo_pendente(self) -> float:
        """Retorna o total a receber"""
        return sum(
            float(movimento['valor'])
            for movimento in self.get_all()
            if movimento['tipo'] == TipoMovimento.RECEITA.value and
            movimento.get('pago', 'False').lower() == 'false'
        )