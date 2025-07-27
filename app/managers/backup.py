import shutil
from pathlib import Path
from datetime import datetime
import zipfile
import locale

# Configura o locale para português (para nome do mês)
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
except:
    locale.setlocale(locale.LC_TIME, '')  # fallback para locale padrão do sistema

class BackupManager:
    def __init__(self, limite_backups: int = 10):
        self.backup_dir = Path("backups")
        self.data_dir = Path("app/dados")
        self.limite_backups = limite_backups
        self.backup_dir.mkdir(exist_ok=True)

    def criar_backup(self, comentario: str = ""):
        """Cria um backup compactado de todos os dados"""
        nome_data = datetime.now().strftime("%d-%B-%Y").lower()  # ex: 25-julho-2025
        nome_data = nome_data.replace("ç", "c").replace("ã", "a").replace("é", "e").replace(" ", "-")

        comentario_formatado = f"_{comentario}" if comentario else ""
        nome_arquivo = f"{nome_data}{comentario_formatado}.zip"
        caminho_backup = self.backup_dir / nome_arquivo

        with zipfile.ZipFile(caminho_backup, 'w') as zipf:
            for arquivo in self.data_dir.glob('*.csv'):
                zipf.write(arquivo, arquivo.name)

        self._limitar_backups()

        return caminho_backup

    def restaurar_backup(self, nome_arquivo: str):
        """Restaura dados a partir de um backup"""
        caminho_zip = self.backup_dir / nome_arquivo
        if not caminho_zip.exists():
            raise FileNotFoundError(f"Backup '{nome_arquivo}' não encontrado.")

        with zipfile.ZipFile(caminho_zip, 'r') as zipf:
            zipf.extractall(self.data_dir)

    def listar_backups(self) -> list[str]:
        """Retorna uma lista dos nomes de arquivos de backup existentes"""
        return sorted([f.name for f in self.backup_dir.glob("*.zip")], reverse=True)

    def excluir_backup(self, nome_arquivo: str):
        """Exclui um arquivo de backup"""
        caminho = self.backup_dir / nome_arquivo
        if caminho.exists():
            caminho.unlink()

    def _limitar_backups(self):
        """Mantém apenas os N backups mais recentes"""
        backups = sorted(self.backup_dir.glob("*.zip"), key=lambda f: f.stat().st_mtime, reverse=True)
        for velho in backups[self.limite_backups:]:
            velho.unlink()

    def data_hora_atual(self) -> str:
        """Retorna a data/hora atual formatada"""
        return datetime.now().strftime("%d-%B-%Y").lower()
