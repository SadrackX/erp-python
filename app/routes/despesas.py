from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from datetime import datetime
from app.services import despesas as service
from app.managers.despesas import DespesasManager

despesas_bp = Blueprint("despesas", __name__, url_prefix="/despesas")
manager = DespesasManager()

@despesas_bp.route("/")
def index():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    despesas = DespesasManager().buscar_todos()
    return render_template("despesas_list.html", despesas=despesas, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

@despesas_bp.route("/novo", methods=["POST"])
def novo():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    try:
        descricao = request.form["descricao"]
        valor = float(request.form["valor"])
        data_vencimento = datetime.strptime(request.form["data_vencimento"], "%Y-%m-%d")
        tipo = request.form.get("tipo", "unico")
        parcelas = int(request.form.get("parcelas") or 1)
        recorrencia = request.form.get("recorrencia")

        despesas_criadas = service.criar_despesa(
            descricao=descricao,
            valor=valor,
            data_vencimento=data_vencimento,
            tipo=tipo,
            parcelas=parcelas,
            recorrencia=recorrencia
        )

        flash(f"{len(despesas_criadas)} despesa(s) criada(s) com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao criar despesa: {str(e)}", "danger")
    
    return redirect(url_for("despesas.index"))

@despesas_bp.route("/excluir/<id>")
def excluir(id):
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    manager.excluir(id)
    flash("Despesa excluída com sucesso.", "success")
    return redirect(url_for("despesas.index"))

@despesas_bp.route("/editar/<id>", methods=["GET", "POST"])
def editar(id):
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    despesa = manager.buscar_por_id(id)
    
    if request.method == "POST":
        dados = {
            'descricao': request.form.get('descricao'),
            'valor': float(request.form.get('valor')),
            'data_vencimento': datetime.strptime(request.form.get('data_vencimento'), "%Y-%m-%d"),
            'status': request.form.get('status')
        }
        if manager.atualizar(id, dados):
            flash("Despesa atualizada com sucesso!", "success")
        return redirect(url_for("despesas.index"))
    
    return render_template("editar_despesa.html", despesa=despesa)

@despesas_bp.route("/pagar/<id>")
def pagar(id):
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    despesa = manager.buscar_por_id(id)
    if despesa:
        manager.atualizar(id, {
            'status': 'Pago',
            'data_pagamento': datetime.now()
        })
        flash("Despesa marcada como paga!", "success")
    return redirect(url_for("despesas.index"))

@despesas_bp.route("/filtrar", methods=["POST"])
def filtrar():
    status = request.form.get("status")
    despesas = manager.buscar_por_status(status) if status else manager.buscar_todos()
    return render_template("despesas_list.html", despesas=despesas)

@despesas_bp.route("/relatorios")
def relatorios():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    # Despesas por status
    status_counts = manager.buscar_por_status()
    
    # Total a pagar
    total_pendente = sum(
        c.valor for c in manager.buscar_por_status("Pendente") 
        if not c.recorrencia
    )
    
    # Próximos vencimentos
    proximas = manager.buscar_proximos_vencimentos(15)
    
    return render_template("relatorios.html", 
                          status_counts=status_counts,
                          total_pendente=total_pendente,
                          proximas=proximas, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])