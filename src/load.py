# Functions Load
import pandas as pd
from pathlib import Path


def load_csv(file_name: str, base_path: Path) -> pd.DataFrame:
    """
    Upload a CSV from the local path
    - Verifies file existence  
    - Handles read and parse errors
    - Reports upload summary
    """
    path = base_path / file_name
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    try:
        df = pd.read_csv(path, na_values=['', 'NULL', 'null', 'NaN', 'nan'], keep_default_na=False)
        print(f"[Load CSV] Cargado {file_name}: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df
    except Exception as e:
        raise RuntimeError(f"Error reading {file_name}: {e}")
