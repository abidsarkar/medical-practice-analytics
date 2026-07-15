WITH hourly_slots AS (
    SELECT 
        generate_series(
            date_trunc('hour', actual_start_time), 
            date_trunc('hour', actual_end_time), 
            '1 hour'::interval
        ) AS appointment_timestamp
    FROM appointments
)
SELECT 
    to_char(appointment_timestamp, 'HH12:00 AM') AS peak_hour,
    COUNT(*) AS active_appointments
FROM hourly_slots
GROUP BY peak_hour
ORDER BY active_appointments DESC
LIMIT 5;