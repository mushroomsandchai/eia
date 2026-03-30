mkdir -p airflow/dags airflow/logs
mkdir -p dbt
sudo chown -R $(id -u):0 airflow/dags airflow/logs
sudo chown -R $(id -u):0 dbt
chmod -R 775 airflow/dags airflow/logs
chmod -R 775 dbt
docker compose up -d
until curl -s -o /dev/null localhost:8080; do
  echo "Waiting for Airflow UI..."
  sleep 10
done
echo "Airflow is UP!"
echo "expose port 8080 and visit http://localhost:8080/"
echo "{user : password}"
docker exec airflow cat simple_auth_manager_passwords.json.generated