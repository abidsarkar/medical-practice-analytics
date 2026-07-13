-- witch age group successfully complete the visit
with age_visit as (SELECT
	patient_id,
	gender,
	case
		WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 0 AND 18 THEN '0–18'
        WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 19 AND 35 THEN '19–35'
        WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 36 AND 50 THEN '36–50'
        WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 51 AND 65 THEN '51–65'
        ELSE '65+'
    END AS age_group
from patients)
select 
age_group,
count(a.age_group)as total_visited_group
from age_visit a 
JOIN appointments as b
ON a.patient_id = b.patient_id
where b.status =  'Completed'
group by age_group
order by 1;
-- most cancel age group
with age_visit as (SELECT
	patient_id,
	gender,
	case
		WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 0 AND 18 THEN '0–18'
        WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 19 AND 35 THEN '19–35'
        WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 36 AND 50 THEN '36–50'
        WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 51 AND 65 THEN '51–65'
        ELSE '65+'
    END AS age_group
from patients)
select 
age_group,
count(a.age_group)as total_visited_group
from age_visit a 
JOIN appointments as b
ON a.patient_id = b.patient_id
where b.status =  'Cancelled'
group by age_group
order by 1;
-- get appointment but not coming
with age_visit as (SELECT
	patient_id,
	gender,
	case
		WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 0 AND 18 THEN '0–18'
        WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 19 AND 35 THEN '19–35'
        WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 36 AND 50 THEN '36–50'
        WHEN EXTRACT(YEAR FROM age(dob)) BETWEEN 51 AND 65 THEN '51–65'
        ELSE '65+'
    END AS age_group
from patients)
select 
age_group,
count(a.age_group)as total_visited_group
from age_visit a 
JOIN appointments as b
ON a.patient_id = b.patient_id
where b.status =  'No-Show'
group by age_group
order by 1;
-- male vs female No-show ratio
