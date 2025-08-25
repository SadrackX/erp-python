from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Despesas:
    id: str = ''
    status: str = ''
    descricao: str = ''
    valor: float = 0.0
    data_vencimento: Optional[datetime] = None
    data_pagamento: Optional[datetime] = None
    parcela_atual: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict):
        try:
            # Conversão segura de datas
            data_vencimento = None
            if 'data_vencimento' in data and data['data_vencimento']:
                data_vencimento = datetime.strptime(data['data_vencimento'], "%Y-%m-%d")
            
            data_pagamento = None
            if 'data_pagamento' in data and data['data_pagamento']:
                data_pagamento = datetime.strptime(data['data_pagamento'], "%Y-%m-%d")
            
            # Tratamento de campos numéricos opcionais
            parcela_atual = int(data['parcela_atual']) if 'parcela_atual' in data and data['parcela_atual'] else None
            
            return cls(
                id=data.get('id', ''),
                status=data.get('status', 'Pendente'),
                descricao=data.get('descricao', ''),
                valor=float(data.get('valor', 0.0)),
                data_vencimento=data_vencimento,
                data_pagamento=data_pagamento,
                parcela_atual=parcela_atual
            )
        except Exception as e:
            print(f"Erro ao criar despesa a pagar: {e}")
            return None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'status': self.status,
            'descricao': self.descricao,
            'valor': self.valor,
            'data_vencimento': self.data_vencimento.strftime("%Y-%m-%d") if self.data_vencimento else '',
            'data_pagamento': self.data_pagamento.strftime("%Y-%m-%d") if self.data_pagamento else '',
            'parcela_atual': self.parcela_atual
        }