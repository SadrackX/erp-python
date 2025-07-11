import csv
import os
from pathlib import Path
from typing import List, Dict, Optional

class CSVManager:
    def __init__(self, filename: str):
        self.data_dir = Path(__file__).parent.parent / "dados"
        self.filepath = self.data_dir / filename
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Cria o arquivo CSV com cabeçalhos se não existir"""
        self.data_dir.mkdir(exist_ok=True)
        if not self.filepath.exists():
            with open(self.filepath, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.get_headers())
                writer.writeheader()
    
    def get_headers(self) -> List[str]:
        """Retorna os cabeçalhos do CSV (deve ser implementado pelas subclasses)"""
        raise NotImplementedError("Método get_headers() deve ser implementado")
    
    def save(self, data: Dict) -> None:
        """Salva um novo registro em uma nova linha"""
        with open(self.filepath, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_headers())
            
            # Verifica se o arquivo está vazio (incluindo cabeçalhos)
            file_is_empty = os.stat(self.filepath).st_size == 0
            
            if file_is_empty:
                writer.writeheader()  # Escreve cabeçalhos se arquivo novo
            
            writer.writerow(data)  # Escreve os dados em nova linha
    
    def get_all(self) -> List[Dict]:
        """Retorna todos os registros válidos"""
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = list(reader)
                print(f"Registros lidos de {self.filepath}: {records}")  # Log de depuração
                return [row for row in records if row] # Filtra registros com ID válido
        except FileNotFoundError:
            print(f"Arquivo {self.filepath} não encontrado, criando novo...")
            self._ensure_file_exists()
            return []
        except Exception as e:
            print(f"Erro ao ler {self.filename}: {str(e)}")
            return []
        
    def find_by_id(self, id_value: str) -> Optional[Dict]:
        """Busca um registro por ID"""
        for record in self.get_all():
            if record['id'] == id_value:
                return record
        return None
    
    def update(self, id_value: str, new_data: Dict) -> bool:
        """Atualiza um registro existente"""
        records = self.get_all()
        updated = False
        
        with open(self.filepath, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_headers())
            writer.writeheader()
            
            for record in records:
                if record['id'] == id_value:
                    record.update(new_data)
                    updated = True
                writer.writerow(record)
        
        return updated