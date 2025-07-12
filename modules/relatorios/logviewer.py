from rich.console import Console
from rich.table import Table
from pathlib import Path

class LogViewer:
    def mostrar_logs(self, dias: int = 1):
        console = Console()
        log_dir = Path("logs")
        
        table = Table(title="Últimas Atividades", show_lines=True)
        table.add_column("Data/Hora", style="cyan")
        table.add_column("Nível", style="magenta")
        table.add_column("Mensagem")
        
        for log_file in sorted(log_dir.glob("*.log"), reverse=True)[:dias]:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f.readlines()[-100:]:  # Últimas 100 linhas
                    parts = line.split(' | ')
                    if len(parts) >= 3:
                        table.add_row(*parts)
        
        console.print(table)