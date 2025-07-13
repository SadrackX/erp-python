# -*- coding: utf-8 -*-
from core import logger
from flask import Flask, render_template, request, redirect, url_for, session, flash
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
            quantidade=int(request.form['quantidade']),
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
    return render_template('pedidos_list.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], pedidos=pedidos)

@app.route('/pedidos/novo', methods=['GET', 'POST'])
def pedidos_novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        novo = Pedido(
            id='',
            id_cliente=request.form['id_cliente'],
            id_forma_pagamento=request.form['id_forma_pagamento'],
            data=datetime.fromisoformat(request.form['data']),
            status=request.form['status'],
            itens=[],  # Itens devem ser cadastrados separadamente
            observacoes=request.form['observacoes'],
            desconto_total=float(request.form['desconto_total']),
            valor_frete=float(request.form['valor_frete'])
        )
        PedidoManager().criar_pedido(novo)
        flash('Pedido cadastrado!')
        return redirect(url_for('pedidos'))
    return render_template('pedidos_form.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
    logout()  # Limpa a sessão ao iniciar o app)
    if not UsuarioManager.get_all():
        logger.log("Usuário admin criado automaticamente")  # Se não houver usuários    
        UsuarioManager.criar_usuario(
        nome="Admin",
        email="admin@erp.com",
        senha="admin123",
        nivel=NivelAcesso.ADMIN
    )
