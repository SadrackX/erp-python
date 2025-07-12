from rich.console import Console
from rich.table import Table
from .manager import AuditoriaManager

console = Console()

def mostrar_historico(tabela: str = None, registro_id: str = None):
    manager = AuditoriaManager()
    registros = manager.get_all()
    
    table = Table(title="Histórico de Alterações")
    table.add_column("Data", style="cyan")
    table.add_column("Usuário")
    table.add_column("Evento")
    table.add_column("Tabela")
    table.add_column("Registro")
    table.add_column("Detalhes")
    
    for reg in sorted(registros, key=lambda x: x['timestamp'], reverse=True):
        if (tabela and reg['tabela'] != tabela) or (registro_id and reg['registro_id'] != registro_id):
            continue
            
        table.add_row(
            reg['timestamp'],
            reg['usuario_id'][:8],
            reg['evento'],
            reg['tabela'],
            reg['registro_id'][:8],
            f"Antes: {reg['dados_anteriores']}\nDepois: {reg['dados_novos']}" if reg['dados_anteriores'] else "-"
        )
    
    console.print(table)