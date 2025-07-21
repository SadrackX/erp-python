# -*- coding: utf-8 -*-
import json
from logging import log
from core import logger
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify,send_file
from modules import empresa
from modules.auth.manager import UsuarioManager
from modules.auth.models import NivelAcesso
from modules.empresa.manager import EmpresaManager
from modules.relatorios.dashboard import Dashboard
from modules.clientes.manager import ClienteManager
from modules.clientes.models import Cliente
from modules.produtos.manager import ProdutoManager
from modules.produtos.models import Produto
from modules.fornecedores.manager import FornecedorManager
from modules.fornecedores.models import Fornecedor
from modules.pedidos.manager import ItensPedidoManager, PedidoManager
from modules.pedidos.models import Pedido, ItemPedido
import os
from datetime import datetime
from modules.relatorios.logviewer import LogViewer
from flask import session, request
from core.utils import redirecionar_pos_formulario
from werkzeug.utils import secure_filename
from PIL import Image

import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = 'erp_secret_key'

# AUTENTICAÇÃO
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = UsuarioManager().verificar_login(email, senha)
        if usuario:
            session['usuario_nome'] = usuario.nome
            session['usuario_nivel'] = usuario.nivel_acesso.value
            logger.log(f"Usuário {usuario.nome} logado com sucesso.")
            return redirect(url_for('dashboard'))
        else:
            logger.log('Credenciais invalidas!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# DASHBOAR/RESUMO
@app.route('/dashboard')
def dashboard():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    pedidos = PedidoManager().buscar_todos()
    clientes_dict = {c.id: c.nome for c in ClienteManager().buscar_todos()}
    resumo = Dashboard().obter_resumo() if hasattr(Dashboard(), 'obter_resumo') else None
    return render_template(
        'dashboard.html', 
        pedidos=pedidos,
        clientes=clientes_dict,
        usuario_nome=session['usuario_nome'], 
        usuario_nivel=session['usuario_nivel'], 
        resumo=resumo)

# CLIENTES
@app.route('/clientes')
def clientes():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    clientes = ClienteManager().buscar_todos()
    return render_template('clientes_list.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], clientes=clientes)

@app.route('/clientes/novo', methods=['GET', 'POST'])
def clientes_novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))

    editar_id = request.args.get('editar')
    #cliente = ClienteManager().buscar_por_id(editar_id) if editar_id else None
    if request.method == 'POST':
        # Pega informações do form cliente
        form = request.form.to_dict()
        cliente = form  

        if editar_id:        
            # Atualização de cliente existente   
            ClienteManager().atualizar_cliente(editar_id, cliente)
            logger.log(f"Cliente {request.form['nome']} atualizado com sucesso!", 'info')
            return redirect(url_for('clientes'))
        else:          
            # Cadastro de novo cliente  
            ClienteManager().cadastrar_cliente(Cliente.from_dict(cliente))
            logger.log(f"Cliente {request.form['nome']} cadastrado!", 'info')
            return redirect(url_for('clientes'))
    return render_template('clientes_list.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@app.route('/buscar_clientes')
def buscar_clientes():
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

# FORNECEDORES
@app.route('/fornecedores')
def fornecedores():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    fornecedores = FornecedorManager().buscar_todos()
    return render_template('fornecedores_list.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], fornecedores=fornecedores)

@app.route('/fornecedores/novo', methods=['GET', 'POST'])
def fornecedores_novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    fornecedor_id = request.args.get('editar')
    #fornecedor = FornecedorManager().buscar_por_id(fornecedor_id) if fornecedor_id else None
    if request.method == 'POST':

        form = request.form.to_dict()
        fornecedor = form  

        if fornecedor_id:
            # Atualização de fornecedor existente
            FornecedorManager().atualizar_fornecedor(fornecedor_id, fornecedor)
            logger.log(f"Fornecedor {request.form['nome']} atualizado com sucesso!", 'info')
            return redirect(url_for('fornecedores'))
        else:
            # Cadastro de novo fornecedor
            FornecedorManager().cadastrar_fornecedor(Fornecedor.from_dict(fornecedor))
            logger.log(f"Fornecedor {request.form['nome']} cadastrado!", 'info')
            return redirect(url_for('fornecedores'))
    return render_template('fornecedores_list.html', fornecedor=fornecedor, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

# PEDIDOS
@app.route('/pedidos')
def pedidos():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))

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
        if p.status != 'Orçamento':
            p.falta_pagar = max(0, p.total - (p.valor_pago or 0))
            nome_cliente = clientes_dict.get(p.id_cliente, '').lower()

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

@app.route('/pedidos/status/<status>')
def pedidos_por_status(status):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))

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

