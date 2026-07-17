SELECT 
    ROUND(
        COUNT(pr.procedure_id) * 1.0 / 
        NULLIF(COUNT(DISTINCT e.encounter_id), 0), 
        2
    ) AS avg_procedures_per_encounter
FROM 
    encounters e
LEFT JOIN 
    procedures pr ON e.encounter_id = pr.encounter_id;