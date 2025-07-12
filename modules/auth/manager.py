import csv
import uuid
import hashlib
from core import logger
from core.database import CSVManager
from .models import Usuario, NivelAcesso

class UsuarioManager(CSVManager):
    def __init__(self):
        super().__init__('usuarios.csv')
    
    def get_headers(self) -> list:
        return ['id', 'nome', 'email', 'senha_hash', 'nivel_acesso', 'ativo']
    
    def criar_usuario(self, nome: str, email: str, senha: str, nivel: NivelAcesso) -> Usuario:
        usuario = Usuario(
            id=str(uuid.uuid4()),
            nome=nome,
            email=email,
            senha_hash=self._hash_senha(senha),
            nivel_acesso=nivel.value
        )
        self.save(usuario.__dict__)
        return usuario.id
    
    def _hash_senha(self, senha: str) -> str:
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def verificar_login(self, email: str, senha: str) -> Usuario | None:
        for usuario_data in self.get_all():
            if (usuario_data['email'] == email and 
                usuario_data['senha_hash'] == self._hash_senha(senha)):
                
                # Converte string para enum
                nivel = NivelAcesso(usuario_data['nivel_acesso'])
                
                return Usuario(
                    id=usuario_data['id'],
                    nome=usuario_data['nome'],
                    email=usuario_data['email'],
                    senha_hash=usuario_data['senha_hash'],
                    nivel_acesso=nivel,
                    ativo=usuario_data.get('ativo', 'True').lower() == 'true'
                )
        return None
    def get_all(self) -> list[dict]:
        """Retorna todos os usuários com tratamento de erro"""
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            self._ensure_file_exists()
            return []
        except Exception as e:
            logger.log(f"Erro ao ler usuários: {str(e)}", "error")
            return []