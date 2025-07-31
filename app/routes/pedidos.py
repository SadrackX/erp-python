from datetime import datetime
from flask import Blueprint, flash, json, redirect, render_template, request, session, url_for

from app.services import logger
from app.core.utils import redirecionar_pos_formulario
from app.managers.clientes import ClienteManager
from app.managers.itens import ItensPedidoManager
from app.managers.pedidos import PedidoManager
from app.models.Itens import ItemPedido
from app.models.clientes import Cliente
from app.models.pedidos import Pedido
from ..services.pedidos import verificar_e_atualizar_status_pedidos, total_este_mes

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

@pedidos_bp.route('/listar')
def listar():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))

    todos_pedidos = PedidoManager().buscar_todos()
    clientes = ClienteManager().buscar_todos()
    clientes_dict = {c.id: c.nome for c in clientes}

    # Filtros recebidos por query string
    cliente_filtro = request.args.get('cliente', '').lower()
    status_filtro = request.args.get('status', '')
    data_inicio_str = request.args.get('data_inicio', '')
    data_fim_str = request.args.get('data_fim', '')
    pagina = int(request.args.get('pagina', 1))
    pedidos_por_pagina = 10

    # Aplica filtros
    pedidos_filtrados = []
    for p in todos_pedidos:
        if p.status:
            p.falta_pagar = max(0, p.total - (p.valor_pago or 0))
            nome_cliente = clientes_dict.get(p.id_cliente, '').lower()

            if not status_filtro and p.status.lower() in ['cancelado', 'finalizado', 'orçamento']:
                continue

            # Filtro por cliente (nome ou id)
            if cliente_filtro and cliente_filtro not in p.id_cliente.lower() and cliente_filtro not in nome_cliente:
                continue

            # Filtro por status
            if status_filtro and p.status.lower() != status_filtro.lower():
                continue

            # Filtro por data de entrega
            if p.data_previsao_entrega:
                if data_inicio_str:
                    data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
                    if p.data_previsao_entrega < data_inicio:
                        continue
                if data_fim_str:
                    data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
                    if p.data_previsao_entrega > data_fim:
                        continue

            pedidos_filtrados.append(p)
            pedidos_filtrados.sort(key=lambda p: p.data or datetime.min, reverse=True)

    # Paginação
    total_pedidos = len(pedidos_filtrados)
    total_paginas = (total_pedidos + pedidos_por_pagina - 1) // pedidos_por_pagina
    inicio = (pagina - 1) * pedidos_por_pagina
    fim = inicio + pedidos_por_pagina
    pedidos_paginados = pedidos_filtrados[inicio:fim]

    return render_template(
        'pedidos_list.html',
        usuario_nome=session['usuario_nome'],
        usuario_nivel=session['usuario_nivel'],
        pedidos=pedidos_paginados,
        clientes=clientes_dict,
        cliente_filtro=cliente_filtro,
        status_filtro=status_filtro,
        data_inicio=data_inicio_str,
        data_fim=data_fim_str,
        pagina_atual=pagina,
        total_paginas=total_paginas
    )

@pedidos_bp.route('/por_status/<status>')
def por_status(status):
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))

    pedidos = PedidoManager().buscar_todos()
    clientes_dict = {c.id: c.nome for c in ClienteManager().buscar_todos()}

    # Filtros recebidos por query string
    cliente_filtro = request.args.get('cliente', '').lower()
    data_inicio_str = request.args.get('data_inicio', '')
    data_fim_str = request.args.get('data_fim', '')
    pagina = int(request.args.get('pagina', 1))
    pedidos_por_pagina = 10

    # Aplica filtros
    pedidos_resultado = []
    for p in pedidos:
        p.falta_pagar = max(0, p.total - (p.valor_pago or 0))
        if p.status.lower() != status.lower():
            continue

        nome_cliente = clientes_dict.get(p.id_cliente, '').lower()

        # Filtro por cliente (nome ou id)
        if cliente_filtro and cliente_filtro not in p.id_cliente.lower() and cliente_filtro not in nome_cliente:
            continue

        # Filtro por data de entrega
        if p.data_previsao_entrega:
            if data_inicio_str:
                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
                if p.data_previsao_entrega < data_inicio:
                    continue
            if data_fim_str:
                data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
                if p.data_previsao_entrega > data_fim:
                    continue

        pedidos_resultado.append(p)

    # Ordena por data (mais novo primeiro)
    pedidos_resultado.sort(key=lambda p: p.data or datetime.min, reverse=True)

    # Paginação
    total_pedidos = len(pedidos_resultado)
    total_paginas = (total_pedidos + pedidos_por_pagina - 1) // pedidos_por_pagina
    inicio = (pagina - 1) * pedidos_por_pagina
    fim = inicio + pedidos_por_pagina
    pedidos_paginados = pedidos_resultado[inicio:fim]

    return render_template(
        'pedidos_list.html',
        usuario_nome=session['usuario_nome'],
        usuario_nivel=session['usuario_nivel'],
        clientes=clientes_dict,
        titulo=status,
        pedidos=pedidos_paginados,
        cliente_filtro=cliente_filtro,
        data_inicio=data_inicio_str,
        data_fim=data_fim_str,
        pagina_atual=pagina,
        total_paginas=total_paginas
    )

