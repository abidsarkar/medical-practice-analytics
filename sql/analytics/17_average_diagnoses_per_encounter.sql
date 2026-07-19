--Basic Average Diagnoses Per Encounter
SELECT 
    ROUND(
        COUNT(d.diagnosis_id) * 1.0 / 
        NULLIF(COUNT(DISTINCT e.encounter_id), 0), 
        2
    ) AS avg_diagnoses_per_encounter
FROM 
    encounters e
LEFT JOIN 
    diagnoses d ON e.encounter_id = d.encounter_id;

--Average Diagnoses Per Encounter by Provider
SELECT 
    p.provider_id,
    p.first_name,
    p.last_name,
    p.specialty,
    COUNT(DISTINCT e.encounter_id) AS total_encounters,
    COUNT(d.diagnosis_id) AS total_diagnoses,
    ROUND(
        COUNT(d.diagnosis_id) * 1.0 / 
        NULLIF(COUNT(DISTINCT e.encounter_id), 0), 
        2
    ) AS avg_diagnoses_per_encounter
FROM 
    providers p
LEFT JOIN 
    appointments a ON p.provider_id = a.provider_id
LEFT JOIN 
    encounters e ON a.appointment_id = e.appointment_id
LEFT JOIN 
    diagnoses d ON e.encounter_id = d.encounter_id
GROUP BY 
    p.provider_id, p.first_name, p.last_name, p.specialty
HAVING 
    COUNT(DISTINCT e.encounter_id) > 0
ORDER BY 
    avg_diagnoses_per_encounter DESC;