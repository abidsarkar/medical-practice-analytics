WITH provider_patient_counts AS (
    SELECT 
        p.provider_id,
        p.first_name,
        p.last_name,
        COUNT(DISTINCT a.patient_id) AS patient_count
    FROM 
        providers p
    LEFT JOIN 
        appointments a ON p.provider_id = a.provider_id
    GROUP BY 
        p.provider_id, p.first_name, p.last_name
)
SELECT 
    ROUND(AVG(patient_count), 2) AS avg_patients_per_provider
FROM 
    provider_patient_counts;