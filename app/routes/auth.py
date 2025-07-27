
from flask import Blueprint, redirect, render_template, request, session, url_for
from app.services import logger
from app.managers.auth import UsuarioManager
#from ..services.auth import

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_nome' in session:
        return redirect(url_for('dashboard.dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = UsuarioManager().verificar_login(email, senha)
        if usuario:
            session['usuario_nome'] = usuario.nome
            session['usuario_nivel'] = usuario.nivel_acesso.value
            logger.log(f"Usuário {usuario.nome} logado com sucesso.")
            return redirect(url_for('dashboard.dashboard'))
        else:
            logger.log('Credenciais invalidas!', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

