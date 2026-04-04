set -a
source .env
set +a

cd terraform

export TF_VAR_project_id=$PROJECT
export TF_VAR_bucket_name=$BUCKET_NAME
export TF_VAR_dataset_name=$DATASET
export TF_VAR_project_location=$DATASET_LOCATION
export GOOGLE_APPLICATION_CREDENTIALS=$LOCAL_GCS_JSON_CREDENTIALS_PATH


terraform init && terraform apply -auto-approve && cd ..

mkdir -p airflow/dags airflow/logs
mkdir -p dbt
sudo chown -R $(id -u):0 airflow/dags airflow/logs
sudo chown -R $(id -u):0 dbt
chmod -R 775 airflow/dags airflow/logs
chmod -R 775 dbt
docker compose up -d

echo -e "\n"

echo -n "Waiting for Streamlit dashboard"
until curl -s -o /dev/null localhost:8501; do
    echo -n "."
    sleep 5
done
echo " Done!"

echo -e "\n\nExpose port 8501 and visit http://localhost:8501/ to see the dashboard."
echo -e "If the pipeline is running for the first time, streamlit will use preloaded tables to create the dashboard.\n\n"

echo -n "Waiting for Airflow UI"
until curl -s -o /dev/null localhost:8080; do
    echo -n "."
    sleep 5
done
echo " Done!"

echo -e "\n\nAirflow is UP!"
echo -e "\nExpose port 8080 and visit http://localhost:8080/ for airflow UI.\n\n"
# Extract and pretty-print Airflow credentials
creds=$(docker exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated)
echo "Airflow credentials:"
echo "user: $(echo $creds | jq -r 'keys[0]')"
echo "password: $(echo $creds | jq -r '.[keys[0]]')"


echo -e "\nExpose port 8080 and visit http://localhost:8080/ for airflow UI.\n\n"
echo -e "\nExpose port 8082 and visit http://localhost:8082/ for dbt docs.\n\n"
echo -e "\nExpose port 8501 and visit http://localhost:8501/ for streamlit.\n\n"