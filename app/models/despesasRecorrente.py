from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DespesasRecorrente:
    id: str = ''
    status: str = ''
    descricao: str = ''
    valor: float = 0.0
    dia_vencimento: int = 0
    recorrencia: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        try:                        
            return cls(
                id=data.get('id', ''),
                status=data.get('status', 'Ativo'),
                descricao=data.get('descricao', ''),
                valor=float(data.get('valor', 0.0)),
                dia_vencimento=int(data.get('dia_vencimento')),
                recorrencia=data.get('recorrencia')
            )
        except Exception as e:
            print(f"Erro ao criar despesa recorrente: {e}")
            return None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'status': self.status,
            'descricao': self.descricao,
            'valor': self.valor,
            'dia_vencimento': self.dia_vencimento,
            'recorrencia': self.recorrencia
        }