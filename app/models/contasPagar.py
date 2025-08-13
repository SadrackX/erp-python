from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class ContasPagar:
    id: str    
    status: str
    descricao: str = ''
    valor: float = 0.0
    data_vencimento: Optional[datetime] = None
    data_pagamento: Optional[datetime] = None
    recorrencia: bool = False

    @classmethod
    def from_dict(cls, data: dict):
        """Versão robusta com tratamento de erros"""
        from app.managers.contasPagar import contasPagarManager
        try:
            return cls(
                id=data.get('id', contasPagarManager().get_next_id()),  # Gera novo ID se não existir
                status=data.get('status',''),
                descricao=data.get('descricao',''),
                valor=float(data['valor'],'0.0'),
                data_vencimento=datetime.strptime(data.get('data_vencimento',''), "%Y-%m-%d"),
                data_pagamento=datetime.strptime(data.get('data_pagamento',''), "%Y-%m-%d")
                recorrencia=data['recorrencia',False]
            )
        except Exception as e:
            print(f"Erro ao criar conta a pagar: {e}\nDados: {data}")
            return None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'status':self.status or '',
            'descricao':self.descricao or '',
            'valor':float(self.valor) or 0.0,
            'data_vencimento':self.data_vencimento.strftime("%Y-%m-%d")
                                if isinstance(self.data_vencimento, datetime)
                                else self.data_vencimento or '',
            'data_pagamento':self.data_pagamento.strftime("%Y-%m-%d")
                                if isinstance(self.data_pagamento, datetime)
                                else self.data_pagamento or '',
            'recorrencia': self.recorrencia or False,
        }