from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table

class LogEntry:
    def __init__(self, data: str, nivel: str, mensagem: str):
        self.data = data
        self.nivel = nivel
        self.mensagem = mensagem

class LogViewer:
    def mostrar_logs(self, dias: int = 1) -> List[LogEntry]:
        console = Console()
        log_dir = Path("logs")
        logs = []

        # Tabela para exibição no terminal
        table = Table(title="Últimas Atividades", show_lines=True)
        table.add_column("Data/Hora", style="cyan")
        table.add_column("Nível", style="magenta")
        table.add_column("Mensagem")

        # Filtra os últimos N arquivos de log
        for log_file in sorted(log_dir.glob("*.log"), reverse=True)[:dias]:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f.readlines()[-100:]:  # Últimas 100 linhas
                    parts = line.strip().split(' | ')
                    if len(parts) >= 3:
                        data, nivel, mensagem = parts
                        logs.append(LogEntry(data=data, nivel=nivel, mensagem=mensagem))
                        table.add_row(*parts)

        # Mostra a tabela no terminal (opcional)
        console.print(table)

        return logs