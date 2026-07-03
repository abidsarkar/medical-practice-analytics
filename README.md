```bash
pip install pandas faker psycopg2-binary sqlalchemy jupyter fastapi uvicorn scikit-learn
pip freeze > requirements.txt
```
```bash
git init
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "data/synthetic/*.csv" >> .gitignore
echo ".ipynb_checkpoints/" >> .gitignore
```
```bash
psql -U postgres
CREATE DATABASE medical_practice;
CREATE USER med_analyst WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE medical_practice TO med_analyst;
```
```bash
psql -d medical_practice -U med_analyst
```


