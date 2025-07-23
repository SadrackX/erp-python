import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from core.database import CSVManager
from modules.produtos.manager import ProdutoManager
from modules.clientes.manager import ClienteManager
from modules.fornecedores.manager import FornecedorManager
from modules.pedidos.manager import PedidoManager
from modules.pedidos.itens_manager import ItensPedidoManager
from modules.empresa.manager import EmpresaManager

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