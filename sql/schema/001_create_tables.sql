-- Connect to medical_practice database first
-- \c medical_practice

CREATE TABLE IF NOT EXISTS patients (
    patient_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    dob DATE,
    gender VARCHAR(10),
    insurance_provider VARCHAR(200),
    insurance_plan VARCHAR(200),
    date_registered DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS providers (
    provider_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    specialty VARCHAR(100),
    npi VARCHAR(10) UNIQUE
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    provider_id INT REFERENCES providers(provider_id),
    scheduled_time TIMESTAMP,
    actual_start_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('Completed','No-Show','Cancelled','Checked-In'))
);

CREATE TABLE IF NOT EXISTS encounters (
    encounter_id SERIAL PRIMARY KEY,
    appointment_id INT REFERENCES appointments(appointment_id),
    patient_id INT REFERENCES patients(patient_id),
    provider_id INT REFERENCES providers(provider_id),
    encounter_date DATE,
    chief_complaint TEXT
);

CREATE TABLE IF NOT EXISTS diagnoses (
    diagnosis_id SERIAL PRIMARY KEY,
    encounter_id INT REFERENCES encounters(encounter_id),
    icd_code VARCHAR(10),
    description VARCHAR(500),
    diagnosis_rank INT CHECK (diagnosis_rank IN (1,2,3,4))
);

CREATE TABLE IF NOT EXISTS procedures (
    procedure_id SERIAL PRIMARY KEY,
    encounter_id INT REFERENCES encounters(encounter_id),
    cpt_code VARCHAR(10),
    description VARCHAR(500),
    units INT DEFAULT 1,
    charge_amount DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id SERIAL PRIMARY KEY,
    encounter_id INT REFERENCES encounters(encounter_id),
    patient_id INT REFERENCES patients(patient_id),
    provider_id INT REFERENCES providers(provider_id),
    total_charge DECIMAL(10,2),
    claim_status VARCHAR(20) CHECK (claim_status IN ('Paid','Denied','Pending','Partial')),
    filing_date DATE,
    adjudication_date DATE
);

CREATE TABLE IF NOT EXISTS claim_line_items (
    line_id SERIAL PRIMARY KEY,
    claim_id INT REFERENCES claims(claim_id),
    procedure_id INT REFERENCES procedures(procedure_id),
    charge_amount DECIMAL(10,2),
    payment_amount DECIMAL(10,2) DEFAULT 0.00,
    adjustment_amount DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    claim_id INT REFERENCES claims(claim_id),
    payment_date DATE,
    amount DECIMAL(10,2),
    payment_type VARCHAR(20) CHECK (payment_type IN ('Insurance','Patient'))
);