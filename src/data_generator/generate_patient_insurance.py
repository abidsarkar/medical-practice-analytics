# generate_patient_insurance.py
import pandas as pd
import numpy as np
import random
from config import save_and_load, DATA_DIR

np.random.seed(111)
random.seed(111)

def generate_patient_insurance(load_to_db=False):
    print(f"\n{'='*60}")
    print("GENERATING PATIENT INSURANCE")
    print(f"{'='*60}")

    # Load patients and insurance companies
    patients_df = pd.read_csv(DATA_DIR / "patients.csv")
    insurance_df = pd.read_csv(DATA_DIR / "insurance_companies.csv")

    # For each patient, assign exactly one active insurance (priority=1, no end date)
    patient_insurance = []
    for pid in patients_df['patient_id']:
        # Choose a random insurance company
        ins_id = random.choice(insurance_df['insurance_company_id'])
        # effective_date: some date between date_registered and today
        reg_date = patients_df[patients_df['patient_id'] == pid]['date_registered'].values[0]
        # If reg_date is string, convert; assume date format
        from datetime import datetime, timedelta
        reg_date = pd.to_datetime(reg_date).date()
        eff_date = reg_date + timedelta(days=random.randint(0, 30))

        patient_insurance.append({
            "patient_insurance_id": pid,  # One-to-one: use patient_id as primary key
            "patient_id": pid,
            "insurance_company_id": ins_id,
            "effective_date": eff_date,
            "termination_date": None,
            "priority": random.randint(1, 5)
        })

    df = pd.DataFrame(patient_insurance)
    save_and_load(df, "patient_insurance", load_to_db)
    print(f"  ✓ Complete: {len(df)} patient insurance records generated")
    return df

if __name__ == "__main__":
    generate_patient_insurance(load_to_db=False)