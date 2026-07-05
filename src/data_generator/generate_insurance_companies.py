# generate_insurance_companies.py
import pandas as pd
from config import INSURANCE_COMPANIES, save_and_load

def generate_insurance_companies(load_to_db=False):
    print(f"\n{'='*60}")
    print("GENERATING INSURANCE COMPANIES")
    print(f"{'='*60}")

    df = pd.DataFrame(INSURANCE_COMPANIES)
    df.index += 1  # start insurance_company_id at 1
    df.insert(0, 'insurance_company_id', df.index)

    save_and_load(df, "insurance_companies", load_to_db)
    print(f"  ✓ Complete: {len(df)} insurance companies generated")
    return df

if __name__ == "__main__":
    generate_insurance_companies(load_to_db=False)