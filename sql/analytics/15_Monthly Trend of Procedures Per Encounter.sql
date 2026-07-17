SELECT 
    DATE_TRUNC('month', e.encounter_date) AS month,
    COUNT(DISTINCT e.encounter_id) AS total_encounters,
    COUNT(pr.procedure_id) AS total_procedures,
    ROUND(
        COUNT(pr.procedure_id) * 1.0 / 
        NULLIF(COUNT(DISTINCT e.encounter_id), 0), 
        2
    ) AS avg_procedures_per_encounter,
    -- Running average
    ROUND(
        AVG(COUNT(pr.procedure_id) * 1.0 / NULLIF(COUNT(DISTINCT e.encounter_id), 0)) 
            OVER (ORDER BY DATE_TRUNC('month', e.encounter_date) ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 
        2
    ) AS three_month_moving_avg
FROM 
    encounters e
LEFT JOIN 
    procedures pr ON e.encounter_id = pr.encounter_id
GROUP BY 
    DATE_TRUNC('month', e.encounter_date)
HAVING 
    COUNT(DISTINCT e.encounter_id) >= 5
ORDER BY 
    month DESC;