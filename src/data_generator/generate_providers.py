# generate_providers.py
import pandas as pd
import numpy as np
from faker import Faker
import random
from config import SPECIALTIES, save_and_load

fake = Faker()
np.random.seed(123)
random.seed(123)

def generate_providers(n=50, load_to_db=False):
    """Generate providers with specialty distribution."""
    print(f"\n{'='*60}")
    print(f"GENERATING {n} PROVIDERS")
    print(f"{'='*60}")
    
    # More primary care than specialists
    specialty_weights = [0.20, 0.15, 0.10, 0.08, 0.10, 0.07, 0.05, 0.08, 0.10, 0.07]
    
    providers = []
    for provider_id in range(1, n + 1):
        specialty = np.random.choice(SPECIALTIES, p=specialty_weights)
        providers.append({
            "provider_id": provider_id,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "specialty": specialty,
            "npi": ''.join([str(random.randint(0, 9)) for _ in range(10)])
        })
    
    df = pd.DataFrame(providers)
    save_and_load(df, "providers", load_to_db)
    print(f"  ✓ Complete: {len(df)} providers generated")
    return df

if __name__ == "__main__":
    generate_providers(50, load_to_db=False)