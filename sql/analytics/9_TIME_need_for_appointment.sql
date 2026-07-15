SELECT
avg(actual_end_time - actual_start_time) as avg_wating_time
from appointments
where status = 'Completed';  
SELECT
MAX(actual_end_time - actual_start_time) as avg_wating_time
from appointments
where status = 'Completed';
SELECT
min(actual_end_time - actual_start_time) as avg_wating_time
from appointments;