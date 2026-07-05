import os

# Folder to store the CSV files
OUTPUT_DIR = '../../data/synthetic'
os.makedirs(OUTPUT_DIR, exist_ok=True)

files = [
    "insurance_companies.csv",
    "patients.csv",
    "patient_insurance.csv",
    "providers.csv",
    "appointments.csv",
    "encounters.csv",
    "diagnoses.csv",
    "procedures.csv",
    "claims.csv",
    "claim_line_items.csv",
    "payments.csv"
]

for file_name in files:
    file_path = os.path.join(OUTPUT_DIR, file_name)

    # Create an empty file
    open(file_path, "w").close()

    print(f"Created: {file_path}")

print("\n✅ All empty CSV files have been created successfully!")