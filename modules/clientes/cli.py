from rich.console import Console
from rich.table import Table
from .manager import ClienteManager
from .models import Cliente
import re

console = Console()

def validar_cpf_cnpj(valor: str, tipo: str) -> bool:
    """Validação simples de CPF/CNPJ"""
    if tipo == 'PF':
        return len(re.sub(r'\D', '', valor)) == 11
    else:
        return len(re.sub(r'\D', '', valor)) == 14

def exibir_clientes(clientes: list[Cliente]):
    """Exibe clientes em tabela formatada - Versão corrigida"""
    if not clientes:
        console.print("[yellow]Nenhum cliente cadastrado![/]")
        return
    
    table = Table(
        title="Lista de Clientes",
        show_header=True,
        header_style="bold blue",
        show_lines=True
    )
    
    # Colunas com larguras definidas
    table.add_column("ID", style="cyan", width=8)
    table.add_column("Nome", style="magenta", min_width=20)
    table.add_column("Tipo", justify="center", width=4)
    table.add_column("CPF/CNPJ", min_width=14)
    table.add_column("Contato", min_width=25)
    table.add_column("Status", justify="center", width=8)
    
    for cliente in clientes:
        # Debug: Verifique cada cliente antes de adicionar
        print(f"DEBUG - Cliente sendo processado: {cliente.__dict__}")
        
        # Formatação condicional do documento
        doc = cliente.cpf_cnpj
        if cliente.tipo == 'PF' and len(doc) == 11:
            doc = f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
        elif cliente.tipo == 'PJ' and len(doc) == 14:
            doc = f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
        
        # Adiciona linha à tabela
        table.add_row(
            cliente.id[:8],
            cliente.nome,
            cliente.tipo,
            doc,
            f"Email: {cliente.email}\nTel: {cliente.celular}" if cliente.email else cliente.celular,
            "[green]Ativo[/]" if cliente.ativo else "[red]Inativo[/]"
        )
    
    console.print(table)
    print("DEBUG - Tabela renderizada com", len(clientes), "clientes")  # Confirmação

def coletar_dados_cliente() -> dict:
    """Coleta dados do cliente via input"""
    console.print("\n[bold]DADOS DO CLIENTE[/]", style="blue")
    
    while True:
        tipo = input("Tipo (PF/PJ): ").upper()
        if tipo in ('PF', 'PJ'):
            break
        console.print("[red]Erro: Digite PF para pessoa física ou PJ para jurídica[/]")
    
    cpf_cnpj = input("CPF/CNPJ: ")
    while not validar_cpf_cnpj(cpf_cnpj, tipo):
        console.print("[red]CPF/CNPJ inválido para o tipo selecionado![/]")
        cpf_cnpj = input("CPF/CNPJ: ")
    
    return {
        'nome': input("Nome completo/Razão social: "),
        'tipo': tipo,
        'cpf_cnpj': cpf_cnpj,
        'email': input("E-mail (opcional): ") or None,
        'celular': input("Celular (opcional): ") or None,
        'observacoes': input("Observações (opcional): ") or None,
        'ativo': True
    }

def menu_clientes():
    """Menu principal de clientes"""
    manager = ClienteManager()
    
    while True:
        console.print("\n[bold]GERENCIAMENTO DE CLIENTES[/]", style="blue")
        console.print("1. Listar clientes")
        console.print("2. Cadastrar novo cliente")
        console.print("3. Editar cliente")
        console.print("4. Desativar/reativar cliente")
        console.print("5. Voltar")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            clientes = manager.buscar_todos()
            exibir_clientes(clientes)
        
        elif opcao == "2":
            dados = coletar_dados_cliente()
            id_novo = manager.cadastrar_cliente(Cliente(id="", **dados))
            console.print(f"\n[green]✔ Cliente cadastrado com sucesso! ID: {id_novo}[/]")
        
        elif opcao == "3":
            cliente_id = input("ID do cliente a editar: ").strip()
            cliente = manager.buscar_por_id(cliente_id)
            
            if cliente:
                exibir_clientes([cliente])
                novos_dados = coletar_dados_cliente()
                if manager.atualizar_cliente(cliente_id, novos_dados):
                    console.print("\n[green]✔ Cliente atualizado com sucesso![/]")
            else:
                console.print("\n[red]✖ Cliente não encontrado![/]")
        
        elif opcao == "4":
            cliente_id = input("ID do cliente: ").strip()
            cliente = manager.buscar_por_id(cliente_id)
            
            if cliente:
                acao = "reativar" if not cliente.ativo else "desativar"
                if input(f"Confirmar {acao} cliente {cliente.nome}? (s/n): ").lower() == 's':
                    if manager.atualizar_cliente(cliente_id, {'ativo': not cliente.ativo}):
                        console.print(f"\n[green]✔ Cliente {acao}do com sucesso![/]")
            else:
                console.print("\n[red]✖ Cliente não encontrado![/]")
        
        elif opcao == "5":
            break
        
        else:
            console.print("\n[red]✖ Opção inválida![/]")