@app.route('/pedidos/novo', methods=['GET', 'POST'])
def pedidos_novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        cliente_id = request.form['id_cliente']
        form = request.form.to_dict()
        if cliente_id == 'novo':            
            novo_cliente = Cliente.from_dict(form)
            logger.log(f"Cliente {request.form['nome']} cadastrado!", 'info')
            cliente_id = ClienteManager().cadastrar_cliente(novo_cliente)
        novo = Pedido.from_dict(form)
        PedidoManager().criar_pedido(novo)
        logger.log(f"Pedido ID: {novo.id} adicionado!", 'info')
        return redirect(url_for('pedidos'))
    return render_template('pedidos_form.html', pedido=None,cliente=None, produtos=None, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])


@app.route('/pedidos/<pedido_id>/editar', methods=['GET', 'POST'])
def pedido_editar(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))

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
        return redirect(url_for('pedidos'))
    
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
            'desconto_total': request.form.get('desconto_total', pedido.get('desconto_total')),
            'id_cliente': request.form.get('id_cliente'),
            'data_previsao_entrega': data_str,
            'forma_de_pagamento': request.form.get('forma_de_pagamento'),
            'valor_pago': request.form.get('valor_pago',0)
        }
        PedidoManager().atualizar_itens_pedido(pedido_id, produtos_att)
        PedidoManager().atualizar_pedido(pedido_id, novos_dados)
        logger.log(f"Pedido ID: {pedido_id} atualizado!", 'info')
        return redirecionar_pos_formulario('dashboard')
    
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

@app.route('/pedidos/<pedido_id>')
def pedido_detalhes(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    pedido = PedidoManager().buscar_por_id(pedido_id)
    if not pedido:
        logger.log('Pedido não encontrado!', 'error')
        return redirect(url_for('pedidos'))
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

@app.route('/pedidos/<pedido_id>/cancelar')
def pedido_cancelar(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    PedidoManager().cancelar_pedido(pedido_id)
    logger.log(f"Pedido ID: {pedido_id} cancelado!", 'info')
    return redirecionar_pos_formulario('pedidos')


# ORÇAMENTOS
@app.route('/pedidos/orcamentos', methods=['GET', 'POST'])
def orcamentos_novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
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
            desconto_total=float(request.form.get('desconto_total', 0)),
            data_previsao_entrega='',
            forma_de_pagamento='',
            valor_pago=0.0
        )
        pedido_id = PedidoManager().criar_pedido(pedido)

        flash('Orçamento criado com sucesso!')
        return redirect(url_for('pedidos_por_status', status='Orçamento'))  # ou `orcamentos`

    produtos = ProdutoManager().buscar_todos()
    return render_template('orcamentos_form.html', cliente=None, produtos=produtos, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], pedido=None)

@app.route('/pedidos/orcamentos/<pedido_id>/editar', methods=['GET', 'POST'])
def orcamentos_editar(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))

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
        return redirect(url_for('pedidos_por_status', status='Orçamento'))

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
            'desconto_total': request.form.get('desconto_total', pedido.get('desconto_total')),
            'id_cliente': request.form.get('id_cliente'),
            'data_previsao_entrega': data_str,
            'forma_de_pagamento': request.form.get('forma_de_pagamento'),
            'valor_pago': request.form.get('valor_pago',0)
        }
        
        if novos_dados['status'] == 'Orçamento':
            PedidoManager().atualizar_itens_pedido(pedido_id, produtos_att)
            PedidoManager().atualizar_pedido(pedido_id, novos_dados)
            logger.log(f"Orçamento ID: {pedido_id} atualizado!", 'info')
            return redirect(url_for('pedidos_por_status', status='Orçamento'))
        else:
            novos_dados['data'] = datetime.now().isoformat()
            PedidoManager().atualizar_pedido(pedido_id, novos_dados)
            return redirect(url_for('pedido_editar', pedido_id=pedido_id)) 
        
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

