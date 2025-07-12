import schedule
import time
from scripts.backup import BackupManager

def agendar_backups():
    """Agenda backups diários automáticos"""
    manager = BackupManager()
    
    # Backup diário às 23:59
    schedule.every().day.at("23:59").do(
        manager.criar_backup, "backup_automatico"
    )
    
    while True:
        schedule.run_pending()
        time.sleep(60)