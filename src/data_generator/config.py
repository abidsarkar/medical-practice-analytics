# config.py
import os
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database connection
DB_USER = os.getenv("DB_USER", "med_analyst")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_secure_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "medical_practice")
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Reference data
# Insurance companies (payers)

INSURANCE_COMPANIES = [
    {"company_name": "Blue Cross Blue Shield", "payer_id": "BCBS001", "billing_address": "123 Blue Cross Way, Chicago, IL", "email": "claims@bcbs.com", "phone_number": "800-123-4567"},
    {"company_name": "Aetna", "payer_id": "AETNA01", "billing_address": "456 Aetna Ave, Hartford, CT", "email": "provider@aetna.com", "phone_number": "800-234-5678"},
    {"company_name": "United Healthcare", "payer_id": "UHC0001", "billing_address": "789 United Blvd, Minnetonka, MN", "email": "claims@uhc.com", "phone_number": "800-345-6789"},
    {"company_name": "Cigna", "payer_id": "CIGNA01", "billing_address": "321 Cigna Dr, Bloomfield, CT", "email": "support@cigna.com", "phone_number": "800-456-7890"},
    {"company_name": "Humana", "payer_id": "HUMANA1", "billing_address": "654 Humana St, Louisville, KY", "email": "claims@humana.com", "phone_number": "800-567-8901"},
    {"company_name": "Medicare", "payer_id": "MCRPARTB", "billing_address": "7500 Security Blvd, Baltimore, MD", "email": "medicare@cms.gov", "phone_number": "800-633-4227"},
    {"company_name": "Medicaid", "payer_id": "MCDSTAT", "billing_address": "State Medicaid Office", "email": "medicaid@state.gov", "phone_number": "800-678-9012"},
    {"company_name": "Kaiser Permanente", "payer_id": "KP00001", "billing_address": "1 Kaiser Plaza, Oakland, CA", "email": "claims@kp.org", "phone_number": "800-789-0123"},
]
SPECIALTIES = [
    "Family Medicine", "Internal Medicine", "Cardiology", 
    "Orthopedics", "Pediatrics", "Dermatology", "Neurology",
    "Psychiatry", "OB/GYN", "Endocrinology"
]

CPT_CODES = [
    ("99213", "Office visit established patient level 3", 75.00, 25),
    ("99214", "Office visit established patient level 4", 110.00, 20),
    ("99203", "Office visit new patient level 3", 120.00, 10),
    ("99204", "Office visit new patient level 4", 170.00, 5),
    ("97110", "Therapeutic exercises", 55.00, 8),
    ("97140", "Manual therapy techniques", 65.00, 6),
    ("85025", "Complete blood count", 25.00, 15),
    ("71045", "Chest X-ray single view", 90.00, 5),
    ("93000", "Electrocardiogram complete", 85.00, 7),
    ("80053", "Comprehensive metabolic panel", 30.00, 10),
    ("81003", "Urinalysis automated with microscopy", 15.00, 8),
    ("90471", "Immunization administration", 40.00, 12),
    ("G0008", "Admin influenza virus vaccine", 35.00, 10),
]

ICD10_BY_SPECIALTY = {
    "Cardiology": [
        ("I10", "Essential hypertension", 30),
        ("I25.10", "Atherosclerotic heart disease", 20),
        ("I48.91", "Atrial fibrillation", 10),
        ("R07.9", "Chest pain unspecified", 15),
        ("I50.9", "Heart failure unspecified", 10),
        ("E78.5", "Hyperlipidemia", 15),
    ],
    "Pediatrics": [
        ("J06.9", "Acute upper respiratory infection", 25),
        ("Z00.129", "Well-child visit", 30),
        ("H66.9", "Otitis media", 15),
        ("J45.909", "Unspecified asthma", 10),
        ("R05", "Cough", 10),
        ("B34.9", "Viral infection", 10),
    ],
    "Orthopedics": [
        ("M54.5", "Low back pain", 25),
        ("M17.9", "Osteoarthritis of knee", 15),
        ("S93.4", "Ankle sprain", 10),
        ("M75.4", "Shoulder impingement", 8),
        ("M25.561", "Knee pain", 12),
        ("M54.2", "Cervicalgia", 10),
    ],
    "default": [
        ("I10", "Essential hypertension", 15),
        ("E11.9", "Type 2 diabetes mellitus", 12),
        ("J06.9", "Acute upper respiratory infection", 10),
        ("M54.5", "Low back pain", 10),
        ("Z00.00", "General adult medical exam", 15),
        ("E78.5", "Hyperlipidemia", 8),
        ("F41.9", "Anxiety disorder", 5),
        ("R10.9", "Abdominal pain", 5),
    ]
}

# Specialty-specific procedure weights
SPECIALTY_PROCEDURES = {
    "Cardiology": [("93000", 0.4), ("85025", 0.2), ("99214", 0.4)],
    "Orthopedics": [("97110", 0.3), ("97140", 0.2), ("71045", 0.3), ("99214", 0.2)],
    "Family Medicine": [("99213", 0.3), ("99214", 0.2), ("85025", 0.15), ("80053", 0.15), ("90471", 0.2)],
    "Internal Medicine": [("99214", 0.4), ("85025", 0.2), ("80053", 0.2), ("93000", 0.2)],
    "Pediatrics": [("99213", 0.3), ("90471", 0.3), ("85025", 0.2), ("81003", 0.2)],
    "default": [("99213", 0.4), ("99214", 0.3), ("85025", 0.15), ("80053", 0.15)]
}

def save_and_load(df, table_name, load_to_db=False):
    """Save DataFrame to CSV and optionally to PostgreSQL."""
    # Save CSV
    csv_path = DATA_DIR / f"{table_name}.csv"
    df.to_csv(csv_path, index=False)
    print(f"  ✓ Saved {csv_path} ({len(df):,} rows)")
    
    # Load to PostgreSQL
    if load_to_db:
        try:
            df.to_sql(table_name, engine, if_exists="replace", index=False, method="multi", chunksize=1000)
            print(f"  ✓ Loaded to PostgreSQL: {table_name}")
        except Exception as e:
            print(f"  ✗ Error loading to PostgreSQL: {e}")
    
    return df