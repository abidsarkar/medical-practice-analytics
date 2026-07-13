SELECT
a.company_name,
count(b.insurance_company_id) as total_consumer,
round(count(b.insurance_company_id)::NUMERIC / SUM(COUNT(*)) OVER () * 100,2)  as percentage
from insurance_companies a
JOIN patient_insurance b
ON a.insurance_company_id = b.insurance_company_id
GROUP BY 1;