@pedidos_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        data_str = request.form.get('data_previsao_entrega')
        produtos_json = request.form.get('produtos_json')
        itens = []
        if produtos_json:
            produtos = json.loads(produtos_json)
            for p in produtos:
                itens.append(ItemPedido(
                    id_pedido='',
                    nome=p['nome'],
                    quantidade=p['quantidade'],
                    preco_unitario=p['preco_unitario']
                ))
        cliente_id = request.form['id_cliente']
        raw_valor = request.form.get('valor_pago', '').strip()
        form = request.form.to_dict()
        novo_cliente = Cliente.from_dict(form)
        if cliente_id == 'novo':            
            form['ativo'] = 'ativo' in request.form
            form['observacoes']=None            
            logger.log(f"Cliente {novo_cliente.nome} cadastrado!", 'info')
            cliente_id = ClienteManager().cadastrar_cliente(novo_cliente)
        else:
            logger.log(f"Cliente {novo_cliente.nome} atualizado!")
            ClienteManager().atualizar_cliente(cliente_id,form)

        novo = Pedido(
            id='',
            id_cliente=cliente_id,
            data=datetime.now(),
            status=request.form['status'],
            itens=itens,
            observacoes=request.form.get('observacoes'),
            data_previsao_entrega=data_str,
            forma_de_pagamento=request.form.get('forma_de_pagamento'),
            valor_pago=float(raw_valor) if raw_valor else 0.0
        )
        PedidoManager().criar_pedido(novo)
        logger.log(f"Pedido ID: {novo.id} adicionado!", 'info')
        return redirect(url_for('pedidos.listar'))
    return render_template('pedidos_form.html', pedido=None,cliente=None, produtos=None, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@pedidos_bp.route('/editar/<pedido_id>/editar', methods=['GET', 'POST'])
def editar(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))

    pedido_id = pedido_id or request.args.get('editar')
    produtos_json = request.form.get('produtos_json')
    produtos_att = []
    if produtos_json:
        produtos = json.loads(produtos_json)
        for p in produtos:
            produtos_att.append(ItemPedido(
                id_pedido='',
                nome=p['nome'],
                quantidade=p['quantidade'],
                preco_unitario=p['preco_unitario']
            ))
    
    pedido_obj = PedidoManager().buscar_por_id(pedido_id) if pedido_id else None
    if not pedido_obj:
        flash('Pedido não encontrado!')
        return redirect(url_for('pedidos.listar'))
    
    session['voltar_para'] = request.referrer

    pedido = pedido_obj.to_dict()  # Aqui corrigido: chama o método

    cliente = ClienteManager().buscar_por_id(pedido['id_cliente']) if pedido.get('id_cliente') else None

    pedido['itens'] = produtos_json
    itens = pedido.get('itens', [])
    if isinstance(itens, list):
        for item in itens:
            if isinstance(item, dict):
                pedido['itens'].append({
                    'id_produto': item.get('id_produto', ''),
                    'nome': item.get('nome', 'Produto removido'),
                    'quantidade': item.get('quantidade', 0),
                    'preco_unitario': item.get('preco_unitario', 0),
                    'total': item.get('total', 0)
                })

    if request.method == 'POST':
        data_str = request.form.get('data_previsao_entrega')
        novos_dados = {
            'status': request.form['status'],
            'observacoes': request.form.get('observacoes'),
            'id_cliente': request.form.get('id_cliente'),
            'data_previsao_entrega': data_str,
            'forma_de_pagamento': request.form.get('forma_de_pagamento'),
            'valor_pago': request.form.get('valor_pago',0)
        }
        PedidoManager().atualizar_itens_pedido(pedido_id, produtos_att)
        PedidoManager().atualizar_pedido(pedido_id, novos_dados)
        logger.log(f"Pedido ID: {pedido_id} atualizado!", 'info')
        return redirect(url_for('dashboard.dashboard'))
    
    if isinstance(pedido.get("data_previsao_entrega"), datetime):
        pedido["data_previsao_entrega"] = pedido["data_previsao_entrega"].strftime("%Y-%m-%d")

    return render_template(
        'pedidos_form.html',
        pedido=pedido,
        cliente=cliente,
        produtos=pedido_obj.itens if pedido_obj else [],
        usuario_nome=session['usuario_nome'],
        usuario_nivel=session['usuario_nivel']
    )

@pedidos_bp.route('/detalhes/<pedido_id>')
def detalhes(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    pedido = PedidoManager().buscar_por_id(pedido_id)
    if not pedido:
        logger.log('Pedido não encontrado!', 'error')
        return redirect(url_for('pedidos.listar'))
    cliente = ClienteManager().buscar_por_id(pedido.id_cliente).to_dict() if pedido.id_cliente else None
    produtos = []
    for item in pedido.itens:
        prod = ItensPedidoManager().buscar_itens_por_pedido(item.id_pedido)
        produtos.append({
            'nome': item.nome if prod else 'Produto removido',
            'preco_unitario': item.preco_unitario,
            'quantidade': item.quantidade,
            'total': item.total
        })
    return render_template('pedido_detalhes.html', pedido=pedido, cliente=cliente, produtos=produtos, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@pedidos_bp.route('/cancelar/<pedido_id>/cancelar')
def cancelar(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    PedidoManager().cancelar_pedido(pedido_id)
    logger.log(f"Pedido ID: {pedido_id} cancelado!", 'info')
    return redirecionar_pos_formulario('pedidos.listar')
