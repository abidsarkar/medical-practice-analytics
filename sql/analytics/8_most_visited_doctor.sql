SELECT
a.provider_id,
CONCAT(b.first_name,' ',b.last_name) as name,
b.specialty,
count(a.provider_id) as total_visited_patient
from appointments a
JOIN providers b 
ON a.provider_id = b.provider_id
where a.status ='Completed'
group by 1 ,2,3
order by 4 desc;