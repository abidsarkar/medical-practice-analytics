# src/etl/config.py
import os
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
SQL_DIR = PROJECT_ROOT / "sql"

# Database connection
DB_USER = os.getenv("DB_USER", "med_analyst")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_secure_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "medical_practice")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Table load order (respecting foreign key constraints)
TABLE_ORDER = [
    "insurance_companies",
    "patients",
    "providers",
    "patient_insurance",
    "appointments",
    "encounters",
    "diagnoses",
    "procedures",
    "claims",
    "claim_line_items",
    "payments"
]

# Expected schema for each table (for validation)
EXPECTED_COLUMNS = {
    "insurance_companies": ["insurance_company_id", "company_name", "payer_id", "billing_address", "email", "phone_number"],
    "patients": ["patient_id", "first_name", "last_name", "dob", "gender", "date_registered"],
    "providers": ["provider_id", "first_name", "last_name", "specialty", "npi"],
    "patient_insurance": ["patient_insurance_id", "patient_id", "insurance_company_id", "effective_date", "termination_date", "priority"],
    "appointments": ["appointment_id", "patient_id", "provider_id", "scheduled_time", "actual_start_time", "actual_end_time", "status"],
    "encounters": ["encounter_id", "appointment_id", "encounter_date", "chief_complaint"],
    "diagnoses": ["diagnosis_id", "encounter_id", "icd_code", "description", "diagnosis_rank"],
    "procedures": ["procedure_id", "encounter_id", "cpt_code", "description", "units", "charge_amount"],
    "claims": ["claim_id", "encounter_id", "total_charge", "claim_status", "filing_date", "adjudication_date"],
    "claim_line_items": ["line_id", "claim_id", "procedure_id", "charge_amount", "payment_amount", "adjustment_amount"],
    "payments": ["payment_id", "claim_id", "payment_date", "amount", "payment_type"]
}