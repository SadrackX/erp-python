from flask import Blueprint, redirect, render_template, request, session, url_for

from app.services import logger
from app.managers.fornecedores import FornecedorManager
from app.models.fornecedores import Fornecedor

fornecedores_bp = Blueprint('fornecedores', __name__, url_prefix='/fornecedores')

@fornecedores_bp.route('/listar')
def listar():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    fornecedores = FornecedorManager().buscar_todos()
    return render_template('fornecedores_list.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], fornecedores=fornecedores)
pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')


@fornecedores_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    fornecedor_id = request.args.get('editar')
    fornecedor = request.form.to_dict()
    #fornecedor = FornecedorManager().buscar_por_id(fornecedor_id) if fornecedor_id else None
    if request.method == 'POST':

        """ form = request.form.to_dict()
        fornecedor = form   """

        if fornecedor_id:
            # Atualização de fornecedor existente
            FornecedorManager().atualizar_fornecedor(fornecedor_id, fornecedor)
            logger.log(f"Fornecedor {request.form['nome']} atualizado com sucesso!", 'info')
            return redirect(url_for('fornecedores.listar'))
        else:
            # Cadastro de novo fornecedor
            FornecedorManager().cadastrar_fornecedor(Fornecedor.from_dict(fornecedor))
            logger.log(f"Fornecedor {request.form['nome']} cadastrado!", 'info')
            return redirect(url_for('fornecedores.listar'))
    return render_template('fornecedores_list.html', fornecedor=fornecedor, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])
