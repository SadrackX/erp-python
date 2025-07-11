import os
from modules.empresa.cli import executar_menu_empresa
from modules.produtos.cli import menu_produtos
from modules.clientes.cli import menu_clientes
from rich.console import Console

# Configuração específica para Windows
os.system('')  # Habilita cores no Windows Console
console = Console()
from modules.fornecedores.cli import menu_fornecedores
from modules.pedidos.cli import menu_pedidos
from scripts.inicializar_db import inicializar_todos_arquivos



def menu_principal():
    inicializar_todos_arquivos()
    while True:
        console.print("\n[bold]ERP PYTHON[/]", style="blue")
        console.print("1. Empresa")
        console.print("2. Produtos")
        console.print("3. Clientes")
        console.print("4. Fornecedores")
        console.print("5. Pedidos")
        console.print("6. Sair")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            executar_menu_empresa()
        elif opcao == "2":
            menu_produtos()
        elif opcao == "3":
            menu_clientes()
        elif opcao == "4":
            menu_fornecedores()
        elif opcao == "5":
            menu_pedidos()
        elif opcao == "6":
            console.print("\n[bold]Saindo do sistema...[/]")
            break
        else:
            console.print("\n[red]Opção inválida![/]")

if __name__ == "__main__":
    # Verifica se a pasta dados existe
    if not os.path.exists('dados'):
        os.makedirs('dados')
    menu_principal()