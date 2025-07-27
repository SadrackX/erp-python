from datetime import datetime
from typing import Optional
from app.managers.pedidos import PedidoManager

pedido_manager = PedidoManager()

def verificar_e_atualizar_status_pedidos() -> int:
    """Atualiza automaticamente o status dos pedidos com base na data de entrega"""
    hoje = datetime.now().date()
    alteracoes = 0

    for pedido_data in pedido_manager.get_all():
        status_atual = pedido_data['status']
        data_entrega_str = pedido_data.get('data_previsao_entrega', '')
        data_entrega = None

        if data_entrega_str:
            try:
                data_entrega = datetime.fromisoformat(data_entrega_str).date()
            except ValueError:
                continue

        atualizou = False

        if status_atual not in ['Finalizado', 'Cancelado'] and data_entrega and data_entrega < hoje:
            pedido_data['status'] = 'Atrasado'
            atualizou = True

        if status_atual in ['Orçamento', 'Rascunho'] and data_entrega_str:
            pedido_data['data_previsao_entrega'] = ''
            atualizou = True

        if atualizou:
            pedido_manager.update(pedido_data['id'], pedido_data)
            alteracoes += 1

    return alteracoes

def buscar_por_periodo_entrega(data_inicio: datetime, data_fim: datetime) -> list:
    return [
        pedido for pedido in pedido_manager.buscar_todos()
        if pedido.data_previsao_entrega and data_inicio <= pedido.data_previsao_entrega <= data_fim
    ]

def total_este_mes() -> float:
    hoje = datetime.now()
    return sum(
        pedido.total for pedido in pedido_manager.buscar_todos()
        if pedido.data.month == hoje.month and pedido.data.year == hoje.year
    )

def parse_data(data_str: Optional[str]) -> Optional[datetime]:
            if data_str is None:
                return None
            try:
                # Tenta como ISO (com ou sem hora)
                return datetime.fromisoformat(data_str)
            except ValueError:
                # Tenta como formato customizado (ex: YYYY-MM-DD)
                try:
                    return datetime.strptime(data_str, "%Y-%m-%d")
                except ValueError:
                    return None