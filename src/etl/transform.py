# src/etl/transform.py
import pandas as pd
import numpy as np
from datetime import datetime
from config import EXPECTED_COLUMNS
import logging

logger = logging.getLogger(__name__)

def validate_columns(df, table_name):
    """Check that DataFrame has expected columns."""
    expected = EXPECTED_COLUMNS.get(table_name, [])
    actual = df.columns.tolist()
    
    missing = set(expected) - set(actual)
    extra = set(actual) - set(expected)
    
    if missing:
        logger.warning(f"⚠ {table_name}: Missing columns: {missing}")
    if extra:
        logger.warning(f"⚠ {table_name}: Extra columns: {extra}")
    
    return len(missing) == 0

def convert_dates(df, table_name):
    """Convert date columns to proper datetime format."""
    date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    
    for col in date_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                logger.debug(f"  Converted {table_name}.{col} to datetime")
            except Exception as e:
                logger.warning(f"  Could not convert {table_name}.{col}: {e}")
    
    return df

def clean_strings(df, table_name):
    """Clean string columns - strip whitespace, handle nulls."""
    string_columns = df.select_dtypes(include=['object']).columns
    
    for col in string_columns:
        # Strip whitespace
        df[col] = df[col].astype(str).str.strip()
        # Replace 'nan', 'None', '' with actual NaN
        df[col] = df[col].replace(['nan', 'None', ''], np.nan)
    
    return df

def validate_business_rules(dfs):
    """Apply and validate business rules across tables."""
    logger.info("\n--- Business Rule Validation ---")
    issues = []
    
    # Rule 1: Cancelled appointments should have no encounters
    if 'appointments' in dfs and 'encounters' in dfs:
        cancelled = dfs['appointments'][dfs['appointments']['status'] == 'Cancelled']
        cancelled_ids = set(cancelled['appointment_id'])
        encounter_appt_ids = set(dfs['encounters']['appointment_id'])
        violations = cancelled_ids & encounter_appt_ids
        
        if violations:
            issues.append(f"⚠ {len(violations)} cancelled appointments have encounters")
        else:
            logger.info("✓ Rule 1: No cancelled appointments have encounters")
    
    # Rule 2: Denied claims should have $0 payment in line items
    if 'claims' in dfs and 'claim_line_items' in dfs:
        denied_claims = dfs['claims'][dfs['claims']['claim_status'] == 'Denied']['claim_id']
        denied_lines = dfs['claim_line_items'][dfs['claim_line_items']['claim_id'].isin(denied_claims)]
        denied_with_payment = denied_lines[denied_lines['payment_amount'] > 0]
        
        if len(denied_with_payment) > 0:
            issues.append(f"⚠ {len(denied_with_payment)} denied claim lines have payments > $0")
        else:
            logger.info("✓ Rule 2: Denied claims have $0 payment")
    
    # Rule 3: Charge reconciliation
    if 'claims' in dfs and 'claim_line_items' in dfs:
        claims_total = dfs['claims']['total_charge'].sum()
        lines_total = dfs['claim_line_items']['charge_amount'].sum()
        diff = abs(claims_total - lines_total)
        
        if diff > 1.00:
            issues.append(f"⚠ Charge mismatch: Claims=${claims_total:,.2f} vs Lines=${lines_total:,.2f}")
        else:
            logger.info(f"✓ Rule 3: Charges reconciled (diff: ${diff:.2f})")
    
    # Rule 4: Every patient has insurance
    if 'patients' in dfs and 'patient_insurance' in dfs:
        patient_ids = set(dfs['patients']['patient_id'])
        insured_ids = set(dfs['patient_insurance']['patient_id'])
        uninsured = patient_ids - insured_ids
        
        if uninsured:
            issues.append(f"⚠ {len(uninsured)} patients have no insurance")
        else:
            logger.info("✓ Rule 4: All patients have insurance coverage")
    
    # Rule 5: Completed appointments have encounters
    if 'appointments' in dfs and 'encounters' in dfs:
        completed = dfs['appointments'][dfs['appointments']['status'] == 'Completed']
        completed_ids = set(completed['appointment_id'])
        encounter_appt_ids = set(dfs['encounters']['appointment_id'])
        missing_encounters = completed_ids - encounter_appt_ids
        
        if missing_encounters:
            issues.append(f"⚠ {len(missing_encounters)} completed appointments missing encounters")
        else:
            logger.info("✓ Rule 5: All completed appointments have encounters")
    
    return issues

def transform_table(df, table_name):
    """Apply all transformations to a single table."""
    logger.info(f"  Transforming {table_name}...")
    
    # Validate columns
    validate_columns(df, table_name)
    
    # Convert dates
    df = convert_dates(df, table_name)
    
    # Clean strings
    df = clean_strings(df, table_name)
    
    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    if before != after:
        logger.warning(f"  Removed {before - after} duplicate rows from {table_name}")
    
    # Remove rows with null primary key
    pk_col = df.columns[0]  # Assume first column is PK
    df = df.dropna(subset=[pk_col])
    
    return df

def transform_all_tables(dataframes):
    """Transform all extracted dataframes."""
    logger.info("\n" + "="*60)
    logger.info("TRANSFORM PHASE: Cleaning and validating data")
    logger.info("="*60)
    
    transformed = {}
    for table_name, df in dataframes.items():
        transformed[table_name] = transform_table(df, table_name)
    
    # Validate business rules across tables
    issues = validate_business_rules(transformed)
    
    if issues:
        logger.warning("\n⚠ Business rule violations found:")
        for issue in issues:
            logger.warning(f"  {issue}")
    else:
        logger.info("\n✓ All business rules passed!")
    
    return transformed

if __name__ == "__main__":
    from extract import extract_all_tables
    dfs = extract_all_tables()
    transformed = transform_all_tables(dfs)