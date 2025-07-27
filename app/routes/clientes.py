from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.services import logger
from app.managers.clientes import ClienteManager
from app.models.clientes import Cliente

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/listar')
def listar():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    clientes = ClienteManager().buscar_todos()
    clientes_dict = {c.id: c.nome for c in ClienteManager().buscar_todos()}

    # Filtros recebidos por query string
    cliente_filtro = request.args.get('cliente', '').lower()
    pagina = int(request.args.get('pagina', 1))
    clientes_por_pagina = 10

    # Aplica filtros
    clientes_filtrados = []
    for p in clientes:
        nome_cliente = clientes_dict.get(p.id, '').lower()

        # Filtro por cliente (nome ou id)
        if cliente_filtro and cliente_filtro not in p.id.lower() and cliente_filtro not in nome_cliente:
            continue

        clientes_filtrados.append(p)
        clientes_filtrados.sort(key=lambda p: p.id, reverse=True)

    # Paginação
    total_clientes = len(clientes_filtrados)
    total_paginas = (total_clientes + clientes_por_pagina - 1) // clientes_por_pagina
    inicio = (pagina - 1) * clientes_por_pagina
    fim = inicio + clientes_por_pagina
    clientes_paginados = clientes_filtrados[inicio:fim]

    return render_template(
        'clientes_list.html',
        usuario_nome=session['usuario_nome'],
        usuario_nivel=session['usuario_nivel'],
        clientes=clientes_paginados,
        clientes_dict=clientes_dict,
        cliente_filtro=cliente_filtro,
        pagina_atual=pagina,
        total_paginas=total_paginas
    )

@clientes_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))

    editar_id = request.args.get('editar')
    #cliente = ClienteManager().buscar_por_id(editar_id) if editar_id else None
    if request.method == 'POST':
        # Pega informações do form cliente
        cliente = request.form.to_dict()
        if editar_id:        
            # Atualização de cliente existente   
            ClienteManager().atualizar_cliente(editar_id, cliente)
            logger.log(f"Cliente {request.form['nome']} atualizado com sucesso!", 'info')
            return redirect(url_for('clientes.listar'))
        else:          
            # Cadastro de novo cliente  
            ClienteManager().cadastrar_cliente(Cliente.from_dict(cliente))
            logger.log(f"Cliente {request.form['nome']} cadastrado!", 'info')
            return redirect(url_for('clientes.listar'))
    return render_template('clientes_list.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@clientes_bp.route('/buscar')
def buscar():
    termo = request.args.get('q', '').lower()
    clientes = ClienteManager().buscar_todos()
    resultados = []
    for c in clientes:
        if (
            termo in c.nome.lower() or
            termo in (c.cpf_cnpj or '').lower() or
            termo in (c.email or '').lower()
        ):
            resultados.append(Cliente.to_dict(c))
    return jsonify(resultados)
