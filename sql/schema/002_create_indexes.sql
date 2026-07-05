-- for patients table
create INDEX idx_patients_dob ON patients (dob);
create INDEX idx_patients_insurance_provider ON patients (insurance_provider);