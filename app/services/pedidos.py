from datetime import datetime, timedelta
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

        if status_atual in ['Orçamento', 'Rascunho', 'Cancelado'] and data_entrega_str:
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
                
def definir_prazo_entrega(self, pedido_id: str, dias_uteis: int = None, data_manual: datetime = None) -> bool:
        """Define a previsão de entrega por dias úteis ou data fixa"""
        pedido = pedido_manager.buscar_por_id(pedido_id)
        if not pedido:
            return False
    
        if data_manual:
            pedido.data_previsao_entrega = data_manual
        elif dias_uteis:
            calcular_previsao_entrega(self,dias_uteis)
        else:
            calcular_previsao_entrega(self)  # Usa o padrão (5 dias)
    
        return PedidoManager.atualizar_pedido(self,pedido_id=pedido_id, novos_dados=self)

def calcular_previsao_entrega(self, dias_uteis: int = 5):
        """
        Calcula a data de previsão de entrega somando dias úteis à data do pedido.
        Por padrão, considera 5 dias úteis.
        """
        def adicionar_dias_uteis(data_inicial, qtd_dias):
            data = data_inicial
            dias_adicionados = 0
            while dias_adicionados < qtd_dias:
                data += timedelta(days=1)
                if data.weekday() < 5:  # Segunda (0) a sexta (4)
                    dias_adicionados += 1
            return data

        self.data_previsao_entrega = adicionar_dias_uteis(self.data, dias_uteis)