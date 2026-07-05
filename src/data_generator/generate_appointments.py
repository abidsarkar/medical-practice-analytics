# generate_appointments.py
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
from config import save_and_load, DATA_DIR
from utils import calculate_age

fake = Faker()
np.random.seed(456)
random.seed(456)

def generate_appointments(n=50000, load_to_db=False):
    """Generate appointments referencing existing patients and providers."""
    print(f"\n{'='*60}")
    print(f"GENERATING {n} APPOINTMENTS")
    print(f"{'='*60}")
    
    # Load dependent data
    patients_df = pd.read_csv(DATA_DIR / "patients.csv")
    providers_df = pd.read_csv(DATA_DIR / "providers.csv")
    
    # Calculate patient ages
    patients_df['dob'] = pd.to_datetime(patients_df['dob'])
    patients_df['age'] = patients_df['dob'].apply(calculate_age)
    
    # Separate providers by specialty
    ped_providers = providers_df[providers_df['specialty'] == 'Pediatrics']['provider_id'].tolist()
    other_providers = providers_df[providers_df['specialty'] != 'Pediatrics']['provider_id'].tolist()
    
    pediatric_patients = patients_df[patients_df['age'] < 18]['patient_id'].tolist()
    adult_patients = patients_df[patients_df['age'] >= 18]['patient_id'].tolist()
    
    appointments = []
    start_date = datetime.now() - timedelta(days=730)
    
    for i in range(1, n + 1):
        # Assign patient to appropriate provider
        if random.random() < 0.15 and pediatric_patients:
            patient_id = random.choice(pediatric_patients)
            provider_id = random.choice(ped_providers) if ped_providers else random.choice(other_providers)
        elif adult_patients:
            patient_id = random.choice(adult_patients)
            provider_id = random.choice(other_providers)
        else:
            patient_id = random.choice(pediatric_patients)
            provider_id = random.choice(ped_providers)
        
        # Schedule during business hours
        scheduled_date = fake.date_time_between(start_date=start_date, end_date=datetime.now())
        scheduled_date = scheduled_date.replace(
            hour=random.randint(8, 16),
            minute=random.choice([0, 15, 30, 45]),
            second=0, microsecond=0
        )
        
        # Status distribution: 70% completed, 12% no-show, 8% cancelled, 10% checked-in
        status_roll = random.random()
        if status_roll < 0.08:
            status = "Cancelled"
            actual_start = None
            actual_end = None
        elif status_roll < 0.20:
            status = "No-Show"
            actual_start = None
            actual_end = None
        elif status_roll < 0.90:
            status = "Completed"
            wait = random.randint(5, 45)
            actual_start = scheduled_date + timedelta(minutes=wait)
            duration = random.randint(10, 60)
            actual_end = actual_start + timedelta(minutes=duration)
        else:
            status = "Checked-In"
            wait = random.randint(5, 45)
            actual_start = scheduled_date + timedelta(minutes=wait)
            actual_end = None
        
        appointments.append({
            "appointment_id": i,
            "patient_id": patient_id,
            "provider_id": provider_id,
            "scheduled_time": scheduled_date,
            "actual_start_time": actual_start,
            "actual_end_time": actual_end,
            "status": status
        })
        
        if i % 10000 == 0:
            print(f"  Generated {i} appointments...")
    
    df = pd.DataFrame(appointments)
    save_and_load(df, "appointments", load_to_db)
    print(f"  ✓ Complete: {len(df)} appointments generated")
    return df

if __name__ == "__main__":
    generate_appointments(50000, load_to_db=False)