@app.route('/orcamentos/<pedido_id>/pedido')
def gerar_pedido(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    PedidoManager().gerar_pedido(pedido_id)
    logger.log(f"Pedido ID: {pedido_id} Criado!", 'info')
    return redirect(url_for('pedidos_por_status', status='Orçamento'))

# PRODUTOS
@app.route('/produtos')
def produtos():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    produtos = ProdutoManager().buscar_todos()
    return render_template('produtos_list.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], produtos=produtos)

@app.route('/produtos/novo', methods=['GET', 'POST'])
def produtos_novo():    
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    produto_id = request.args.get('editar')
    produto = ProdutoManager().buscar_por_id(produto_id) if produto_id else None
    if request.method == 'POST':               
        produto = {
            'id': produto_id or '',
            'nome': request.form['nome'],
            'preco_custo': float(request.form['preco_custo']),
            'preco_venda': float(request.form['preco_venda']),
            'observacao': request.form.get('observacao', ''),
            'ativo': request.form.get('ativo', 'on') == 'on'
        }
        if produto_id:
            # Atualização de produto existente
            ProdutoManager().atualizar_produto(produto_id, produto)
            logger.log(f"Produto {request.form['nome']} atualizado com sucesso!", 'info')
            return redirecionar_pos_formulario('produtos')
        else:
            # Cadastro de novo produto
            ProdutoManager().cadastrar_produto(Produto.from_dict(produto))
            logger.log(f"Produto {request.form['nome']} cadastrado!", 'info')
            return redirecionar_pos_formulario('produtos')
    return render_template('produtos_list.html', produto=produto, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@app.route('/buscar_produtos')
def buscar_produtos():
    termo = request.args.get('q', '').lower()
    produtos = ProdutoManager().buscar_todos()
    resultados = []
    for p in produtos:
        if termo in p.nome.lower():
            resultados.append({
                'id': p.id,
                'nome': p.nome,
                'preco_venda': p.preco_venda
            })
    return jsonify(resultados)

#LOGS
@app.route('/logs')
def logs():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    
    dias = request.args.get('dias', 1)
    try:
        dias = int(dias)
    except ValueError:
        dias = 30

    logs = LogViewer().mostrar_logs(dias)
    logs.sort(key=lambda p: p.data or datetime.min, reverse=True)
    return render_template('logs.html', logs=logs, dias=dias , usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

from reportlab.platypus import Paragraph
#PDF
@app.route('/pedido/<pedido_id>/pdf')
def gerar_pdf_pedido(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    
    p = PedidoManager().buscar_por_id(pedido_id)
    pedido = p.to_dict()
    c = ClienteManager().buscar_por_id(pedido['id_cliente'])
    cliente = c.to_dict()
    itens = ItensPedidoManager().buscar_itens_por_pedido(pedido_id)

    # Dados da empresa
    empresa = EmpresaManager().get_all()[0]  # Considerando uma única empresa
    logo_path = os.path.join('static', empresa.get('logo_path')) if empresa.get('logo_path') else None

    tipo = request.args.get('tipo', 'orcamento')
    titulo = {
        'orcamento': 'Orçamento',
        'ordem_servico': 'Ordem de Serviço',
        'recibo': 'Recibo'
    }.get(tipo, 'Documento')

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading2']
    styleTabela = styles["Normal"]

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=30,
        bottomMargin=30,
        leftMargin=40,
        rightMargin=40
    )

    elementos = []

    # Cabeçalho Empresa com ou sem logo
    if logo_path and os.path.exists(logo_path):
        from reportlab.platypus import Image
        img = Image(logo_path, width=80, height=80)
        dados_empresa = Paragraph(
            f"<b>{empresa['nome']}</b><br/>"
            f"CNPJ: {empresa['cnpj']}<br/>"
            f"{empresa['endereco']}, {empresa['numero']} - {empresa['bairro']}<br/>"
            f"{empresa['cidade']}-{empresa['uf']} - CEP: {empresa['cep']}<br/>"
            f"Telefone: {empresa['celular']} | Email: {empresa['email']}",
            styleN
        )
        from reportlab.platypus import Table
        header = Table([[img, dados_empresa]], colWidths=[90, 400])
        header.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elementos.append(header)
    else:
        elementos.append(Paragraph(f"<b>{empresa['nome']}</b>", styleH))
        elementos.append(Paragraph(
            f"CNPJ: {empresa['cnpj']}<br/>"
            f"{empresa['endereco']}, {empresa['numero']} - {empresa['bairro']}<br/>"
            f"{empresa['cidade']}-{empresa['uf']} - CEP: {empresa['cep']}<br/>"
            f"Telefone: {empresa['celular']} | Email: {empresa['email']}",
            styleN
        ))

    elementos.append(Spacer(1, 12))

    # Título do documento
    elementos.append(Paragraph(f"{titulo} - Pedido #{pedido['id']}", styleH))
    elementos.append(Spacer(1, 6))

    # Informações do cliente
    elementos.append(Paragraph(
        f"<b>Cliente:</b> {cliente['nome']} - "
        f"CPF/CNPJ: {cliente['cpf_cnpj']}<br/>"
        f"Endereço: {cliente['endereco']}, {cliente['numero']} - {cliente['bairro']} - "
        f"{cliente['cidade']}-{cliente['uf']}<br/>"
        f"Telefone: {cliente['celular']} | Email: {cliente['email']}",
        styleN
    ))

    elementos.append(Spacer(1, 12))

    # Tabela de itens
    dados_tabela = [['Produto/Serviço', 'Qtd.', 'Preço Unit. (R$)', 'Subtotal (R$)']]
    total = 0

    for item in itens:
        produto = item.to_dict()
        subtotal = int(produto['quantidade']) * float(produto['preco_unitario'])
        total += subtotal
        nome_produto = Paragraph(produto['nome'], styleTabela)
        dados_tabela.append([
            nome_produto,
            str(produto['quantidade']),
            f"{float(produto['preco_unitario']):.2f}",
            f"{subtotal:.2f}"
        ])

    dados_tabela.append(['', '', 'Total:', f"{total:.2f}"])

    tabela = Table(dados_tabela, colWidths=[300, 40, 80, 80])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.1, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
    ]))

    elementos.append(tabela)

    doc.build(elementos, onFirstPage=adicionar_rodape, onLaterPages=adicionar_rodape)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=False,
        download_name='pedido.pdf',
        mimetype='application/pdf'
    )

