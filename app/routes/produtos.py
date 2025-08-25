from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.services import logger
from app.core.utils import redirecionar_pos_formulario
from app.managers.produtos import ProdutoManager
from app.models.produtos import Produto

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')

@produtos_bp.route('/')
def listar():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    produtos = ProdutoManager().buscar_todos()
    return render_template('produtos_list.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], produtos=produtos)

@produtos_bp.route('/novo', methods=['GET', 'POST'])
def novo():    
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
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
            return redirecionar_pos_formulario('produtos.listar')
        else:
            # Cadastro de novo produto
            ProdutoManager().cadastrar_produto(Produto.from_dict(produto))
            logger.log(f"Produto {request.form['nome']} cadastrado!", 'info')
            return redirecionar_pos_formulario('produtos.listar')
    return render_template('produtos_list.html', produto=produto, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@produtos_bp.route('/buscar')
def buscar():
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
