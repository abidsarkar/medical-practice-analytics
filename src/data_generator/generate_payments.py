# generate_payments.py
import pandas as pd
import numpy as np
import random
from datetime import timedelta
from config import save_and_load, DATA_DIR

np.random.seed(404)
random.seed(404)

def generate_payments(load_to_db=False):
    """Generate payments for paid and partially paid claims."""
    print(f"\n{'='*60}")
    print(f"GENERATING PAYMENTS")
    print(f"{'='*60}")
    
    # Load claims
    claims_df = pd.read_csv(DATA_DIR / "claims.csv")
    
    # Only paid or partial claims
    eligible = claims_df[claims_df['claim_status'].isin(['Paid', 'Partial'])]
    print(f"  Found {len(eligible)} eligible claims")
    
    payments = []
    payment_id = 1
    
    for _, claim in eligible.iterrows():
        payment_type = np.random.choice(["Insurance", "Patient"], p=[0.80, 0.20])
        
        # Usually 1 payment, sometimes 2
        num_payments = np.random.choice([1, 1, 1, 2], p=[0.70, 0.15, 0.10, 0.05])
        
        if claim['claim_status'] == 'Paid':
            total_payment = claim['total_charge'] * random.uniform(0.75, 0.95)
        else:
            total_payment = claim['total_charge'] * random.uniform(0.30, 0.70)
        
        remaining = total_payment
        for i in range(num_payments):
            if i == num_payments - 1:
                amount = round(remaining, 2)
            else:
                amount = round(remaining * random.uniform(0.3, 0.7), 2)
                remaining -= amount
            
            if pd.notna(claim['adjudication_date']):
                base_date = pd.to_datetime(claim['adjudication_date'])
            else:
                base_date = pd.to_datetime(claim['filing_date'])
            
            payment_date = base_date + timedelta(days=random.randint(5, 30))
            
            payments.append({
                "payment_id": payment_id,
                "claim_id": claim['claim_id'],
                "payment_date": payment_date,
                "amount": max(amount, 0.01),
                "payment_type": payment_type
            })
            payment_id += 1
        
        if payment_id % 5000 == 0:
            print(f"  Generated {payment_id} payments...")
    
    df = pd.DataFrame(payments)
    save_and_load(df, "payments", load_to_db)
    print(f"  ✓ Complete: {len(df)} payments generated")
    return df

if __name__ == "__main__":
    generate_payments(load_to_db=False)