import os
from flask import Flask, redirect, url_for

from app.managers.empresa import EmpresaManager

def create_app():
    app = Flask(
    __name__,
    template_folder='templates')

    app.config['SECRET_KEY'] = 'erp_secret_key'
    #app.secret_key = 'erp_secret_key'

    # Caminhos adicionais, caso precise importar CSV, logs etc
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['BASE_DIR'] = base_dir

    with app.app_context():
        print("\nRotas registradas:")
        for rule in app.url_map.iter_rules():
            print(rule)

    # Importa e registra os blueprints das rotas
    from .routes.auth import auth_bp
    from .routes.pedidos import pedidos_bp
    from .routes.clientes import clientes_bp
    from .routes.fornecedores import fornecedores_bp
    from .routes.admin import admin_bp
    from .routes.dashboard import dashboard_bp
    from .routes.produtos import produtos_bp
    from .routes.gerar_pdf import gerar_pdf_bp
    from .routes.logs import logs_bp
    from .routes.orcamentos import orcamentos_bp
    from .routes.backups import backup_bp
    from .routes.api_atualizar_status import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(fornecedores_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(gerar_pdf_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(orcamentos_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    @app.context_processor
    def inject_empresa():
        try:
            empresa = EmpresaManager().get_all()[0]
        except Exception:
            empresa = {
                "nome": "Empresa não cadastrada",
                "cnpj": "00.000.000/0000-00",
                "endereco": "Endereço não cadastrado",
                "numero": "SN",
                "bairro": '',
                "cidade": '',
                "uf": '',
                "celular": "(00) 0000-0000"
            }
        return dict(empresa=empresa)
    
    return app


