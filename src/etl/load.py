# src/etl/load.py
import pandas as pd
from sqlalchemy import text
from config import engine, TABLE_ORDER
import logging

logger = logging.getLogger(__name__)

def create_schema():
    """Create database schema from SQL file."""
    logger.info("Creating database schema...")
    
    schema_file = "../../sql/schema/001_create_tables.sql"
    
    try:
        with open(schema_file, 'r') as f:
            sql = f.read()
        
        # Split by semicolon and execute each statement
        with engine.connect() as conn:
            for statement in sql.split(';'):
                statement = statement.strip()
                if statement:
                    conn.execute(text(statement))
            conn.commit()
        
        logger.info("✓ Schema created successfully")
    except Exception as e:
        logger.error(f"✗ Error creating schema: {e}")
        raise

def truncate_tables():
    """Truncate all tables before loading (in reverse order for FK constraints)."""
    logger.info("Truncating existing data...")
    
    reverse_order = list(reversed(TABLE_ORDER))
    
    with engine.connect() as conn:
        for table in reverse_order:
            try:
                conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                logger.info(f"  Truncated {table}")
            except Exception as e:
                logger.warning(f"  Could not truncate {table}: {e}")
        conn.commit()
    
    logger.info("✓ Tables truncated")

def load_table(df, table_name):
    """Load a single DataFrame to PostgreSQL."""
    try:
        df.to_sql(
            table_name,
            engine,
            if_exists='append',  # Append after truncate
            index=False,
            method='multi',
            chunksize=1000
        )
        
        # Verify row count
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            db_count = result.scalar()
        
        logger.info(f"✓ Loaded {table_name}: {len(df):,} rows (DB: {db_count:,} rows)")
        return True
    except Exception as e:
        logger.error(f"✗ Error loading {table_name}: {e}")
        return False

def create_indexes():
    """Create indexes for better query performance."""
    logger.info("Creating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id)",
        "CREATE INDEX IF NOT EXISTS idx_appointments_provider ON appointments(provider_id)",
        "CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status)",
        "CREATE INDEX IF NOT EXISTS idx_appointments_scheduled ON appointments(scheduled_time)",
        "CREATE INDEX IF NOT EXISTS idx_encounters_appointment ON encounters(appointment_id)",
        "CREATE INDEX IF NOT EXISTS idx_encounters_date ON encounters(encounter_date)",
        "CREATE INDEX IF NOT EXISTS idx_diagnoses_encounter ON diagnoses(encounter_id)",
        "CREATE INDEX IF NOT EXISTS idx_diagnoses_code ON diagnoses(icd_code)",
        "CREATE INDEX IF NOT EXISTS idx_procedures_encounter ON procedures(encounter_id)",
        "CREATE INDEX IF NOT EXISTS idx_procedures_code ON procedures(cpt_code)",
        "CREATE INDEX IF NOT EXISTS idx_claims_encounter ON claims(encounter_id)",
        "CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(claim_status)",
        "CREATE INDEX IF NOT EXISTS idx_claims_filing_date ON claims(filing_date)",
        "CREATE INDEX IF NOT EXISTS idx_line_items_claim ON claim_line_items(claim_id)",
        "CREATE INDEX IF NOT EXISTS idx_payments_claim ON payments(claim_id)",
        "CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date)",
        "CREATE INDEX IF NOT EXISTS idx_patient_insurance_patient ON patient_insurance(patient_id)",
        "CREATE INDEX IF NOT EXISTS idx_patient_insurance_company ON patient_insurance(insurance_company_id)",
    ]
    
    with engine.connect() as conn:
        for idx_sql in indexes:
            try:
                conn.execute(text(idx_sql))
            except Exception as e:
                logger.warning(f"  Could not create index: {e}")
        conn.commit()
    
    logger.info("✓ Indexes created")

def load_all_tables(dataframes):
    """Load all transformed DataFrames to PostgreSQL."""
    logger.info("\n" + "="*60)
    logger.info("LOAD PHASE: Inserting data into PostgreSQL")
    logger.info("="*60)
    
    # Create schema first
    create_schema()
    
    # Clear existing data
    truncate_tables()
    
    # Load tables in order
    success_count = 0
    for table_name in TABLE_ORDER:
        if table_name in dataframes:
            if load_table(dataframes[table_name], table_name):
                success_count += 1
    
    # Create indexes
    create_indexes()
    
    logger.info(f"\n✓ Loaded {success_count}/{len(TABLE_ORDER)} tables successfully")
    
    return success_count == len(TABLE_ORDER)

if __name__ == "__main__":
    from extract import extract_all_tables
    from transform import transform_all_tables
    
    dfs = extract_all_tables()
    transformed = transform_all_tables(dfs)
    load_all_tables(transformed)