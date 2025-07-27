# scripts/criar_admin.py


from app.managers.auth import UsuarioManager
from app.models.auth import NivelAcesso


if __name__ == "__main__":
    manager = UsuarioManager()
    manager.criar_usuario(
        nome="Admin",
        email="admin@erp.com",
        senha="admin123",
        nivel=NivelAcesso.ADMIN
    )
    print("Usuário admin criado com sucesso!")