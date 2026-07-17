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
-- Detailed No-Show Analysis by Provider
SELECT 
    p.provider_id,
    p.first_name,
    p.last_name,
    p.specialty,
    COUNT(*) AS total_appointments,
    COUNT(CASE WHEN a.status = 'No-Show' THEN 1 END) AS no_shows,
    COUNT(CASE WHEN a.status = 'Completed' THEN 1 END) AS completed,
    COUNT(CASE WHEN a.status = 'Cancelled' THEN 1 END) AS cancelled,
    COUNT(CASE WHEN a.status = 'Checked-In' THEN 1 END) AS checked_in,
    ROUND(
        (COUNT(CASE WHEN a.status = 'No-Show' THEN 1 END) * 100.0) / 
        NULLIF(COUNT(*), 0), 
        2
    ) AS no_show_rate,
    ROUND(
        (COUNT(CASE WHEN a.status = 'Completed' THEN 1 END) * 100.0) / 
        NULLIF(COUNT(*), 0), 
        2
    ) AS completion_rate,
    ROUND(
        (COUNT(CASE WHEN a.status = 'Cancelled' THEN 1 END) * 100.0) / 
        NULLIF(COUNT(*), 0), 
        2
    ) AS cancellation_rate
FROM 
    providers p
LEFT JOIN 
    appointments a ON p.provider_id = a.provider_id
GROUP BY 
    p.provider_id, p.first_name, p.last_name, p.specialty
HAVING 
    COUNT(*) > 0
ORDER BY 
    no_show_rate DESC;