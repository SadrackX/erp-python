﻿# -*- coding: utf-8 -*-
import json
from logging import log
from core import logger
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from modules.auth.manager import UsuarioManager
from modules.auth.models import NivelAcesso
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

app = Flask(__name__)
app.secret_key = 'erp_secret_key'

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
    cliente = ClienteManager().buscar_por_id(editar_id) if editar_id else None
    if request.method == 'POST':
        cliente = {
            'nome': request.form['nome'],
            'tipo': request.form['tipo'],
            'cpf_cnpj': request.form['cpf_cnpj'],
            'email': request.form['email'],
            'celular': request.form['celular'],
            'endereco': request.form['endereco'],
            'bairro': request.form['bairro'],
            'cidade': request.form['cidade'],
            'cep': request.form['cep'],
            'uf': request.form['uf'],
            'ativo': True
        }       
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
            return redirect(url_for('produtos'))
        else:
            # Cadastro de novo produto
            ProdutoManager().cadastrar_produto(Produto.from_dict(produto))
            logger.log(f"Produto {request.form['nome']} cadastrado!", 'info')
            return redirect(url_for('produtos'))
    return render_template('produtos_list.html', produto=produto, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

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
    fornecedor = FornecedorManager().buscar_por_id(fornecedor_id) if fornecedor_id else None
    if request.method == 'POST':
        fornecedor = {
            'id': fornecedor_id or '',
            'nome': request.form['nome'],
            'cnpj': request.form['cnpj'],
            'email': request.form['email'],
            'telefone': request.form['telefone'],
            'produtos_fornecidos': request.form.get('produtos_fornecidos', ''),
            'observacoes': request.form.get('observacoes', ''),
            'ativo': request.form.get('ativo', 'on') == 'on'
        }
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

    # Aplica filtros
    pedidos_filtrados = []
    for p in todos_pedidos:
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

    return render_template(
        'pedidos_list.html',
        usuario_nome=session['usuario_nome'],
        usuario_nivel=session['usuario_nivel'],
        pedidos=pedidos_filtrados,
        clientes=clientes_dict,
        cliente_filtro=cliente_filtro,
        status_filtro=status_filtro,
        data_inicio=data_inicio_str,
        data_fim=data_fim_str
    )

@app.route('/pedidos/novo', methods=['GET', 'POST'])
def pedidos_novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
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
        if cliente_id == 'novo':
            novo_cliente = Cliente(
                id='',
                nome=request.form['nome'],
                tipo=request.form['tipo'],
                cpf_cnpj=request.form['cpf_cnpj'],
                email=request.form['email'],
                celular=request.form['celular'],
                endereco=request.form['endereco'],
                bairro=request.form['bairro'],
                cidade=request.form['cidade'],
                cep=request.form['cep'],
                uf=request.form['uf'],
                observacoes=None,
                ativo=True
            )
            cliente_id = ClienteManager().cadastrar_cliente(novo_cliente)
        novo = Pedido(
            id='',
            id_cliente=cliente_id,
            data=datetime.now(),
            status=request.form['status'],
            itens=itens,
            observacoes=request.form.get('observacoes'),
            desconto_total=float(request.form.get('desconto_total', 0)),
            data_previsao_entrega=data_str,
            forma_de_pagamento=request.form.get('forma_de_pagamento'),
            valor_pago=float(request.form.get('valor_pago', 0))
        )
        PedidoManager().criar_pedido(novo)
        flash('Pedido cadastrado!')
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
        logger.log(f"Pedido {pedido_id} atualizado!", 'info')
        return redirect(url_for('pedidos'))
    
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

@app.route('/pedidos/status/<status>')
def pedidos_por_status(status):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))

    pedidos = PedidoManager().buscar_todos()
    pedidos_filtrados = [p for p in pedidos if p.status.lower() == status.lower()]
    clientes_dict = {c.id: c.nome for c in ClienteManager().buscar_todos()}

    return render_template(
        'pedidos_list.html',
        usuario_nome=session['usuario_nome'],
        usuario_nivel=session['usuario_nivel'],
        pedidos=pedidos_filtrados,
        clientes=clientes_dict,
        titulo=f"Pedidos - {status}"
    )

@app.route('/pedidos/<pedido_id>/cancelar')
def pedido_cancelar(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    PedidoManager().cancelar_pedido(pedido_id)
    logger.log(f"Pedido {pedido_id} cancelado!", 'info')
    return redirect(url_for('pedidos'))

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
            resultados.append({
                'id': c.id,
                'nome': c.nome,
                'tipo': c.tipo,
                'cpf_cnpj': c.cpf_cnpj,
                'email': c.email,
                'celular': c.celular,
                'endereco': c.endereco,
                'bairro': c.bairro,
                'cidade': c.cidade,
                'cep': c.cep,
                'uf': c.uf
            })
    return jsonify(resultados)

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
    
    dias = request.args.get('dias', 30)
    try:
        dias = int(dias)
    except ValueError:
        dias = 30

    logs = LogViewer().mostrar_logs(dias)
    return render_template('logs.html', logs=logs, dias=dias , usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)

