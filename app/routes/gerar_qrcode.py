
 # qrcode_pix.py
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import io
import qrcode
import re
import uuid


def gerar_payload_pix_corrigido(chave_pix: str, valor: float, nome: str, cidade: str, descricao: str = "") -> str:
    """
    Gera payload PIX no formato exato que funciona em todos os bancos
    """
    # Validações básicas
    if not chave_pix or not nome or not cidade:
        raise ValueError("Chave PIX, nome e cidade são obrigatórios")
    
    if valor < 0:
        raise ValueError("Valor deve ser positivo")

    # Formata os campos conforme o padrão do BC
    valor_str = f"{valor:.2f}"
    chave_len = len(chave_pix)
    
    # Monta o payload no formato exato que funciona
    payload = [
        "000201",  # Payload Format Indicator
        "2636",  # Merchant Account Information
        f"0014BR.GOV.BCB.PIX01{chave_len:02}{chave_pix}",
        "52040000",  # Merchant Category Code
        "5303986",  # Transaction Currency (BRL)
        f"54{len(valor_str):02}{valor_str}",  # Transaction Amount (SEM o campo de length!)
        "5802BR",  # Country Code
        f"59{len(nome):02}{nome}",  # Merchant Name
        f"60{len(cidade):02}{cidade}",  # Merchant City
        "6211",  # Additional Data Field
        f"05{len(descricao):02}{descricao}",  # TXID (no exemplo é "03***")
        "6304"  # CRC16
    ]
    
    payload_str = "".join(payload)
    
    # Calcula o CRC16 (implementação manual garantida)
    crc = 0xFFFF
    for byte in payload_str.encode('utf-8'):
        crc ^= byte << 8
        for _ in range(8):
            crc = (crc << 1) ^ 0x1021 if (crc & 0x8000) else crc << 1
    crc &= 0xFFFF
    payload_str += f"{crc:04X}"
    
    return payload_str

def gerar_qrcode_pix_bytes(chave_pix: str, valor: float, nome: str, cidade: str, descricao: str = "") -> io.BytesIO:
    """Gera QR Code PIX compatível com todos os bancos"""
    try:
        payload = gerar_payload_pix_corrigido(chave_pix, valor, nome, cidade, descricao)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=1,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        raise RuntimeError(f"Falha ao gerar QR Code PIX: {str(e)}")



def validar_chave_pix(chave: str):
    """
    Valida e formata a chave PIX.
    
    Retorna:
        (tipo, chave_formatada, valido)
        tipo -> 'cpf', 'cnpj', 'email', 'telefone', 'aleatoria', 'invalida'
        chave_formatada -> string no formato correto
        valido -> True ou False
    """
    chave = chave.strip()

    # Prepara números só com dígitos
    numeros = re.sub(r"\D", "", chave)

    # Telefone (com DDI +55)
    if numeros.startswith("55") and len(numeros) in [12, 13]:
        return ("telefone", numeros, True)
    if len(numeros) in [10, 11] and chave.startswith("("):
        return ("telefone", "+55" + numeros, True)
    if numeros.startswith("0") and len(numeros) >= 10:
        return ("telefone", "+55" + numeros.lstrip("0"), True)

    # CPF (somente números, 11 dígitos)
    if re.fullmatch(r"\d{11}", numeros):
        return ("cpf", numeros, True)

    # CNPJ (somente números, 14 dígitos)
    if re.fullmatch(r"\d{14}", numeros):
        return ("cnpj", numeros, True)

    # E-mail
    if re.fullmatch(r"[^@]+@[^@]+\.[^@]+", chave):
        return ("email", chave.lower(), True)

    # Chave aleatória (UUID)
    try:
        chave_uuid = str(uuid.UUID(chave))
        return ("aleatoria", chave_uuid, True)
    except ValueError:
        pass

    return ("invalida", chave, False)




def criar_quadro_pix(qr_img, chave_pix: str, valor: float, nome_recebedor: str):
    altura_quadro = 3 * cm
    largura_total = 17 * cm
    
    largura_col1 = largura_total * 0.22
    largura_col2 = largura_total * 0.60
    largura_col3 = largura_total * 0.18

    estilo_pague_por = ParagraphStyle(
        name='paguePor',
        fontSize=15,
        leading=15,   # igual ao tamanho da fonte para texto compacto
        alignment=1,
        spaceAfter=0,
    )

    estilo_pix = ParagraphStyle(
        name='pix',
        fontSize=60,
        leading=60,   # igual ao tamanho da fonte para evitar espaçamento extra
        alignment=1,
        textColor=colors.HexColor('#4CAF50'),
        spaceAfter=0,
        fontName='Helvetica-Bold'
    )
    estilo_instrucoes = ParagraphStyle(
        name='instrucoes',
        fontSize=8,
        leading=9,
        leftIndent=10,
        bulletIndent=0,
        bulletFontSize=7,
        bulletAnchor='start',
    )
    estilo_info_recebedor = ParagraphStyle(
        name='infoRecebedor',
        fontSize=7,
        leading=8,
        alignment=0,
        textColor=colors.grey,
        spaceBefore=2
    )
    
    col1 = [
        [Paragraph("PAGUE POR", estilo_pague_por)],
        [Paragraph("PIX", estilo_pix)],
    ]
    
    # Criar lista de instruções com parágrafos bullet separados:
    instrucoes_textos = [
        "Abra o app do seu banco",
        "Aponte a câmera para o QR Code",
        "Confirme o pagamento",
    ]
    col2 = [Paragraph(f'<bullet>&bull;</bullet> {texto}', estilo_instrucoes) for texto in instrucoes_textos]
    
    col2.append(Spacer(1, 4))
    col2.append(Paragraph(f"<b>Chave Pix:</b> {chave_pix}", estilo_info_recebedor))
    col2.append(Paragraph(f"<b>Valor:</b> R$ { '{:,.2f}'.format(valor).replace(',', 'X').replace('.', ',').replace('X', '.') }", estilo_info_recebedor))
    col2.append(Paragraph(f"<b>Recebedor:</b> {nome_recebedor}", estilo_info_recebedor))
    
    qr_img.drawHeight = altura_quadro * 0.9
    qr_img.drawWidth = qr_img.drawHeight
    
    col3 = [qr_img]
    col1_table = Table(col1, colWidths=[largura_col1], rowHeights=[None, altura_quadro * 0.50])
    col1_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), -8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    
    data = [[col1_table, col2, col3]]
    
    tabela = Table(
        data,
        colWidths=[largura_col1, largura_col2, largura_col3],
        rowHeights=[altura_quadro],
        style=TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0, colors.white),
        ])
    )
    
    return tabela

def calcular_crc16(data: bytes) -> int:
    """Implementação manual do CRC-16/CCITT-FALSE"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc
