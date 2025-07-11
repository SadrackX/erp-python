from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from .manager import PedidoManager
from .models import Pedido, ItemPedido
from modules.clientes.manager import ClienteManager
from modules.produtos.manager import ProdutoManager
from modules.fornecedores.manager import FornecedorManager
from datetime import datetime
import uuid

console = Console()

def exibir_pedido(pedido: Pedido, cliente_manager: ClienteManager, produto_manager: ProdutoManager):
    """Exibe detalhes de um pedido"""
    cliente = cliente_manager.buscar_por_id(pedido.id_cliente)
    
    table = Table(title=f"Pedido #{pedido.id[:8]}", show_lines=True)
    table.add_column("Item", style="cyan")
    table.add_column("Detalhes", style="magenta")
    
    table.add_row("Cliente", f"{cliente.nome} ({cliente.tipo})")
    table.add_row("Data", pedido.data.strftime("%d/%m/%Y %H:%M"))
    table.add_row("Status", pedido.status.upper())
    table.add_row("Observações", pedido.observacoes or "Nenhuma")
    
    # Tabela de itens
    itens_table = Table(show_lines=True)
    itens_table.add_column("Produto")
    itens_table.add_column("Qtd", justify="right")
    itens_table.add_column("Unitário", justify="right")
    itens_table.add_column("Desconto", justify="right")
    itens_table.add_column("Total", justify="right")
    
    for item in pedido.itens:
        produto = produto_manager.buscar_por_id(item.id_produto)
        itens_table.add_row(
            produto.nome,
            str(item.quantidade),
            f"R$ {item.preco_unitario:.2f}",
            f"R$ {item.desconto:.2f}",
            f"R$ {item.total:.2f}"
        )
    
    # Totais
    table.add_row("Itens", itens_table)
    table.add_row("Subtotal", f"R$ {sum(item.total for item in pedido.itens):.2f}")
    table.add_row("Desconto Total", f"- R$ {pedido.desconto_total:.2f}")
    table.add_row("Frete", f"+ R$ {pedido.valor_frete:.2f}")
    table.add_row("[bold]TOTAL[/]", f"[bold]R$ {pedido.total:.2f}[/]")
    
    console.print(table)

def selecionar_cliente(cliente_manager: ClienteManager) -> str:
    """Interface para seleção de cliente"""
    clientes = cliente_manager.buscar_todos()
    if not clientes:
        console.print("[red]Nenhum cliente cadastrado![/]")
        return None
    
    table = Table(title="Selecione um Cliente", show_lines=True)
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Tipo")
    
    for cliente in clientes:
        table.add_row(
            cliente.id[:8],
            cliente.nome,
            "PF" if cliente.tipo == "PF" else "PJ"
        )
    
    console.print(table)
    
    while True:
        cliente_id = Prompt.ask("Digite o ID do cliente (ou 0 para cancelar)")
        if cliente_id == "0":
            return None
        
        cliente = cliente_manager.buscar_por_id(cliente_id)
        if cliente:
            return cliente.id
        
        console.print("[red]ID inválido! Tente novamente.[/]")

def selecionar_produtos(produto_manager: ProdutoManager) -> list[ItemPedido]:
    """Interface para seleção de produtos"""
    produtos = [p for p in produto_manager.buscar_todos() if p.ativo]
    if not produtos:
        console.print("[red]Nenhum produto ativo cadastrado![/]")
        return []
    
    itens = []
    
    while True:
        console.print("\n[bold]ADICIONAR ITEM AO PEDIDO[/]")
        
        # Mostra tabela de produtos
        table = Table(show_lines=True)
        table.add_column("ID", style="cyan")
        table.add_column("Produto", style="magenta")
        table.add_column("Estoque", justify="right")
        table.add_column("Preço", justify="right")
        
        for produto in produtos:
            table.add_row(
                produto.id[:8],
                produto.nome,
                str(produto.quantidade),
                f"R$ {produto.preco_venda:.2f}"
            )
        
        console.print(table)
        
        produto_id = Prompt.ask(
            "Digite o ID do produto (ou 0 para finalizar)",
            choices=["0"] + [p.id[:8] for p in produtos]
        )
        
        if produto_id == "0":
            break
        
        # Encontra o produto completo pelo ID
        produto = next(p for p in produtos if p.id.startswith(produto_id))
        
        quantidade = Prompt.ask(
            f"Quantidade de '{produto.nome}'",
            default="1",
            show_default=True
        )
        
        desconto = Prompt.ask(
            f"Desconto para '{produto.nome}' (R$)",
            default="0.00",
            show_default=True
        )
        
        itens.append(ItemPedido(
            id_pedido="",  # Será preenchido depois
            id_produto=produto.id,
            quantidade=int(quantidade),
            preco_unitario=produto.preco_venda,
            desconto=float(desconto)
        ))
        
        console.print(f"[green]✔ Item adicionado! Total parcial: R$ {sum(item.total for item in itens):.2f}[/]")
    
    return itens

