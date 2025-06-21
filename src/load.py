# Functions Load
import pandas as pd
from pathlib import Path


def load_csv(file_name: str, base_path: Path) -> pd.DataFrame:
    """
    Upload a CSV from the Google Drive path
    - Verifies file existence
    - Handles read and parse errors
    - Reports upload summary
    """
    path = base_path / file_name
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    try:
        df = pd.read_csv(path)
        print(f"[Load CSV] Cargado {file_name}: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df
    except pd.errors.EmptyDataError:
        print(f"⚠️ [Load CSV] The file {file_name} is empty.")
        return pd.DataFrame()
    except pd.errors.ParserError as e:
        print(f"❌ [Load CSV] Error parsing {file_name}: {e}")
        raise
    except Exception as e:
        print(f"❌ [Load CSV] Error reading {file_name}: {e}")
        raise
