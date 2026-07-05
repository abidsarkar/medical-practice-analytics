# generate_diagnoses.py
import pandas as pd
import numpy as np
from config import save_and_load, DATA_DIR, ICD10_BY_SPECIALTY
from utils import calculate_age
import random

np.random.seed(101)
random.seed(101)


def generate_diagnoses(load_to_db=False):
    """Generate diagnoses based on encounter specialty and patient age."""
    print(f"\n{'='*60}")
    print(f"GENERATING DIAGNOSES")
    print(f"{'='*60}")
    
    # Load dependent data
    encounters_df = pd.read_csv(DATA_DIR / "encounters.csv")
    appointments_df = pd.read_csv(DATA_DIR / "appointments.csv")
    providers_df = pd.read_csv(DATA_DIR / "providers.csv")
    patients_df = pd.read_csv(DATA_DIR / "patients.csv")
    
    # Create lookups from appointments (now the bridge table)
    # appointments has: appointment_id, patient_id, provider_id
    appt_lookup = appointments_df.set_index('appointment_id')
    
    # Create provider specialty lookup
    provider_specialty = dict(zip(providers_df['provider_id'], providers_df['specialty']))
    
    # Create patient age lookup
    patients_df['dob'] = pd.to_datetime(patients_df['dob'])
    patient_ages = dict(zip(patients_df['patient_id'], patients_df['dob'].apply(calculate_age)))
    
    diagnoses = []
    diagnosis_id = 1
    
    for _, enc in encounters_df.iterrows():
        # Get appointment details to find provider_id and patient_id
        appt_id = enc['appointment_id']
        appt_info = appt_lookup.loc[appt_id]
        
        provider_id = appt_info['provider_id']
        patient_id = appt_info['patient_id']
        
        # Get specialty and age
        specialty = provider_specialty.get(provider_id, 'default')
        age = patient_ages.get(patient_id, 45)
        
        # Get ICD codes for this specialty
        codes = ICD10_BY_SPECIALTY.get(specialty, ICD10_BY_SPECIALTY['default'])
        
        # Apply age-based logic: older patients more likely chronic conditions
        if age > 60:
            # Boost weight of chronic codes (I10, E11.9, E78.5, I25.10)
            adjusted_codes = []
            for code, desc, weight in codes:
                if code in ["I10", "E11.9", "E78.5", "I25.10"]:
                    adjusted_codes.append((code, desc, weight * 2))  # Double weight
                else:
                    adjusted_codes.append((code, desc, weight))
            codes = adjusted_codes
        
        # Number of diagnoses: 1-4
        num_dx = np.random.choice([1, 2, 3, 4], p=[0.20, 0.40, 0.25, 0.15])
        
        used = set()
        for rank in range(1, num_dx + 1):
            available = [(c, d, w) for (c, d, w) in codes if c not in used]
            if not available:
                break
            
            # Weighted selection
            code_list = [(c, d) for c, d, _ in available]
            weights = [w for _, _, w in available]
            total = sum(weights)
            weights = [w/total for w in weights]
            
            chosen_idx = np.random.choice(len(code_list), p=weights)
            icd_code, description = code_list[chosen_idx]
            
            diagnoses.append({
                "diagnosis_id": diagnosis_id,
                "encounter_id": enc['encounter_id'],
                "icd_code": icd_code,
                "description": description,
                "diagnosis_rank": rank
            })
            
            used.add(icd_code)
            diagnosis_id += 1
        
        if diagnosis_id % 10000 == 0:
            print(f"  Generated {diagnosis_id} diagnoses...")
    
    df = pd.DataFrame(diagnoses)
    save_and_load(df, "diagnoses", load_to_db)
    print(f"  ✓ Complete: {len(df)} diagnoses generated")
    return df


if __name__ == "__main__":
    generate_diagnoses(load_to_db=False)