# Functions Transform
import re
import pandas as pd
import numpy as np
from pathlib import Path


def standardize_dates(df: pd.DataFrame, columns: list, df_name: str) -> pd.DataFrame:
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
         to understand and improve the system. Today it is not a priority as our 
         validation says we have 0 such cases.
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


def deduplicate_logic(
    df: pd.DataFrame,
    subset: list,
    sort_by: str,
    name: str
) -> pd.DataFrame:
    """
    Purpose:
      -> Remove duplicate rows based on the `subset` of key columns,
         keeping the earliest record as determined by `sort_by` ascending.

    Parameters:
      df      : Input DataFrame
      subset  : List of column names to define duplicate groups
      sort_by : Column name to sort by (earliest first)
      name    : Logical name for logging (e.g. 'events', 'retries', 'clients')

    Next Features:
      -> Implement a conflict-resolution mechanism to persist key duplicates
         once business rules are defined (e.g. prioritizing by status or other flags).
    """
    before = len(df)

    # Ensure sort_by column is datetime or comparable
    df_sorted = df.sort_values(by=sort_by, ascending=True)

    # Drop duplicates, keeping the first (earliest) occurrence per subset group
    df_clean = df_sorted.drop_duplicates(subset=subset, keep='first')

    after = len(df_clean)
    print(f"[Deduplicate] {name}: {before} → {after} rows (kept earliest by {sort_by})")

    return df_clean


