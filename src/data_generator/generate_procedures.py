# generate_procedures.py
import pandas as pd
import numpy as np
import random
from config import save_and_load, DATA_DIR, CPT_CODES, SPECIALTY_PROCEDURES

np.random.seed(202)
random.seed(202)

def generate_procedures(load_to_db=False):
    """Generate procedures based on encounter specialty."""
    print(f"\n{'='*60}")
    print(f"GENERATING PROCEDURES")
    print(f"{'='*60}")
    
    # Load dependent data
    encounters_df = pd.read_csv(DATA_DIR / "encounters.csv")
    appointments_df = pd.read_csv(DATA_DIR / "appointments.csv")
    providers_df = pd.read_csv(DATA_DIR / "providers.csv")
    
    # Create lookups
    # appointments now acts as the bridge between encounters and providers
    appt_lookup = appointments_df.set_index('appointment_id')
    provider_specialty = dict(zip(providers_df['provider_id'], providers_df['specialty']))
    
    # CPT code lookups
    cpt_desc = {code: desc for code, desc, _, _ in CPT_CODES}
    cpt_charge = {code: charge for code, _, charge, _ in CPT_CODES}
    
    procedures = []
    procedure_id = 1
    
    for _, enc in encounters_df.iterrows():
        # Get provider_id from the appointment (bridge table)
        appt_id = enc['appointment_id']
        appt_info = appt_lookup.loc[appt_id]
        provider_id = appt_info['provider_id']
        
        # Get specialty for procedure weighting
        specialty = provider_specialty.get(provider_id, 'default')
        proc_weights = SPECIALTY_PROCEDURES.get(specialty, SPECIALTY_PROCEDURES['default'])
        
        # 1-5 procedures per encounter
        num_procs = np.random.choice([1, 2, 3, 4, 5], p=[0.30, 0.30, 0.20, 0.15, 0.05])
        
        used = set()
        for _ in range(num_procs):
            available = [(code, w) for code, w in proc_weights if code not in used]
            if not available:
                break
            
            codes = [a[0] for a in available]
            weights = [a[1] for a in available]
            weights = [w/sum(weights) for w in weights]
            chosen = np.random.choice(codes, p=weights)
            
            desc = cpt_desc.get(chosen, "Unknown")
            base = cpt_charge.get(chosen, 75.00)
            charge = round(base * random.uniform(0.85, 1.15), 2)
            
            procedures.append({
                "procedure_id": procedure_id,
                "encounter_id": enc['encounter_id'],
                "cpt_code": chosen,
                "description": desc,
                "units": random.randint(1, 3) if chosen in ["97110", "97140"] else 1,
                "charge_amount": charge
            })
            
            used.add(chosen)
            procedure_id += 1
        
        if procedure_id % 10000 == 0:
            print(f"  Generated {procedure_id} procedures...")
    
    df = pd.DataFrame(procedures)
    save_and_load(df, "procedures", load_to_db)
    print(f"  ✓ Complete: {len(df)} procedures generated")
    return df

if __name__ == "__main__":
    generate_procedures(load_to_db=False)