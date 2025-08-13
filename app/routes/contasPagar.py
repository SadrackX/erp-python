from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.managers.contasPagar import ContasPagar, contasPagarManager
from app.services import logger
from app.core.utils import redirecionar_pos_formulario

contasPagar_bp = Blueprint('contasPagar', __name__, url_prefix='/contasPagar')

@contasPagar_bp.route('/listar')
def listar():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    dados = contasPagarManager().buscar_todos()
    return render_template('contas_list.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], contas=dados)

@contasPagar_bp.route('/novo', methods=['GET', 'POST'])
def novo():    
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))    
    if request.method == 'POST':
        dados = request.form.to_dict()
        contasPagarManager.cadastrar(dados)
        logger.log(f"Conta a pagar cadastrada!", 'info')
    return render_template('contas_list.html', usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'], contas=dados)
