import os
import time
from flask import Blueprint, redirect, render_template, request, session, url_for

from app.services import logger
from app.core.utils import redirecionar_pos_formulario
from app.managers.empresa import EmpresaManager
from PIL import Image
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# rotas/admin.py ou dentro do seu app principal

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/empresa', methods=['GET', 'POST'])
def empresa():
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))

    empresa_manager = EmpresaManager()
    empresa = empresa_manager.get_all()[0] if empresa_manager.get_all() else {}
    dados_empresa = []
    if request.method == 'POST':
        dados = request.form.to_dict()     

        dados = {
                'id': empresa.get('id', '1'),
                'nome': request.form.get('nome'),
                'cnpj': request.form.get('cnpj'),
                'email': request.form.get('email'),
                'celular': request.form.get('celular'),
                'logo_path': request.form.get('logo_path',''),
                'cep': request.form.get('cep'),
                'endereco': request.form.get('endereco'),
                'numero': request.form.get('numero'),
                'bairro': request.form.get('bairro'),
                'complemento': request.form.get('complemento'),
                'cidade': request.form.get('cidade'),
                'uf': request.form.get('uf'),                
            }
        
        
        if 'logo_file' in request.files:
            file = request.files['logo_file']
            if file and file.filename:
                logo_path = salvar_logo_redimensionada(file)
                if logo_path:
                    dados['logo_path'] = logo_path     

        if empresa:
            if dados['logo_path'] == '':           
                del dados['logo_path']  
            empresa_manager.atualizar_dados(dados)    
            logger.log(f"Dados da empresa {dados['nome']} atualizados!", 'info')
            time.sleep(1)
            redirecionar_pos_formulario('dashboard.dashboard')
        else:
            empresa_manager.cadastrar_empresa(dados)
            if dados['logo_path'] == '':            
                del dados['logo_path']        
            logger.log(f"Dados da empresa {dados['nome']} adicionados!", 'info')
            time.sleep(1)
            return redirecionar_pos_formulario('dashboard.dashboard')
        
        dados_empresa = empresa_manager.get_all()
        if dados_empresa:
            dados_empresa = dados_empresa[0]
        else:
            dados_empresa = {}

    return render_template('admin/empresa.html', dados_empresa=empresa, usuario_nome=session['usuario_nome'], usuario_nivel=session['usuario_nivel'])

def salvar_logo_redimensionada(file):
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ALLOWED_EXTENSIONS:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Redimensiona a imagem para no máximo 300px de largura
        img = Image.open(file)
        img.thumbnail((300, 300))  # largura máx, altura máx
        img.save(filepath)

        return f"uploads/{filename}"
    return None
