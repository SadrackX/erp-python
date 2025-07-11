import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from core.database import CSVManager
from modules.produtos.manager import ProdutoManager
from modules.clientes.manager import ClienteManager
from modules.fornecedores.manager import FornecedorManager
from modules.pedidos.manager import PedidoManager

def inicializar_todos_arquivos():
    # Garante que a pasta dados existe
    Path("dados").mkdir(exist_ok=True)
    
    # Inicializa cada manager para criar os arquivos
    managers = [
        ProdutoManager(),
        ClienteManager(),
        FornecedorManager(),
        PedidoManager()
    ]
    
    print("Arquivos CSV inicializados com sucesso!")

if __name__ == "__main__":
    inicializar_todos_arquivos()