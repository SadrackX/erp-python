from datetime import datetime
import json
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services import logger
from app.core.utils import redirecionar_pos_formulario
from app.managers.clientes import ClienteManager
from app.managers.pedidos import PedidoManager
from app.managers.produtos import ProdutoManager
from app.models.Itens import ItemPedido
from app.models.clientes import Cliente
from app.models.pedidos import Pedido

orcamentos_bp = Blueprint('orcamentos', __name__, url_prefix='/orcamentos')

@orcamentos_bp.route('/')
def listar():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))

    todos_pedidos = PedidoManager().buscar_todos()
    clientes = ClienteManager().buscar_todos()
    clientes_dict = {c.id: c.nome for c in clientes}

    # Filtros recebidos por query string
    cliente_filtro = request.args.get('cliente', '').lower()
    pagina = int(request.args.get('pagina', 1))
    pedidos_por_pagina = 10

    # Aplica filtros
    pedidos_filtrados = []
    for p in todos_pedidos:
        if p.status == 'Orçamento':
            p.falta_pagar = max(0, p.total - (p.valor_pago or 0))
            nome_cliente = clientes_dict.get(p.id_cliente, '').lower()

            # Filtro por cliente (nome ou id)
            if cliente_filtro and cliente_filtro not in p.id_cliente.lower() and cliente_filtro not in nome_cliente:
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
        'orcamentos_list.html',
        usuario_nome=session['usuario_nome'],
        usuario_nivel=session['usuario_nivel'],
        pedidos=pedidos_paginados,
        clientes=clientes_dict,
        cliente_filtro=cliente_filtro,
        status_filtro='Orçamento',
        pagina_atual=pagina,
        total_paginas=total_paginas
    )

@orcamentos_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        dados = request.form.to_dict()
        produtos = json.loads(dados.get('produtos_json', '[]'))
        cliente_id = dados.get('id_cliente')
        novo_cliente = []
        # Verifica ou cria cliente se for novo
        novo_cliente = Cliente(
        id='',
        nome=request.form['nome'],
        tipo=request.form['tipo'],
        cpf_cnpj=request.form['cpf_cnpj'],
        email=request.form['email'],
        celular=request.form['celular'],
        endereco=request.form['endereco'],
        numero=request.form['numero'],
        bairro=request.form['bairro'],
        cidade=request.form['cidade'],
        cep=request.form['cep'],
        uf=request.form['uf'],
        observacoes=None,
        ativo=True)
        if cliente_id == 'novo':   
            cliente_id = ClienteManager().cadastrar_cliente(novo_cliente)
        else:
            novo_cliente.id=cliente_id
            atualizar_cliente = novo_cliente.to_dict()
            ClienteManager().atualizar_cliente(cliente_id,atualizar_cliente)
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

        pedido = Pedido(
            id='',
            id_cliente=cliente_id,
            data=datetime.now(),
            status=request.form['status'],
            itens=itens,
            observacoes=request.form.get('observacoes'),
            data_previsao_entrega='',
            forma_de_pagamento='',
            valor_pago=0.0
        )
        pedido_id = PedidoManager().criar_pedido(pedido)

        flash('Orçamento criado com sucesso!')
        return redirect(url_for('orcamentos.listar'))  # ou `orcamentos`

    produtos = ProdutoManager().buscar_todos()
    return render_template('orcamentos_form.html', cliente=None, produtos=produtos, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], pedido=None)

@orcamentos_bp.route('/editar/<pedido_id>/editar', methods=['GET', 'POST'])
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
        return redirect(url_for('orcamentos.listar'))

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
        
        if novos_dados['status'] == 'Orçamento':
            PedidoManager().atualizar_itens_pedido(pedido_id, produtos_att)
            PedidoManager().atualizar_pedido(pedido_id, novos_dados)
            logger.log(f"Orçamento ID: {pedido_id} atualizado!", 'info')
            return redirecionar_pos_formulario('dashboard.dashboard')
        else:
            novos_dados['data'] = datetime.now().isoformat()
            PedidoManager().atualizar_pedido(pedido_id, novos_dados)
            return redirect(url_for('pedidos.editar', pedido_id=pedido_id)) 
        
    if isinstance(pedido.get("data_previsao_entrega"), datetime):
        pedido["data_previsao_entrega"] = pedido["data_previsao_entrega"].strftime("%Y-%m-%d")

    return render_template(
        'orcamentos_form.html',
        pedido=pedido,
        cliente=cliente,
        produtos=pedido_obj.itens if pedido_obj else [],
        usuario_nome=session['usuario_nome'],
        usuario_nivel=session['usuario_nivel']
    )

@orcamentos_bp.route('/gerar_pedido/<pedido_id>/pedido')
def gerar_pedido(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    PedidoManager().gerar_pedido(pedido_id)
    logger.log(f"Pedido ID: {pedido_id} Criado!", 'info')
    return redirect(url_for('orcamentos.listar'))

