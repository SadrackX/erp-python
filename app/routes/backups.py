from flask import Blueprint, render_template, redirect, session, url_for, flash
from app.managers.backup import BackupManager

backup_bp = Blueprint('backups', __name__, url_prefix='/backups')
manager = BackupManager(limite_backups=5)

@backup_bp.route('/listar')
def listar():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    backups = manager.listar_backups()
    return render_template('backups.html',
                            usuario_nome=session['usuario_nome'],
                            usuario_nivel=session['usuario_nivel'],
                            backups=backups)

@backup_bp.route('/criar')
def criar():
    nome = f"manual_{manager.data_hora_atual()}"
    manager.criar_backup("manual")
    flash(f'Backup {nome} criado com sucesso!', 'success')
    return redirect(url_for('backups.listar'))

@backup_bp.route('/restaurar/<nome>')
def restaurar(nome):
    manager.restaurar_backup(nome)
    flash(f'Backup {nome} restaurado!', 'success')
    return redirect(url_for('backups.listar'))

@backup_bp.route('/excluir/<nome>')
def excluir(nome):
    manager.excluir_backup(nome)
    flash(f'Backup {nome} excluído.', 'warning')
    return redirect(url_for('backups.listar'))
