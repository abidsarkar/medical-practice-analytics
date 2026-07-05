# generate_encounters.py
import pandas as pd
import numpy as np
import random
from config import save_and_load, DATA_DIR

np.random.seed(789)
random.seed(789)

def generate_encounters(load_to_db=False):
    print(f"\n{'='*60}")
    print("GENERATING ENCOUNTERS")
    print(f"{'='*60}")

    appointments_df = pd.read_csv(DATA_DIR / "appointments.csv")
    providers_df = pd.read_csv(DATA_DIR / "providers.csv")

    # Only completed appointments become encounters
    completed = appointments_df[appointments_df['status'] == 'Completed'].copy()
    print(f"  Found {len(completed)} completed appointments")

    # Chief complaints by specialty (need provider specialty via appointment)
    provider_specialty = dict(zip(providers_df['provider_id'], providers_df['specialty']))
    complaints = {
        "Cardiology": ["Chest pain", "Palpitations", "Shortness of breath", "Hypertension follow-up"],
        "Pediatrics": ["Fever", "Cough", "Ear pain", "Well-child check", "Rash"],
        "Orthopedics": ["Back pain", "Knee pain", "Shoulder pain", "Ankle injury"],
        "Family Medicine": ["Annual physical", "Cold symptoms", "Headache", "Fatigue"],
        "Internal Medicine": ["Diabetes follow-up", "Hypertension", "Preventive visit"],
        "default": ["Routine follow-up", "New symptoms", "Medication refill"]
    }

    encounters = []
    for idx, (_, appt) in enumerate(completed.iterrows(), 1):
        specialty = provider_specialty.get(appt['provider_id'], 'default')
        complaint_list = complaints.get(specialty, complaints['default'])

        enc_date = pd.to_datetime(appt['actual_start_time']).date() if pd.notna(appt['actual_start_time']) else pd.to_datetime(appt['scheduled_time']).date()

        encounters.append({
            "encounter_id": idx,
            "appointment_id": appt['appointment_id'],
            "encounter_date": enc_date,
            "chief_complaint": random.choice(complaint_list)
        })

        if idx % 5000 == 0:
            print(f"  Generated {idx} encounters...")

    df = pd.DataFrame(encounters)
    save_and_load(df, "encounters", load_to_db)
    print(f"  ✓ Complete: {len(df)} encounters generated")
    return df

if __name__ == "__main__":
    generate_encounters(load_to_db=False)