def normalize_clients_metadata(df_clients: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
      -> Clean and standardize client metadata fields:
         1. 'sector': lowercase, strip, fill missing as 'unknown'
         2. 'contract_tier': map to one of basic/standard/premium/enterprise,
            fill others as 'unknown'
         3. 'client_name': remove punctuation (_ . , -), normalize spaces,
            apply Title Case
    Next Features:
      -> Enrich sector by web scraping company websites or using GenAI
         to interpret 'notes' and validate category.
    """
    df = df_clients.copy()
    total = len(df)
  
    # 1) Normalize 'sector' to allowed values
    allowed_sectors = {
        'credit':     'credit',
        'logistics':  'logistics',
        'payroll':    'payroll',
        'retail':     'retail',
        'services':   'services'
    }
    df['sector'] = (
        df['sector']
        .astype(str)
        .str.lower()
        .str.strip()
        .map(allowed_sectors)
        .fillna('unknown')
    )
    unknown_sector = (df['sector'] == 'unknown').sum()
    print(f"[Metadata] clients: {unknown_sector}/{total} sectors set to 'unknown'")

    # 2) Normalize 'contract_tier'
    valid_tiers = {
        'basic':      'basic',
        'standard':   'standard',
        'premium':    'premium',
        'enterprise': 'enterprise'
    }
    df['contract_tier'] = (
        df['contract_tier']
        .astype(str)
        .str.lower()
        .str.strip()
        .map(valid_tiers)
        .fillna('unknown')
    )
    unknown_tier   = (df['contract_tier'] == 'unknown').sum()
    print(f"[Metadata] clients: {unknown_tier}/{total} tiers set to 'unknown'")

    # 3) Normalize 'client_name'
    def clean_name(name: str) -> str:
        # Replace . , _ - with space
        s = re.sub(r"[._,-]+", " ", str(name))
        # Collapse multiple spaces
        s = re.sub(r"\s+", " ", s).strip()
        # Title case
        return s.title()

    df['client_name'] = df['client_name'].apply(clean_name)

    return df


def normalize_events_metadata(df_events: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
      -> Clean and standardize events metadata fields:
         1. Drop rows missing critical keys (event_id, client_id, created_at)
         2. 'client_id': cast to string and strip whitespace
         3. 'type': normalize to {'pay_in','pay_out'}, flag others as 'unknown'
         4. 'currency':
            -> Cast to uppercase & strip
            -> Enforce 3-letter codes (invalid or missing → 'XXX') by ISO 4217
         5. 'status': normalize to allowed set {'created','processing','completed','failed'}, flag unknowns
         6. 'error_code':
            -> Cast to uppercase & strip
            -> If status != 'failed' and empty/nan, fill with 'NONE'
            -> If status == 'failed'  and empty/nan, fill with 'UNKNOWN'
         7. 'origin_country' & 'destination_country':
            -> Cast to uppercase & strip
            -> Enforce 2-letter codes (invalid or missing → 'XX') by ISO 3166-1 alpha-2
    Next Features:
      -> Integrate GeoIP lookup for missing country codes
      -> Use GenAI to interpret rare error_codes
    """
    df = df_events.copy()
    total = len(df)

    # 1) Drop rows missing critical keys
    df = df.dropna(subset=['event_id', 'client_id', 'created_at'])
    print(f"[Metadata] events: {total} → {len(df)} after dropping missing keys")

    # 2) Normalize client_id
    df['client_id'] = df['client_id'].astype(str).str.strip()

    # 3) Normalize type
    df['type'] = (
        df['type']
        .astype(str)
        .str.lower()
        .str.strip()
        .where(lambda s: s.isin(['pay_in','pay_out']), other='unknown')
    )
    mask_type = df['type'] == 'unknown'
    n_bad_types = mask_type.sum()
    print(f"[Metadata] events: {n_bad_types}/{total} invalid type set to 'unknown'")


    # 4) Currency enforcement
    df['currency'] = df['currency'].astype(str).str.upper().str.strip()
    mask_currency = df['currency'].str.len() != 3
    n_bad_currency = mask_currency.sum()
    df.loc[mask_currency, 'currency'] = 'XXX'
    print(f"[Metadata] events: {n_bad_currency}/{total} invalid currency codes set to 'XXX'")

    # 5) Normalize status
    allowed_status = {'created','processing','completed','failed'}
    df['status'] = (
        df['status']
        .astype(str)
        .str.lower()
        .str.strip()
        .where(lambda s: s.isin(allowed_status), other='unknown')
    )
    mask_status = df['status'] == 'unknown'
    n_bad_status = mask_status.sum()
    print(f"[Metadata] events: {n_bad_status}/{total} invalid status code set to 'unknown'")


    # 6) Clean error_code
    df['error_code'] = df['error_code'].astype(str).str.upper().str.strip()
    mask_failed = df['status'] == 'failed'
    df.loc[~mask_failed & df['error_code'].isin(['','NONE','NAN']), 'error_code'] = 'NONE'
    df.loc[ mask_failed & df['error_code'].isin(['','NONE','NAN']), 'error_code'] = 'UNKNOWN'
    mask_error_code = df['status'] == 'unknown'
    n_bad_error_code = mask_error_code.sum()
    print(f"[Metadata] events: {n_bad_error_code}/{total} invalid error code set to 'unknown'")

    # 7) Country code enforcement
    for col in ['origin_country','destination_country']:
        df[col] = df[col].astype(str).str.upper().str.strip()
        mask_country = df[col].str.len() != 2
        n_bad_country = mask_country.sum()
        df.loc[mask_country, col] = 'XX'
        print(f"[Metadata] events: {n_bad_country}/{total} invalid {col} codes set to 'XX'")

    return df


def normalize_retry_logs_metadata(df_retry_logs: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
      -> Clean and standardize retry logs metadata fields:
         1. Drop rows missing critical keys (retry_id, original_event_id, retry_time)
         2. 'retry_id' & 'original_event_id': validate UUID format
         3. 'retry_attempt': validate integer in range 1-3
         4. 'retry_status': normalize to {'success','failed'}, flag others as 'unknown'
         5. 'retry_time': ensure proper datetime format
    Next Features:
      -> Validate retry_attempt sequences (should be consecutive 1,2,3 for same event)
      -> Cross-reference original_event_id with events table for consistency
    """
    import uuid
    
    df = df_retry_logs.copy()
    total = len(df)

    # 1) Drop rows missing critical keys
    df = df.dropna(subset=['retry_id', 'original_event_id', 'retry_time'])
    print(f"[Metadata] retry_logs: {total} → {len(df)} after dropping missing keys")

    # 2) Validate UUID format for retry_id and original_event_id
    def is_valid_uuid(value):
        try:
            uuid.UUID(str(value))
            return True
        except (ValueError, TypeError):
            return False

    # Check retry_id
    invalid_retry_id = ~df['retry_id'].apply(is_valid_uuid)
    n_invalid_retry_id = invalid_retry_id.sum()
    if n_invalid_retry_id > 0:
        print(f"[Metadata] retry_logs: {n_invalid_retry_id}/{len(df)} invalid retry_id format")
        # Drop rows with invalid UUIDs
        df = df[~invalid_retry_id]

    # Check original_event_id
    invalid_event_id = ~df['original_event_id'].apply(is_valid_uuid)
    n_invalid_event_id = invalid_event_id.sum()
    if n_invalid_event_id > 0:
        print(f"[Metadata] retry_logs: {n_invalid_event_id}/{len(df)} invalid original_event_id format")
        # Drop rows with invalid UUIDs
        df = df[~invalid_event_id]

    # 3) Validate retry_attempt range (1-3)
    df['retry_attempt'] = pd.to_numeric(df['retry_attempt'], errors='coerce')
    invalid_attempt = ~df['retry_attempt'].isin([1, 2, 3])
    n_invalid_attempt = invalid_attempt.sum()
    if n_invalid_attempt > 0:
        print(f"[Metadata] retry_logs: {n_invalid_attempt}/{len(df)} invalid retry_attempt (not 1-3)")
        # Drop rows with invalid attempts
        df = df[~invalid_attempt]

    # 4) Normalize retry_status
    df['retry_status'] = (
        df['retry_status']
        .astype(str)
        .str.lower()
        .str.strip()
        .where(lambda s: s.isin(['success', 'failed']), other='unknown')
    )
    mask_status = df['retry_status'] == 'unknown'
    n_bad_status = mask_status.sum()
    print(f"[Metadata] retry_logs: {n_bad_status}/{len(df)} invalid status set to 'unknown'")

    # 5) Ensure retry_time is string format for consistency
    df['retry_time'] = df['retry_time'].astype(str).str.strip()

    return df
