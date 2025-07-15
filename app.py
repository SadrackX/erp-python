# -*- coding: utf-8 -*-
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
from modules.pedidos.manager import PedidoManager
from modules.pedidos.models import Pedido, ItemPedido
import os
from datetime import datetime

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
            flash('Credenciais invalidas!')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    resumo = Dashboard().obter_resumo() if hasattr(Dashboard(), 'obter_resumo') else None
    return render_template('dashboard.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], resumo=resumo)

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
    if request.method == 'POST':
        editar_id = request.args.get('editar')
        if editar_id:
            # Atualização de cliente existente
            novos_dados = {
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
            ClienteManager().atualizar_cliente(editar_id, novos_dados)
            flash('Cliente atualizado com sucesso!')
            return redirect(url_for('clientes'))
        else:
            novo = Cliente(
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
            ClienteManager().cadastrar_cliente(novo)
            flash('Cliente cadastrado!')
            return redirect(url_for('clientes'))
    return render_template('clientes_form.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

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
    if request.method == 'POST':
        novo = Produto(
            id='',
            nome=request.form['nome'],
            preco_custo=float(request.form['preco_custo']),
            preco_venda=float(request.form['preco_venda']),
            observacao=request.form['observacao'],
            ativo=True
        )
        ProdutoManager().cadastrar_produto(novo)
        flash('Produto cadastrado!')
        return redirect(url_for('produtos'))
    return render_template('produtos_form.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

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
    if request.method == 'POST':
        produtos_fornecidos = [x.strip() for x in request.form['produtos_fornecidos'].split(',') if x.strip()]
        novo = Fornecedor(
            id='',
            nome=request.form['nome'],
            cnpj=request.form['cnpj'],
            telefone=request.form['telefone'],
            email=request.form['email'],
            produtos_fornecidos=produtos_fornecidos,
            observacoes=request.form['observacoes'],
            ativo=True
        )
        FornecedorManager().cadastrar_fornecedor(novo)
        flash('Fornecedor cadastrado!')
        return redirect(url_for('fornecedores'))
    return render_template('fornecedores_form.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

# PEDIDOS
@app.route('/pedidos')
def pedidos():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    pedidos = PedidoManager().buscar_todos()
    clientes_dict = {c.id: c.nome for c in ClienteManager().buscar_todos()}
    return render_template(
        'pedidos_list.html',
        usuario_nome=session['usuario_nome'],
        usuario_nivel=session['usuario_nivel'],
        pedidos=pedidos,
        clientes=clientes_dict
    )

@app.route('/pedidos/novo', methods=['GET', 'POST'])
def pedidos_novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        import json
        produtos_json = request.form.get('produtos_json')
        itens = []
        if produtos_json:
            produtos = json.loads(produtos_json)
            for p in produtos:
                itens.append(ItemPedido(
                    id_pedido='',
                    id_produto=p['id_produto'],
                    quantidade=p['quantidade'],
                    preco_unitario=p['preco_unitario'],
                    desconto=0.0
                ))
        novo = Pedido(
            id='',
            id_cliente=request.form['id_cliente'],
            id_forma_pagamento=request.form['id_forma_pagamento'] if 'id_forma_pagamento' in request.form else '',
            data=datetime.now(),
            status=request.form['status'],
            itens=itens,
            observacoes=request.form.get('observacoes'),
            desconto_total=float(request.form.get('desconto_total', 0)),
            data_previsao_entrega=None  # Será calculada automaticamente            
        )
        PedidoManager().criar_pedido(novo)
        flash('Pedido cadastrado!')
        return redirect(url_for('pedidos'))
    return render_template('pedidos_form.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@app.route('/pedidos/<pedido_id>')
def pedido_detalhes(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    pedido = PedidoManager().buscar_por_id(pedido_id)
    if not pedido:
        flash('Pedido não encontrado!')
        return redirect(url_for('pedidos'))
    cliente = ClienteManager().buscar_por_id(pedido.id_cliente)
    produtos = []
    for item in pedido.itens:
        prod = ProdutoManager().buscar_por_id(item.id_produto)
        produtos.append({
            'nome': prod.nome if prod else 'Produto removido',
            'preco_unitario': item.preco_unitario,
            'quantidade': item.quantidade,
            'total': item.total
        })
    return render_template('pedido_detalhes.html', pedido=pedido, cliente=cliente, produtos=produtos, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@app.route('/pedidos/<pedido_id>/editar', methods=['GET', 'POST'])
def pedido_editar(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    pedido = PedidoManager().buscar_por_id(pedido_id)
    if not pedido:
        flash('Pedido não encontrado!')
        return redirect(url_for('pedidos'))
    if request.method == 'POST':
        novos_dados = {
            'status': request.form['status'],
            'observacoes': request.form.get('observacoes'),
            'desconto_total': request.form.get('desconto_total', pedido.desconto_total),
            'valor_frete': request.form.get('valor_frete', pedido.valor_frete)
        }
        PedidoManager().atualizar_pedido(pedido_id, novos_dados)
        flash('Pedido atualizado!')
        return redirect(url_for('pedido_detalhes', pedido_id=pedido_id))
    return render_template('pedido_editar.html', pedido=pedido, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@app.route('/pedidos/<pedido_id>/cancelar')
def pedido_cancelar(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    PedidoManager().cancelar_pedido(pedido_id)
    flash('Pedido cancelado!')
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
