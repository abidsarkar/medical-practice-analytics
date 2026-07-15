SELECT
count(*) filter(where gender='Female') as total_female,
count(*) filter(where gender='Male') as total_male
from patients