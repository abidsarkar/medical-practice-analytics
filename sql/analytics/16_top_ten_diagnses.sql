--Top 10 Primary Diagnoses (Diagnosis Rank = 1)
SELECT 
    icd_code,
    description,
    COUNT(*) AS primary_diagnosis_count
FROM 
    diagnoses
WHERE 
    diagnosis_rank = 1
GROUP BY 
    icd_code, description
ORDER BY 
    primary_diagnosis_count DESC
LIMIT 10;
-- top ten Procedures
SELECT 
    icd_code,
    description,
    COUNT(*) AS diagnosis_count
FROM 
    diagnoses
GROUP BY 
    icd_code, description
ORDER BY 
    diagnosis_count DESC
LIMIT 10;
--Top 10 Diagnoses by Encounter Count (One per Encounter)