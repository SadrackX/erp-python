from datetime import datetime, timedelta
from flask import request, redirect, url_for

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

def redirecionar_pos_formulario(padrao='dashboard'):
    """
    Redireciona para a URL do campo 'next' do formulário, se existir,
    ou para a rota padrão passada.
    """
    proxima_url = request.form.get('next')
    return redirect(proxima_url or url_for(padrao))