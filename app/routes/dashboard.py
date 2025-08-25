from flask import Blueprint, redirect, render_template, request, session, url_for

from app.managers.clientes import ClienteManager
from app.managers.pedidos import PedidoManager
from app.models.dashboard import Dashboard

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def dashboard():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
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
