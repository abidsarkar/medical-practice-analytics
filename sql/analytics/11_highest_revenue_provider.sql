select
*
from procedures;
SELECT 
    p.provider_id,
    p.first_name,
    p.last_name,
    p.specialty,
    COALESCE(SUM(pay.amount), 0) AS total_revenue
FROM 
    providers p
LEFT JOIN 
    appointments a ON p.provider_id = a.provider_id
LEFT JOIN 
    encounters e ON a.appointment_id = e.appointment_id
LEFT JOIN 
    claims c ON e.encounter_id = c.encounter_id
LEFT JOIN 
    payments pay ON c.claim_id = pay.claim_id
WHERE 
    c.claim_status = 'Paid' OR c.claim_status IS NULL
GROUP BY 
    p.provider_id, p.first_name, p.last_name, p.specialty
ORDER BY 
    total_revenue DESC
LIMIT 10;