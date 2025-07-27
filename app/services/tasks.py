import time
import schedule
from app.managers.backup import BackupManager
from app.services.pedidos import verificar_e_atualizar_status_pedidos
from app.services import logger

def agendar_backups():
    manager = BackupManager()
    def executar_backup():
        logger.log('Iniciando backup automático.', 'info')
        manager.criar_backup("backup_automatico")
        logger.log('Backup concluído.', 'info')

    schedule.every().day.at("23:59").do(executar_backup)

def agendar_verificacao_pedidos():
    def executar_verificacao():
        #logger.log('Verificando e atualizando status dos pedidos.', 'info')
        verificar_e_atualizar_status_pedidos()
        #logger.log('Verificação concluída.', 'info')
    
    schedule.every(5).minutes.do(executar_verificacao)

def iniciar_agendador():
    agendar_backups()
    agendar_verificacao_pedidos()

    logger.log('Agendador iniciado.', 'info')
    while True:
        schedule.run_pending()
        time.sleep(60)
