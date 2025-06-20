from pathlib import Path

BASE_PATH = Path('data')
RAW_PATH = BASE_PATH / 'raw'
PROCESSED_PATH  = BASE_PATH / 'processed'
CSV_FILES = {
    "clients":   RAW_PATH / 'clients.csv',
    "events":    RAW_PATH / 'events.csv',
    "retries":   RAW_PATH / 'retry_logs.csv'
}
TZ_ORIGIN = 'America/Bogota'
