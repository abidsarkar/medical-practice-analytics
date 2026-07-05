# generate_claims.py
import pandas as pd
import numpy as np
import random
from datetime import timedelta
from config import save_and_load, DATA_DIR

np.random.seed(303)
random.seed(303)

def generate_claims(load_to_db=False):
    print(f"\n{'='*60}")
    print("GENERATING CLAIMS & LINE ITEMS")
    print(f"{'='*60}")

    encounters_df = pd.read_csv(DATA_DIR / "encounters.csv")
    procedures_df = pd.read_csv(DATA_DIR / "procedures.csv")

    # Group procedures by encounter_id
    proc_by_encounter = procedures_df.groupby('encounter_id')

    claims = []
    line_items = []
    claim_id = 1
    line_id = 1

    for _, enc in encounters_df.iterrows():
        enc_id = enc['encounter_id']
        if enc_id not in proc_by_encounter.groups:
            continue

        enc_procs = proc_by_encounter.get_group(enc_id)
        total_charge = enc_procs['charge_amount'].sum()

        filing_date = pd.to_datetime(enc['encounter_date']) + timedelta(days=random.randint(1, 7))

        # Status distribution
        roll = random.random()
        if roll < 0.10:
            status = "Denied"
            adj_date = filing_date + timedelta(days=random.randint(14, 45))
        elif roll < 0.20:
            status = "Pending"
            adj_date = None
        elif roll < 0.75:
            status = "Paid"
            adj_date = filing_date + timedelta(days=random.randint(10, 60))
        else:
            status = "Partial"
            adj_date = filing_date + timedelta(days=random.randint(20, 60))

        claims.append({
            "claim_id": claim_id,
            "encounter_id": enc_id,
            "total_charge": round(total_charge, 2),
            "claim_status": status,
            "filing_date": filing_date,
            "adjudication_date": adj_date
        })

        # Line items
        for _, proc in enc_procs.iterrows():
            charge = proc['charge_amount'] * proc['units']
            if status == "Paid":
                payment = round(charge * random.uniform(0.60, 0.90), 2)
                adjustment = round(charge - payment, 2)
            elif status == "Denied":
                payment = 0.00
                adjustment = round(charge, 2)
            elif status == "Partial":
                payment = round(charge * random.uniform(0.30, 0.70), 2)
                adjustment = round(charge - payment, 2)
            else:  # Pending
                payment = 0.00
                adjustment = 0.00

            line_items.append({
                "line_id": line_id,
                "claim_id": claim_id,
                "procedure_id": proc['procedure_id'],
                "charge_amount": round(charge, 2),
                "payment_amount": payment,
                "adjustment_amount": adjustment
            })
            line_id += 1

        claim_id += 1
        if claim_id % 5000 == 0:
            print(f"  Generated {claim_id} claims...")

    claims_df = pd.DataFrame(claims)
    line_items_df = pd.DataFrame(line_items)

    save_and_load(claims_df, "claims", load_to_db)
    save_and_load(line_items_df, "claim_line_items", load_to_db)

    print(f"  ✓ Complete: {len(claims_df)} claims, {len(line_items_df)} line items")
    return claims_df, line_items_df

if __name__ == "__main__":
    generate_claims(load_to_db=False)