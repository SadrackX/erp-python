from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.models.despesas import Despesas
from app.managers.despesas import DespesasManager

manager = DespesasManager()

def calcular_vencimento(base: datetime, incremento: int, frequencia: str) -> datetime:
    """Calcula nova data de vencimento baseada na frequência"""
    if frequencia == "trimestral":
        return base + relativedelta(months=+incremento*3)
    elif frequencia == "semestral":
        return base + relativedelta(months=+incremento*6)
    elif frequencia == "anual":
        return base + relativedelta(years=+incremento)
    else:  # Mensal
        return base + relativedelta(months=+incremento)

def criar_despesa(descricao: str, valor: float, data_vencimento: datetime, 
                tipo: str, parcelas: int = 1, recorrencia: str = None):
    despesas = []
    
    if tipo == "parcelado" and parcelas > 1:
        for i in range(parcelas):
            nova_data = calcular_vencimento(data_vencimento, i, "mensal")
            despesa = Despesas(
                id='',  # Será gerado pelo manager
                status="Pendente",
                descricao=f"{descricao} ({i+1}/{parcelas})",
                valor=round(valor / parcelas, 2),
                data_vencimento=nova_data,
                parcela_atual=i+1,
                total_parcelas=parcelas
            )
            manager.cadastrar(despesa)
            despesas.append(despesa)
            
    elif tipo == "recorrente":
        for i in range(12):  # 12 meses
            nova_data = calcular_vencimento(data_vencimento, i, recorrencia)
            despesa = Despesas(
                id='',
                status="Pendente",
                descricao=f"{descricao} ({nova_data.strftime('%m/%Y')})",
                valor=valor,
                data_vencimento=nova_data,
                recorrencia=recorrencia
            )
            manager.cadastrar(despesa)
            despesas.append(despesa)
            
    else:  # Pagamento único
        despesa = Despesas(
            id='',
            status="Pendente",
            descricao=descricao,
            valor=valor,
            data_vencimento=data_vencimento,
            parcela_atual=1,
            total_parcelas=1
        )
        manager.cadastrar(despesa)
        despesas.append(despesa)
        
    return despesas