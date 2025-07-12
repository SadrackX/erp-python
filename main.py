from datetime import datetime, timedelta
import os
from core import logger
from core.auth import AuthManager
from modules.auditoria.cli import mostrar_historico
from modules.empresa.cli import executar_menu_empresa
from modules.produtos.cli import menu_produtos
from modules.clientes.cli import menu_clientes
from rich.console import Console
from rich.prompt import Confirm
from modules.relatorios.dashboard import Dashboard
from modules.relatorios.logviewer import LogViewer
from scripts import criar_admin
from scripts.backup import BackupManager
from pathlib import Path
from modules.fornecedores.cli import menu_fornecedores
from modules.pedidos.cli import menu_pedidos
from scripts.inicializar_db import inicializar_todos_arquivos
from modules.auth.cli import menu_autenticacao
from modules.auth.models import NivelAcesso
from modules.auth.middlewares import requer_acesso
from modules.auth.manager import UsuarioManager
usuario_manager = UsuarioManager()
        
if not usuario_manager.get_all():
    logger.log("Usuário admin criado automaticamente")  # Se não houver usuários    
    usuario_manager.criar_usuario(
    nome="Admin",
    email="admin@erp.com",
    senha="admin123",
    nivel=NivelAcesso.ADMIN
)


# Configuração específica para Windows
os.system('')  # Habilita cores no Windows Console
console = Console()

if __name__ == "__main__":
    # Verifica estrutura de diretórios
    if not os.path.exists('dados'):
        os.makedirs('dados')

def menu_backup():
    manager = BackupManager()
    
    while True:
        console.print("\n[bold]GERENCIAMENTO DE BACKUP[/]", style="blue")
        console.print("1. Criar backup agora")
        console.print("2. Listar backups disponíveis")
        console.print("3. Restaurar backup")
        console.print("4. Voltar ao menu principal")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            comentario = input("Digite uma descrição (opcional): ").strip()
            caminho = manager.criar_backup(comentario)
            console.print(f"\n[green]✓ Backup criado com sucesso![/]\nArquivo: {caminho}")
            
        elif opcao == "2":
            backups = list(Path("backups").glob("*.zip"))
            if not backups:
                console.print("\n[yellow]Nenhum backup encontrado![/]")
                continue
                
            table = table(title="Backups Disponíveis", show_lines=True)
            table.add_column("Número", style="cyan")
            table.add_column("Arquivo")
            table.add_column("Tamanho")
            table.add_column("Data")
            
            for i, backup in enumerate(sorted(backups, reverse=True), 1):
                table.add_row(
                    str(i),
                    backup.name,
                    f"{backup.stat().st_size / 1024:.1f} KB",
                    datetime.fromtimestamp(backup.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
                )
            
            console.print(table)
            
        elif opcao == "3":
            backups = list(Path("backups").glob("*.zip"))
            if not backups:
                console.print("\n[yellow]Nenhum backup disponível para restauração![/]")
                continue
                
            console.print("\n[bold]Backups disponíveis:[/]")
            for i, backup in enumerate(sorted(backups, reverse=True), 1):
                console.print(f"{i}. {backup.name}")
                
            try:
                escolha = int(input("\nDigite o número do backup para restaurar: "))
                backup_selecionado = sorted(backups, reverse=True)[escolha - 1]
                
                if Confirm.ask(f"\n[red]ATENÇÃO:[/] Isso sobrescreverá todos os dados atuais. Continuar?"):
                    manager.restaurar_backup(str(backup_selecionado))
                    console.print("\n[green]✓ Dados restaurados com sucesso![/]")
            except (ValueError, IndexError):
                console.print("\n[red]Opção inválida![/]")
                
        elif opcao == "4":
            break
            
        else:
            console.print("\n[red]Opção inválida![/]")

@requer_acesso(NivelAcesso.ADMIN)
def menu_administracao(usuario):
    """Menu exclusivo para administradores"""
    while True:
        console.print("\n[bold]MENU ADMINISTRATIVO[/]", style="blue")
        console.print("1. Gerenciar usuários")
        console.print("2. Configurações do sistema")
        console.print("3. Auditoria")
        console.print("4. Voltar")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            console.print("\n[green]Gerenciamento de usuários[/]")
            # Implementar aqui o gerenciamento de usuários
        elif opcao == "2":
            console.print("\n[green]Configurações do sistema[/]")
            # Implementar configurações
        elif opcao == "3":
            console.print("\n[green]Histórico de Auditoria[/]")
            tabela = input("Digite o nome da tabela (ou deixe em branco para todas): ").strip() or None
            registro_id = input("Digite o ID do registro (ou deixe em branco para todos): ").strip() or None
            mostrar_historico(tabela or None, registro_id or None)
        elif opcao == "4":
            break
        else:
            console.print("\n[red]Opção inválida![/]")

def menu_principal(usuario):
    AuthManager.set_usuario_atual(usuario)
    """Menu principal adaptado ao nível de acesso do usuário"""
    while True:
        console.print(f"\n[bold]ERP PYTHON[/] [dim]({usuario.nome} - {usuario.nivel_acesso.value})[/]", style="blue")
        
        opcoes = [
            "1. Dashboard",
            "2. Clientes",
            "3. Produtos",
            "4. Pedidos",
            "5. Fornecedores",
            "6. Relatórios",
            "7. Backup/Restauração",
            "8. Visualizar logs"
        ]
        
        # Opções apenas para administradores
        if usuario.nivel_acesso == NivelAcesso.ADMIN:
            opcoes.append("9. Administração")
            
        opcoes.append("0. Sair")
        
        opcao = input("\n".join(opcoes) + "\nOpção: ").strip()
        
        try:
            if opcao == "1":
                Dashboard().mostrar_resumo()
            elif opcao == "2":
                menu_clientes()
            elif opcao == "3":
                menu_produtos()
            elif opcao == "4":
                menu_pedidos()
            elif opcao == "5":
                menu_fornecedores()
            #elif opcao == "6":
                #menu_relatorios()
            elif opcao == "7":
                menu_backup()
            elif opcao == "8":
                dias = int(input("Quantos dias de logs (1-30)? ") or 1)
                LogViewer().mostrar_logs(dias)
            elif opcao == "9" and usuario.nivel_acesso == NivelAcesso.ADMIN:
                menu_administracao(usuario)
            elif opcao == "0":
                AuthManager.logout()
                if Confirm.ask("Deseja criar backup antes de sair?"):
                    BackupManager().criar_backup("backup_pre_saida")
                break
            else:
                console.print("\n[red]Opção inválida ou acesso negado![/]")
        except PermissionError as e:
            logger.log(f"Tentativa de acesso não autorizado: {str(e)}", "warning")
            console.print(f"\n[red]Erro: {str(e)}[/]")

if __name__ == "__main__":
    # Verifica estrutura de diretórios
    if not os.path.exists('dados'):
        os.makedirs('dados')
    
    # Tela de login
    usuario = menu_autenticacao()
    
    try:
        logger.log(f"Usuário autenticado: {usuario.nome} ({usuario.nivel_acesso.value})")
        menu_principal(usuario)
    except Exception as e:
        logger.log(f"Erro fatal: {str(e)}", "critical")
        console.print(f"\n[red]Erro: {str(e)}[/]")
    finally:
        logger.log("Sistema encerrado")