def adicionar_rodape(canvas, doc):
    empresa_manager = EmpresaManager()
    empresa = empresa_manager.get_all()[0] if empresa_manager.get_all() else {}
    canvas.saveState()
    #rodape_texto = f"{empresa['nome']} | CNPJ: {empresa['cnpj']} <br/> Tel: {empresa['celular']} | {empresa['email']}"
    
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.grey)
    
    # Linha acima do rodapé
    canvas.line(40, 30, A4[0] - 40, 30)

    # Texto no centro inferior
    linha1 = f"{empresa['nome']} | CNPJ: {empresa['cnpj']}"
    linha2 = f"Tel: {empresa['celular']} | Email: {empresa['email']}"

    x = A4[0] / 2.0
    canvas.drawCentredString(x, 20, linha2)
    canvas.drawCentredString(x, 32, linha1)  # 12 pontos acima da linha2
    
    
    #canvas.drawCentredString(A4[0] / 2.0, 20, rodape_texto)
    
    # Número da página (opcional)
    canvas.drawRightString(A4[0] - 40, 20, f"Página {doc.page}")
    canvas.restoreState()


import time
from flask import Flask, send_from_directory, abort
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# rotas/admin.py ou dentro do seu app principal
@app.route('/admin/empresa', methods=['GET', 'POST'])
def admin_empresa():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))

    empresa_manager = EmpresaManager()
    empresa = empresa_manager.get_all()[0] if empresa_manager.get_all() else {}
    dados_empresa = []
    if request.method == 'POST':
        dados = request.form.to_dict()     

        dados = {
                'id': empresa.get('id', '1'),
                'nome': request.form.get('nome'),
                'cnpj': request.form.get('cnpj'),
                'email': request.form.get('email'),
                'celular': request.form.get('celular'),
                'logo_path': request.form.get('logo_path',''),
                'cep': request.form.get('cep'),
                'endereco': request.form.get('endereco'),
                'numero': request.form.get('numero'),
                'bairro': request.form.get('bairro'),
                'complemento': request.form.get('complemento'),
                'cidade': request.form.get('cidade'),
                'uf': request.form.get('uf'),                
            }
        
        
        if 'logo_file' in request.files:
            file = request.files['logo_file']
            if file and file.filename:
                logo_path = salvar_logo_redimensionada(file)
                if logo_path:
                    dados['logo_path'] = logo_path     

        if empresa:
            if dados['logo_path'] == '':           
                del dados['logo_path']  
            empresa_manager.atualizar_dados(dados)    
            logger.log(f"Dados da empresa {dados['nome']} atualizados!", 'info')
            time.sleep(1)
            redirecionar_pos_formulario('dashboard')
        else:
            empresa_manager.cadastrar_empresa(dados)
            if dados['logo_path'] == '':            
                del dados['logo_path']        
            logger.log(f"Dados da empresa {dados['nome']} adicionados!", 'info')
            time.sleep(1)
            return redirecionar_pos_formulario('dashboard')
        
        dados_empresa = empresa_manager.get_all()
        if dados_empresa:
            dados_empresa = dados_empresa[0]
        else:
            dados_empresa = {}

    return render_template('admin/empresa.html', dados_empresa=empresa, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

def salvar_logo_redimensionada(file):
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ALLOWED_EXTENSIONS:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Redimensiona a imagem para no máximo 300px de largura
        img = Image.open(file)
        img.thumbnail((300, 300))  # largura máx, altura máx
        img.save(filepath)

        return f"uploads/{filename}"
    return None


"""
log("Pedido salvo com sucesso", "info")
log("Cliente não encontrado", "warning")
log("Erro na conexão com o banco", "error")
log("Acesso negado ao usuário admin", "critical")
import colorlog

console_handler = colorlog.StreamHandler()
console_handler.setFormatter(colorlog.ColoredFormatter(
    "%(asctime)s | %(log_color)s%(levelname)-8s%(reset)s | %(message)s",
    datefmt='%d/%m/%Y %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'white',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))
"""

if __name__ == '__main__':
    #app.run(debug=True, port=5001)
    app.run(host='0.0.0.0', port=5000, debug=True)

