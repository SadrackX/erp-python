import os
from flask import Blueprint, redirect, render_template, request, send_file, session, url_for
import io
from reportlab.graphics.barcode.qr import QrCode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet


from app.managers.clientes import ClienteManager
from app.managers.empresa import EmpresaManager
from app.managers.itens import ItensPedidoManager
from app.managers.pedidos import PedidoManager
from app.routes.gerar_qrcode import validar_chave_pix, gerar_qrcode_pix_bytes, criar_quadro_pix

gerar_pdf_bp = Blueprint('gerar_pdf', __name__, url_prefix='/gerar_pdf')

@gerar_pdf_bp.route('/<pedido_id>/pdf', methods=['GET', 'POST'])
def gerar(pedido_id):
    if 'usuario_nome' not in session:
        return redirect(url_for('auth.login'))
    
    p = PedidoManager().buscar_por_id(pedido_id)
    pedido = p.to_dict()
    c = ClienteManager().buscar_por_id(pedido['id_cliente'])
    cliente = c.to_dict()
    itens = ItensPedidoManager().buscar_itens_por_pedido(pedido_id)

    # Dados da empresa
    empresa = EmpresaManager().get_all()[0]  # Considerando uma única empresa
    logo_path = os.path.join('app/static', empresa.get('logo_path')) if empresa.get('logo_path') else None

    tipo = request.args.get('tipo', 'orcamento')
    titulo = {
        'orcamento': 'Orçamento',
        'ordem_servico': 'Ordem de Serviço',
        'recibo': 'Recibo'
    }.get(tipo, 'Documento')             

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading2']
    styleTabela = styles["Normal"]

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=30,
        bottomMargin=30,
        leftMargin=40,
        rightMargin=40
    )

    elementos = []

    # Cabeçalho Empresa com ou sem logo
    if logo_path and os.path.exists(logo_path):
        img = Image(logo_path, width=80, height=80)
        dados_empresa = Paragraph(
            f"<b>{empresa['nome']}</b><br/>"
            f"CNPJ: {empresa['cnpj']}<br/>"
            f"{empresa['endereco']}, {empresa['numero']} - {empresa['bairro']}<br/>"
            f"{empresa['cidade']}-{empresa['uf']} - CEP: {empresa['cep']}<br/>"
            f"Telefone: {empresa['celular']} | Email: {empresa['email']}",
            styleN
        )
        header = Table([[img, dados_empresa]], colWidths=[90, 400])
        header.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elementos.append(header)
    else:
        elementos.append(Paragraph(f"<b>{empresa['nome']}</b>", styleH))
        elementos.append(Paragraph(
            f"CNPJ: {empresa['cnpj']}<br/>"
            f"{empresa['endereco']}, {empresa['numero']} - {empresa['bairro']}<br/>"
            f"{empresa['cidade']}-{empresa['uf']} - CEP: {empresa['cep']}<br/>"
            f"Telefone: {empresa['celular']} | Email: {empresa['email']}",
            styleN
        ))

    elementos.append(Spacer(1, 12))

    # Título do documento
    elementos.append(Paragraph(f"{titulo} - Pedido #{pedido['id']}", styleH))
    elementos.append(Spacer(1, 6))

    # Informações do cliente
    elementos.append(Paragraph(
        f"<b>Cliente:</b> {cliente['nome']}"
        f"<br/><b>CPF/CNPJ:</b> {cliente['cpf_cnpj']}<br/>"
        f"<b>Endereço:</b> {cliente['endereco']}, {cliente['numero']} - {cliente['bairro']} - "
        f"{cliente['cidade']}-{cliente['uf']}<br/>"
        f"<b>Telefone:</b> {cliente['celular']} <b>| Email:</b> {cliente['email']}",
        styleN
    ))

    elementos.append(Spacer(1, 12))

    # Tabela de itens
    dados_tabela = [['Produto/Serviço', 'Qtd.', 'Preço Unit. (R$)', 'Subtotal (R$)']]
    total = 0

    for item in itens:
        produto = item.to_dict()
        subtotal = int(produto['quantidade']) * float(produto['preco_unitario'])
        total += subtotal
        nome_produto = Paragraph(produto['nome'], styleTabela)
        dados_tabela.append([
            nome_produto,
            str(produto['quantidade']),
            f"{ '{:,.2f}'.format(float(produto['preco_unitario'])).replace(',', 'X').replace('.', ',').replace('X', '.')}",
            f"{ '{:,.2f}'.format(subtotal).replace(',', 'X').replace('.', ',').replace('X', '.') }"
            
        ])
    dados_tabela.append(['', '', 'Total:', f"{ '{:,.2f}'.format(total).replace(',', 'X').replace('.', ',').replace('X', '.') }"])

    tabela = Table(dados_tabela, colWidths=[300, 40, 80, 80])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.1, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
    ]))

    elementos.append(tabela)
    
    if pedido['observacoes']:
        from xml.sax.saxutils import escape
        observacoes = pedido.get('observacoes', '')
        texto_escapado = escape(observacoes).replace('\n', '<br/>')  # mostra tudo como texto
        elementos.append(Paragraph(f"<br/><b>OBS:</b> <br/>{texto_escapado}", styles["Normal"]))

    # Adiciona QR Code Pix se disponível
    if (valido := validar_chave_pix(empresa['celular'])) and (valido[0] != 'invalida') and titulo.lower() == 'recibo':
        qr_buffer = gerar_qrcode_pix_bytes(
            chave_pix=valido[1],
            valor=total,
            nome=empresa['nome'][:25],
            cidade='SOUSA',
            descricao=f"PED{pedido_id}"
        )
        qr_img = Image(qr_buffer, width=5 * 28.35, height=5 * 28.35)
        elementos.append(Spacer(1, 20))
        elementos.append(criar_quadro_pix(qr_img, valido[1], total, empresa['nome']))

    doc.build(elementos, onFirstPage=adicionar_rodape, onLaterPages=adicionar_rodape)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=False,
        download_name='pedido.pdf',
        mimetype='application/pdf'
        #pedido=pedido, cliente=cliente, produtos=produtos
    )

def adicionar_rodape(canvas, doc):
    empresa_manager = EmpresaManager()
    empresa = empresa_manager.get_all()[0] if empresa_manager.get_all() else {}
    canvas.saveState()
    #rodape_texto = f"{empresa['nome']} | CNPJ: {empresa['cnpj']} <br/> Tel: {empresa['celular']} | {empresa['email']}"
    
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.grey)
    
    # Linha acima do rodapé
    canvas.line(40, 30, A4[0] - 40, 30)

    # Texto no centro inferior
    linha1 = f"{empresa['nome']} | CNPJ: {empresa['cnpj']}"
    linha2 = f"Tel: {empresa['celular']} | Email: {empresa['email']}"

    x = A4[0] / 2.0
    canvas.drawCentredString(x, 20, linha2)
    canvas.drawCentredString(x, 32, linha1)  # 12 pontos acima da linha2
    
    
    #canvas.drawCentredString(A4[0] / 2.0, 20, rodape_texto)
    
    # Número da página (opcional)
    canvas.drawRightString(A4[0] - 40, 20, f"Página {doc.page}")
    canvas.restoreState()

def moeda(valor):
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
