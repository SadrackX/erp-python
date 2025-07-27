from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session, url_for

from app.services.logviewer import LogViewer


logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

@logs_bp.route('/listar')
def listar():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    
    dias = request.args.get('dias', 1)
    try:
        dias = int(dias)
    except ValueError:
        dias = 30

    logs = LogViewer().mostrar_logs(dias)
    logs.sort(key=lambda p: p.data or datetime.min, reverse=True)
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