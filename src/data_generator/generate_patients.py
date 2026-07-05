# generate_patients.py
import pandas as pd
import numpy as np
from faker import Faker
import random
from config import save_and_load

fake = Faker()
np.random.seed(42)
random.seed(42)

def generate_patients(n=10000, load_to_db=False):
    print(f"\n{'='*60}")
    print(f"GENERATING {n} PATIENTS")
    print(f"{'='*60}")

    patients = []
    for patient_id in range(1, n + 1):
        age_group = np.random.choice(
            [0, 1, 2, 3, 4],
            p=[0.05, 0.10, 0.25, 0.35, 0.25]
        )
        age_ranges = {0: (1, 17), 1: (18, 30), 2: (31, 50), 3: (51, 70), 4: (71, 90)}
        min_age, max_age = age_ranges[age_group]
        dob = fake.date_of_birth(minimum_age=min_age, maximum_age=max_age)

        patients.append({
            "patient_id": patient_id,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "dob": dob,
            "gender": np.random.choice(["Male", "Female"], p=[0.48, 0.52]),
            "date_registered": fake.date_between(start_date="-5y", end_date="today")
        })

        if patient_id % 2000 == 0:
            print(f"  Generated {patient_id} patients...")

    df = pd.DataFrame(patients)
    save_and_load(df, "patients", load_to_db)
    print(f"  ✓ Complete: {len(df)} patients generated")
    return df

if __name__ == "__main__":
    generate_patients(10000, load_to_db=False)