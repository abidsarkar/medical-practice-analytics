SELECT 
    status, 
    ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100,2) AS percentage
FROM appointments 
GROUP BY status;