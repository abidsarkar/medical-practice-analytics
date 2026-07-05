# src/etl/extract.py
import pandas as pd
from config import DATA_DIR, TABLE_ORDER, EXPECTED_COLUMNS
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_csv(table_name):
    """Extract data from CSV file."""
    file_path = DATA_DIR / f"{table_name}.csv"
    
    try:
        df = pd.read_csv(file_path)
        logger.info(f"✓ Extracted {table_name}: {len(df):,} rows from {file_path}")
        return df
    except FileNotFoundError:
        logger.error(f"✗ File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"✗ Error extracting {table_name}: {e}")
        raise

def extract_all_tables():
    """Extract all tables from CSV files."""
    logger.info("\n" + "="*60)
    logger.info("EXTRACT PHASE: Reading CSV files")
    logger.info("="*60)
    
    dataframes = {}
    for table in TABLE_ORDER:
        dataframes[table] = extract_csv(table)
    
    logger.info(f"✓ Extracted {len(dataframes)} tables successfully")
    return dataframes

if __name__ == "__main__":
    dfs = extract_all_tables()
    for name, df in dfs.items():
        print(f"{name}: {df.shape}")