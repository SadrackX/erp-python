import shutil
from pathlib import Path
from datetime import datetime
import zipfile

class BackupManager:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.data_dir = Path("dados")
        self.backup_dir.mkdir(exist_ok=True)

    def criar_backup(self, comentario: str = ""):
        """Cria um backup compactado de todos os dados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"backup_{timestamp}{f'_{comentario}' if comentario else ''}.zip"
        caminho_backup = self.backup_dir / nome_arquivo

        with zipfile.ZipFile(caminho_backup, 'w') as zipf:
            for arquivo in self.data_dir.glob('*.csv'):
                zipf.write(arquivo, arquivo.name)
        
        return caminho_backup

    def restaurar_backup(self, caminho_zip: str):
        """Restaura dados a partir de um backup"""
        with zipfile.ZipFile(caminho_zip, 'r') as zipf:
            zipf.extractall(self.data_dir)