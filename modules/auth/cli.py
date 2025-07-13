from rich.console import Console
from rich.panel import Panel
from .manager import UsuarioManager
from .models import NivelAcesso

console = Console()

def mostrar_tela_login():
    console.print(Panel.fit("Sistema ERP - Login", style="blue"))
    email = input("Email: ")
    senha = input("Senha: ")
    return email, senha

def menu_autenticacao(gui_user=None, gui_pass=None):
    manager = UsuarioManager()
    if gui_user is not None and gui_pass is not None:
        usuario = manager.verificar_login(gui_user, gui_pass)
        return usuario
    while True:
        email, senha = mostrar_tela_login()
        usuario = manager.verificar_login(email, senha)
        if usuario:
            console.print(f"\n[green]Bem-vindo, {usuario.nome}![/]")
            return usuario
        else:
            console.print("\n[red]Credenciais invalidas! Tente novamente.[/]")