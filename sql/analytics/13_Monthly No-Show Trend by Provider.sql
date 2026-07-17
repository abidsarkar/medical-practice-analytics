SELECT 
    p.provider_id,
    p.first_name,
    p.last_name,
    DATE_TRUNC('month', a.scheduled_time) AS month,
    COUNT(*) AS appointments,
    COUNT(CASE WHEN a.status = 'No-Show' THEN 1 END) AS no_shows,
    ROUND(
        (COUNT(CASE WHEN a.status = 'No-Show' THEN 1 END) * 100.0) / 
        NULLIF(COUNT(*), 0), 
        2
    ) AS monthly_no_show_rate
FROM 
    providers p
JOIN 
    appointments a ON p.provider_id = a.provider_id
GROUP BY 
    p.provider_id, p.first_name, p.last_name, 
    DATE_TRUNC('month', a.scheduled_time)
HAVING 
    COUNT(*) >= 3  
ORDER BY 
    p.provider_id, month DESC;