from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

with DAG(
    dag_id="pipeline_medallon",
    description="Ingesta continua -> staging (vistas) -> test -> marts (tabla)",
    start_date=datetime(2026, 1, 1),
    schedule_interval=timedelta(minutes=1),
    catchup=False,
    tags=["raw", "staging", "marts", "dbt"],
) as dag:

    carga_continua = DockerOperator(
        task_id="carga_continua",
        image="ingesta:latest",
        api_version="auto",
        auto_remove="success",
        command="python ingesta_continua.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="medallon_net",
    )

    staging = DockerOperator(
        task_id="staging",
        image="dbt:latest",
        api_version="auto",
        auto_remove="success",
        command="dbt run --select staging",
        docker_url="unix://var/run/docker.sock",
        network_mode="medallon_net",
    )

    test = DockerOperator(
        task_id="test",
        image="dbt:latest",
        api_version="auto",
        auto_remove="success",
        command="dbt test",
        docker_url="unix://var/run/docker.sock",
        network_mode="medallon_net",
    )

    marts = DockerOperator(
        task_id="marts",
        image="dbt:latest",
        api_version="auto",
        auto_remove="success",
        command="dbt run --select marts",
        docker_url="unix://var/run/docker.sock",
        network_mode="medallon_net",
    )

    carga_continua >> staging >> test >> marts
