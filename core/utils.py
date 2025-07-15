from datetime import datetime, timedelta

def add_dias_uteis(data: datetime, dias: int) -> datetime:
    """
    Adiciona dias úteis (exclui sábados e domingos)
    Exemplo: sexta + 3 dias = quarta-feira seguinte
    """
    data_calculada = data
    dias_adicionados = 0
    
    while dias_adicionados < dias:
        data_calculada += timedelta(days=1)
        # 0-4 = segunda a sexta
        if data_calculada.weekday() < 5:
            dias_adicionados += 1
            
    return data_calculada