def menu_pedidos():
    """Menu principal de pedidos"""
    pedido_manager = PedidoManager()
    cliente_manager = ClienteManager()
    produto_manager = ProdutoManager()
    
    while True:
        console.print("\n[bold]GERENCIAMENTO DE PEDIDOS[/]", style="blue")
        console.print("1. Novo pedido")
        console.print("2. Listar pedidos")
        console.print("3. Visualizar pedido")
        console.print("4. Cancelar pedido")
        console.print("5. Voltar")
        
        opcao = Prompt.ask("Opção", choices=["1", "2", "3", "4", "5"])
        
        if opcao == "1":
            console.print("\n[bold]NOVO PEDIDO[/]", style="blue")
            
            # Seleciona cliente
            cliente_id = selecionar_cliente(cliente_manager)
            if not cliente_id:
                continue
            
            # Seleciona produtos
            itens = selecionar_produtos(produto_manager)
            if not itens:
                continue
            
            # Dados adicionais
            observacoes = Prompt.ask("Observações (opcional)", default="")
            desconto_total = Prompt.ask("Desconto total (R$)", default="0.00")
            frete = Prompt.ask("Valor do frete (R$)", default="0.00")
            
            # Cria o pedido
            pedido = Pedido(
                id=str(uuid.uuid4()),
                id_cliente=cliente_id,
                id_forma_pagamento="1",  # Default - pode implementar formas de pagamento depois
                data=datetime.now(),
                status="rascunho",
                itens=itens,
                observacoes=observacoes or None,
                desconto_total=float(desconto_total),
                valor_frete=float(frete)
            )
            
            if Confirm.ask("\nConfirmar criação do pedido?"):
                pedido_manager.criar_pedido(pedido)
                console.print(f"\n[green]✔ Pedido criado com sucesso! ID: {pedido.id}[/]")
                exibir_pedido(pedido, cliente_manager, produto_manager)
        
        elif opcao == "2":
            pedidos = pedido_manager.buscar_todos()
            if not pedidos:
                console.print("\n[yellow]Nenhum pedido cadastrado![/]")
                continue
            
            table = Table(title="Lista de Pedidos", show_lines=True)
            table.add_column("ID", style="cyan")
            table.add_column("Cliente")
            table.add_column("Data")
            table.add_column("Itens", justify="right")
            table.add_column("Total", justify="right")
            table.add_column("Status")
            
            for pedido in sorted(pedidos, key=lambda p: p.data, reverse=True):
                cliente = cliente_manager.buscar_por_id(pedido.id_cliente)
                table.add_row(
                    pedido.id[:8],
                    cliente.nome if cliente else "?",
                    pedido.data.strftime("%d/%m/%y"),
                    str(len(pedido.itens)),
                    f"R$ {pedido.total:.2f}",
                    pedido.status.upper()
                )
            
            console.print(table)
        
        elif opcao == "3":
            pedido_id = Prompt.ask("Digite o ID do pedido")
            pedido = pedido_manager.buscar_por_id(pedido_id)
            
            if pedido:
                exibir_pedido(pedido, cliente_manager, produto_manager)
            else:
                console.print("\n[red]Pedido não encontrado![/]")
        
        elif opcao == "4":
            pedido_id = Prompt.ask("Digite o ID do pedido para cancelar")
            pedido = pedido_manager.buscar_por_id(pedido_id)
            
            if pedido:
                exibir_pedido(pedido, cliente_manager, produto_manager)
                if Confirm.ask("\n[red]Tem certeza que deseja cancelar este pedido?[/]"):
                    if pedido_manager.cancelar_pedido(pedido.id):
                        console.print("\n[green]Pedido cancelado com sucesso![/]")
                    else:
                        console.print("\n[red]Falha ao cancelar pedido![/]")
            else:
                console.print("\n[red]Pedido não encontrado![/]")
        
        elif opcao == "5":
            break