# scripts/criar_admin.py
from modules.auth.manager import UsuarioManager
from modules.auth.models import NivelAcesso

if __name__ == "__main__":
    manager = UsuarioManager()
    manager.criar_usuario(
        nome="Admin",
        email="admin@erp.com",
        senha="admin123",
        nivel=NivelAcesso.ADMIN
    )
    print("Usuário admin criado com sucesso!")