from rich.console import Console
from rich.table import Table
from .manager import ProdutoManager
from .models import Produto
import re

console = Console()

def exibir_produtos(produtos: list[Produto]):
    """Exibe produtos em uma tabela formatada"""
    table = Table(title="Lista de Produtos", show_lines=True)
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Preço Venda", justify="right")
    table.add_column("Ativo", justify="center")
    
    for p in produtos:
        table.add_row(
            p.id[:8] + "...",
            p.nome,
            f"R$ {p.preco_venda:.2f}",
            "✅" if p.ativo else "❌"
        )
    
    console.print(table)

def coletar_dados_produto(produto_existente: Produto = None) -> dict:
    """Coleta dados do produto via input do usuário"""
    dados = {
        'nome': input("Nome do produto: ").strip(),
        'preco_custo': float(input("Preço de custo: R$ ")),
        'preco_venda': float(input("Preço de venda: R$ ")),
        'observacao': input("Observações (opcional): ").strip() or None,
        'ativo': True
    }
    
    # Validação básica
    if dados['preco_venda'] < dados['preco_custo']:
        console.print("[bold red]Atenção:[/] Preço de venda menor que o custo!", style="red")
    
    return dados

def menu_produtos():
    """Menu principal de produtos"""
    manager = ProdutoManager()
    
    while True:
        console.print("\n[bold]GERENCIAMENTO DE PRODUTOS[/]", style="blue")
        console.print("1. Listar produtos")
        console.print("2. Cadastrar novo produto")
        console.print("3. Editar produto")
        console.print("4. Desativar/reativar produto")
        console.print("5. Voltar")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            filtro = input("Filtrar por (1-Ativos, 2-Inativos, 3-Todos): ").strip()
            produtos = manager.buscar_todos()
            if not produtos:
                print("\nNenhum produto cadastrado ou possível ler os dados!")
                print("Verifique o arquivo produtos.csv na pasta dados")
            else:
                if filtro == "1":
                    produtos = [p for p in produtos if p.ativo]
                elif filtro == "2":
                    produtos = [p for p in produtos if not p.ativo]
            
            exibir_produtos(produtos)
        
        elif opcao == "2":
            dados = coletar_dados_produto()
            id_novo = manager.cadastrar_produto(Produto(id="", **dados))
            console.print(f"\n[green]✔ Produto cadastrado com sucesso! ID: {id_novo}[/]")
        
        elif opcao == "3":
            produto_id = input("ID do produto a editar: ").strip()
            produto = manager.buscar_por_id(produto_id)
            
            if produto:
                exibir_produtos([produto])
                novos_dados = coletar_dados_produto(produto)
                if manager.atualizar_produto(produto_id, novos_dados):
                    console.print("\n[green]✔ Produto atualizado com sucesso![/]")
                else:
                    console.print("\n[red]✖ Falha ao atualizar produto![/]")
            else:
                console.print("\n[red]✖ Produto não encontrado![/]")
        
        elif opcao == "4":
            produto_id = input("ID do produto: ").strip()
            produto = manager.buscar_por_id(produto_id)
            
            if produto:
                acao = "reativar" if not produto.ativo else "desativar"
                if input(f"Confirmar {acao} produto {produto.nome}? (s/n): ").lower() == 's':
                    if manager.atualizar_produto(produto_id, {'ativo': not produto.ativo}):
                        console.print(f"\n[green]✔ Produto {acao}do com sucesso![/]")
                    else:
                        console.print("\n[red]✖ Falha na operação![/]")
            else:
                console.print("\n[red]✖ Produto não encontrado![/]")
        
        elif opcao == "5":
            break
        
        else:
            console.print("\n[red]✖ Opção inválida![/]")