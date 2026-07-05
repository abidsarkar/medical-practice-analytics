# generate_all.py
import time
from generate_insurance_companies import generate_insurance_companies
from generate_patients import generate_patients
from generate_providers import generate_providers
from generate_patient_insurance import generate_patient_insurance
from generate_appointments import generate_appointments
from generate_encounters import generate_encounters
from generate_diagnoses import generate_diagnoses
from generate_procedures import generate_procedures
from generate_claims import generate_claims
from generate_payments import generate_payments

def main(load_to_db=True):
    start = time.time()
    print("\n" + "="*60)
    print("MEDICAL PRACTICE SYNTHETIC DATA GENERATOR (UPDATED SCHEMA)")
    print("="*60)

    # 1. Reference tables (no dependencies)
    insurance = generate_insurance_companies(load_to_db)
    providers = generate_providers(50, load_to_db)

    # 2. Core entities (patients now without insurance columns)
    patients = generate_patients(10000, load_to_db)

    # 3. Patient-Insurance linking (after patients and insurance exist)
    patient_ins = generate_patient_insurance(load_to_db)

    # 4. Workflow data (depends on patients, providers)
    appointments = generate_appointments(50000, load_to_db)

    # 5. Clinical data (depends on appointments)
    encounters = generate_encounters(load_to_db)
    diagnoses = generate_diagnoses(load_to_db)    # unchanged – uses patient age via patients.csv (still fine)
    procedures = generate_procedures(load_to_db)  # unchanged

    # 6. Financial data (depends on encounters, procedures)
    claims, line_items = generate_claims(load_to_db)
    payments = generate_payments(load_to_db)      # unchanged

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"ALL DONE! Total time: {elapsed:.1f} seconds")
    print(f"{'='*60}")

if __name__ == "__main__":
    main(load_to_db=False)  # Set True to also load to PostgreSQL