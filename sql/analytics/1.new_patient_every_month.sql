-- every month
SELECT
to_char(date_registered,'YYYY-MM') as month,
count(patient_id) as total_patient
from patients
group by 1
order by 1
-- quatre wise user register
SELECT
    to_char(date_registered, 'YYYY-"Q"Q') as quarter,
    count(patient_id) as total_patient
FROM patients
GROUP BY 1
ORDER BY 1;
--weak wise
SELECT
    to_char(date_registered, 'YYYY-"W"WW') as week,
    count(patient_id) as total_patient
FROM patients
GROUP BY 1
ORDER BY 1;
