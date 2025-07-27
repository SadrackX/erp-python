from enum import Enum
from dataclasses import dataclass
from datetime import date

class TipoMovimento(Enum):
    RECEITA = "R"
    DESPESA = "D"

@dataclass
class MovimentoFinanceiro:
    id: str
    tipo: TipoMovimento
    valor: float
    descricao: str
    data_vencimento: date
    data_pagamento: date = None
    pago: bool = False