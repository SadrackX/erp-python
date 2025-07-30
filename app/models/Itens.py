from dataclasses import dataclass
from typing import Optional

@dataclass
class ItemPedido:
    id_pedido: str
    nome: str
    quantidade: int
    preco_unitario: float

    @property
    def total(self) -> float:
        return self.quantidade * self.preco_unitario

    @classmethod
    def from_dict(cls, data: dict) -> "ItemPedido":
        return cls(
            id_pedido=data["id_pedido"],
            nome=data.get("nome",'').upper(),
            quantidade=int(data["quantidade"]),
            preco_unitario=float(data["preco_unitario"]),
        )

    def to_dict(self) -> dict:
        return {
            "id_pedido": self.id_pedido,
            "nome": self.nome,
            "quantidade": str(self.quantidade),
            "preco_unitario": f"{self.preco_unitario:.2f}",
        }
