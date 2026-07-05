# src/etl/pipeline.py
import logging
import time
from datetime import datetime
from extract import extract_all_tables
from transform import transform_all_tables
from load import load_all_tables
from create_views import create_analytics_views, refresh_views

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_etl_pipeline(extract=True, transform=True, load=True, create_views=True):
    """Run the complete ETL pipeline."""
    
    start_time = time.time()
    logger.info("\n" + "="*70)
    logger.info(f"ETL PIPELINE STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*70)
    
    try:
        # 1. EXTRACT
        if extract:
            dataframes = extract_all_tables()
        else:
            logger.info("EXTRACT PHASE: SKIPPED")
            return
        
        # 2. TRANSFORM
        if transform:
            transformed_data = transform_all_tables(dataframes)
        else:
            logger.info("TRANSFORM PHASE: SKIPPED")
            transformed_data = dataframes
        
        # 3. LOAD
        if load:
            success = load_all_tables(transformed_data)
            if not success:
                logger.error("Load phase had errors. Check logs.")
                return
        else:
            logger.info("LOAD PHASE: SKIPPED")
        
        # 4. CREATE ANALYTICS VIEWS
        if create_views:
            create_analytics_views()
        else:
            logger.info("VIEW CREATION: SKIPPED")
        
        elapsed = time.time() - start_time
        logger.info("\n" + "="*70)
        logger.info(f"ETL PIPELINE COMPLETED SUCCESSFULLY in {elapsed:.1f} seconds")
        logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        # Print summary
        print_summary(transformed_data)
        
    except Exception as e:
        logger.error(f"\n✗ ETL PIPELINE FAILED: {e}")
        raise

def print_summary(dataframes):
    """Print a summary of loaded data."""
    logger.info("\n" + "="*60)
    logger.info("DATA SUMMARY")
    logger.info("="*60)
    
    total_rows = 0
    for table_name, df in dataframes.items():
        rows = len(df)
        total_rows += rows
        logger.info(f"  {table_name:<25} {rows:>10,} rows")
    
    logger.info(f"  {'─'*35}")
    logger.info(f"  {'TOTAL':<25} {total_rows:>10,} rows")

if __name__ == "__main__":
    # Run the full pipeline
    run_etl_pipeline(
        extract=True,
        transform=True,
        load=True,
        create_views=True
    )