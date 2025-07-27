from rich.panel import Panel
from rich.table import Table
from datetime import datetime

from app.managers.clientes import ClienteManager
from app.managers.financeiro import FinanceiroManager
from app.managers.pedidos import PedidoManager
from app.managers.produtos import ProdutoManager


class Dashboard:
    def mostrar_resumo(self):
        # Obter dados dos managers
        total_clientes = ClienteManager().total_ativos()
        total_pedidos = PedidoManager().total_este_mes()
        receita_pendente = FinanceiroManager().saldo_pendente()
        total_produtos = ProdutoManager().total_ativos()
        
        # Criar tabela
        table = Table(title="Resumo Financeiro", show_header=True, header_style="bold blue")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="magenta")
        
        table.add_row("Clientes Ativos", str(total_clientes))
        table.add_row("Produtos Ativos", str(total_produtos))
        table.add_row("Pedidos Este Mês", f"R$ {total_pedidos:,.2f}")
        table.add_row("A Receber", f"[green]R$ {receita_pendente:,.2f}[/]")
        
        return Panel(table, title="Dashboard Principal")