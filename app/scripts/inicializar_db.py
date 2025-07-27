import sys
from pathlib import Path

from app.managers.empresa import EmpresaManager
from app.managers.fornecedores import FornecedorManager
from app.managers.itens import ItensPedidoManager
from app.managers.pedidos import PedidoManager
sys.path.append(str(Path(__file__).parent.parent))
from app.managers.clientes import ClienteManager
from app.managers.produtos import ProdutoManager
from core.database import CSVManager


def inicializar_todos_arquivos():
    # Garante que a pasta dados existe
    Path("dados").mkdir(exist_ok=True)
    
    # Inicializa cada manager para criar os arquivos
    managers = [
        ProdutoManager(),
        ClienteManager(),
        FornecedorManager(),
        PedidoManager(),
        ItensPedidoManager(),
        ProdutoManager(),
        EmpresaManager()
    ]
    print("Arquivos CSV inicializados com sucesso!")
    # Exibe os cabeçalhos de cada arquivo criado
    for m in managers:
        if isinstance(m, ProdutoManager):
            headers = [header for header in m.get_headers() if header != 'quantidade']
            print(f"{m.filepath.name}: {headers}")
        else:
            print(f"{m.filepath.name}: {m.get_headers()}")

if __name__ == "__main__":
    inicializar_todos_arquivos()