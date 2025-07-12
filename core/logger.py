import logging
from pathlib import Path
from datetime import datetime
import sys

class _LoggerConfig:
    def __init__(self):
        self.logger = logging.getLogger("erp_logger")
        self.logger.setLevel(logging.INFO)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura handlers de arquivo e console"""
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S'
        )
        
        # Handler de arquivo (rotação diária)
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(
            logs_dir / f"erp_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # Handler de console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Remove handlers existentes
        self.logger.handlers.clear()
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

# Instância singleton
_logger = _LoggerConfig().logger

def log(mensagem: str, nivel: str = "info"):
    """
    Registra mensagem no log com os níveis:
    debug, info, warning, error, critical
    """
    nivel = nivel.lower()
    try:
        getattr(_logger, nivel)(mensagem)
    except AttributeError:
        _logger.info(mensagem)  # Fallback para info