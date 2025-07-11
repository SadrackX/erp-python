from rich.console import Console
from rich.table import Table
from .manager import FornecedorManager
from .models import Fornecedor
import re

console = Console()

def validar_cnpj(cnpj: str) -> bool:
    """Validação básica de CNPJ"""
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    return len(cnpj_limpo) == 14

def exibir_fornecedores(fornecedores: list[Fornecedor]):
    """Exibe fornecedores em tabela formatada"""
    table = Table(title="Lista de Fornecedores", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Nome", style="magenta")
    table.add_column("CNPJ", justify="center")
    table.add_column("Contato", justify="right")
    table.add_column("Produtos", justify="right")
    table.add_column("Ativo", justify="center")
    
    for f in fornecedores:
        produtos = str(len(f.produtos_fornecidos)) if f.produtos_fornecidos else "0"
        table.add_row(
            f.id[:8] + "...",
            f.nome,
            f.cnpj,
            f"{f.telefone}\n{f.email or ''}",
            produtos,
            "✅" if f.ativo else "❌"
        )
    
    console.print(table)

def coletar_dados_fornecedor() -> dict:
    """Coleta dados do fornecedor via input"""
    console.print("\n[bold]DADOS DO FORNECEDOR[/]", style="blue")
    
    cnpj = input("CNPJ: ")
    while not validar_cnpj(cnpj):
        console.print("[red]CNPJ inválido! Deve conter 14 dígitos.[/]")
        cnpj = input("CNPJ: ")
    
    return {
        'nome': input("Razão Social: "),
        'cnpj': cnpj,
        'telefone': input("Telefone: "),
        'email': input("E-mail (opcional): ") or None,
        'observacoes': input("Observações (opcional): ") or None,
        'ativo': True
    }

def menu_fornecedores():
    """Menu principal de fornecedores"""
    manager = FornecedorManager()
    
    while True:
        console.print("\n[bold]GERENCIAMENTO DE FORNECEDORES[/]", style="blue")
        console.print("1. Listar fornecedores")
        console.print("2. Cadastrar novo fornecedor")
        console.print("3. Editar fornecedor")
        console.print("4. Desativar/reativar fornecedor")
        console.print("5. Associar produto")
        console.print("6. Voltar")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            fornecedores = manager.buscar_todos()
            exibir_fornecedores(fornecedores)
        
        elif opcao == "2":
            dados = coletar_dados_fornecedor()
            id_novo = manager.cadastrar_fornecedor(Fornecedor(id="", produtos_fornecidos=None, **dados))
            console.print(f"\n[green]✔ Fornecedor cadastrado com sucesso! ID: {id_novo}[/]")
        
        elif opcao == "3":
            fornecedor_id = input("ID do fornecedor a editar: ").strip()
            fornecedor = manager.buscar_por_id(fornecedor_id)
            
            if fornecedor:
                exibir_fornecedores([fornecedor])
                novos_dados = coletar_dados_fornecedor()
                if manager.atualizar_fornecedor(fornecedor_id, novos_dados):
                    console.print("\n[green]✔ Fornecedor atualizado com sucesso![/]")
            else:
                console.print("\n[red]✖ Fornecedor não encontrado![/]")
        
        elif opcao == "4":
            fornecedor_id = input("ID do fornecedor: ").strip()
            fornecedor = manager.buscar_por_id(fornecedor_id)
            
            if fornecedor:
                acao = "reativar" if not fornecedor.ativo else "desativar"
                if input(f"Confirmar {acao} fornecedor {fornecedor.nome}? (s/n): ").lower() == 's':
                    if manager.atualizar_fornecedor(fornecedor_id, {'ativo': not fornecedor.ativo}):
                        console.print(f"\n[green]✔ Fornecedor {acao}do com sucesso![/]")
            else:
                console.print("\n[red]✖ Fornecedor não encontrado![/]")
        
        elif opcao == "5":
            # Implementar associação de produtos
            console.print("\n[yellow]⚠ Funcionalidade em desenvolvimento![/]")
        
        elif opcao == "6":
            break
        
        else:
            console.print("\n[red]✖ Opção inválida![/]")