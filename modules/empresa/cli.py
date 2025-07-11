from .manager import EmpresaManager

def mostrar_menu_empresa():
    print("\n=== MENU EMPRESA ===")
    print("1. Cadastrar dados da empresa")
    print("2. Visualizar dados")
    print("3. Editar dados")
    print("4. Voltar")

def coletar_dados_empresa():
    return {
        'id': '1',  # ID fixo pois só terá uma empresa
        'nome': input("Nome/Razão Social: "),
        'cnpj': input("CNPJ: "),
        'email': input("E-mail: "),
        'celular': input("Celular: "),
        'logo_path': input("Caminho do logo (opcional): "),
        'cep': input("CEP: "),
        'endereco': input("Endereço: "),
        'bairro': input("Bairro: "),
        'complemento': input("Complemento: "),
        'cidade': input("Cidade: "),
        'estado': input("Estado (UF): ")
    }

def executar_menu_empresa():
    manager = EmpresaManager()
    
    while True:
        mostrar_menu_empresa()
        opcao = input("Opção: ")
        
        if opcao == "1":
            dados = coletar_dados_empresa()
            if manager.cadastrar_empresa(dados):
                print("\nEmpresa cadastrada com sucesso!")
            else:
                print("\nJá existe um cadastro de empresa!")
        
        elif opcao == "2":
            empresa = manager.get_all()
            if empresa:
                print("\nDADOS DA EMPRESA:")
                for chave, valor in empresa[0].items():
                    print(f"{chave.upper()}: {valor}")
            else:
                print("\nNenhuma empresa cadastrada!")
        
        elif opcao == "3":
            # Implementação similar ao cadastro
            pass
        
        elif opcao == "4":
            break
        
        else:
            print("Opção inválida!")