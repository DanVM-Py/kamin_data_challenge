import pandas as pd
from pathlib import Path


def load_csv(file_name: str, base_path: str) -> pd.DataFrame:
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
        print(f"✅ Cargado {file_name}: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df
    except pd.errors.EmptyDataError:
        print(f"⚠️ The file {file_name} is empty.")
        return pd.DataFrame()
    except pd.errors.ParserError as e:
        print(f"❌ Error parsing {file_name}: {e}")
        raise
    except Exception as e:
        print(f"❌ Error reading {file_name}: {e}")
        raise


def standardize_dates(df, columns, df_name):
    """
    Purpose:
      -> Converts the date/time columns to UTC datetime, marking errors as NaT.
    Disclaimer: 
      -> Here we assume that all dates received are expressed in UTC format,
         since we are not clear on the input or the system that creates them. 
         In a productive environment, we would validate with the engineering
         team to understand in which time zone the dates are expressed.
    Exception:
      -> For the events dataset, we must make sure that the incompleteness of
         the completed_at date is related to the operation, that it is only empty
         as long as the status is between [processing, created].
    Next Features:
      -> In the future, in order to protect us from event completed_at data failures,
         we could create an average per event type to fill it when the status is different
         from [processing, created], so that for our analysis this issue would not affect
         our decision making. Of course, for reporting to the operations system,
         it would be key to tag those transactions that were complemented with averages
         to understand and improve the system.
    """
    for column in columns:
        # Parseo a datetime con UTC
        df[column] = pd.to_datetime(df[column], utc=True, errors='coerce')

        # Conteo total de valores no parseados
        total_null = df[column].isna().sum()

        # Caso especial: completed_at en el dataframe de events
        if df_name == "events" and column == "completed_at":
            # Estados donde esperamos fecha de completado
            mask_should_have = ~df['status'].isin(['processing', 'created'])
            null_should_have = df.loc[mask_should_have, column].isna().sum()
            print(
                f"[{df_name}] '{column}': {total_null} nulls "
                f"({null_should_have} en eventos con status ≠ processing/created)"
            )
        else:
            print(f"[{df_name}] '{column}': {total_null} valores no parseados")
    return df
