import csv
import os
from pathlib import Path
from typing import List, Dict, Optional

class CSVManager:
    def __init__(self, filename: str):
        self.data_dir = Path(__file__).parent.parent / "dados"
        self.filepath = self.data_dir / filename
        self._cache: Optional[List[Dict]] = None
        self._index_por_id: Optional[Dict[str, Dict]] = None
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        self.data_dir.mkdir(exist_ok=True)
        if not self.filepath.exists():
            with open(self.filepath, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.get_headers())
                writer.writeheader()

    def get_headers(self) -> List[str]:
        raise NotImplementedError("Método get_headers() deve ser implementado")

    def _carregar_cache(self):
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = []
                for row in reader:
                    clean_row = {}
                    for k, v in row.items():
                        if k is None:
                            continue
                        key = k.strip().replace('\ufeff', '')
                        clean_row[key] = v.strip() if isinstance(v, str) else v
                    records.append(clean_row)

                self._cache = [row for row in records if row]
                self._index_por_id = {r['id']: r for r in self._cache if 'id' in r}
        except FileNotFoundError:
            self._ensure_file_exists()
            self._cache = []
            self._index_por_id = {}
        except Exception as e:
            print(f"Erro ao ler {getattr(self, 'filepath', 'arquivo desconhecido')}: {str(e)}")
            self._cache = []
            self._index_por_id = {}

    def get_all(self) -> List[Dict]:
        if self._cache is None:
            self._carregar_cache()
        return self._cache or []

    def find_by_id(self, id_value: str) -> Optional[Dict]:
        if self._cache is None or self._index_por_id is None:
            self._carregar_cache()
        return self._index_por_id.get(id_value) if self._index_por_id else None

    def save(self, data: Dict) -> None:
        with open(self.filepath, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_headers())
            file_is_empty = os.stat(self.filepath).st_size == 0
            if file_is_empty:
                writer.writeheader()
            writer.writerow(data)
        self._cache = None  # Limpa cache após alteração
        self._index_por_id = None

    def update(self, id_value: str, new_data: Dict) -> bool:
        records = self.get_all()
        updated = False
        valid_new_data = {k: v for k, v in new_data.items() if k in self.get_headers()}

        with open(self.filepath, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_headers())
            writer.writeheader()
            for record in records:
                if record['id'] == id_value:
                    record.update(valid_new_data)
                    updated = True
                safe_record = {field: record.get(field, '') for field in self.get_headers()}
                writer.writerow(safe_record)

        self._cache = None  # Limpa cache após alteração
        self._index_por_id = None
        return updated
