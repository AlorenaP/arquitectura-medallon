from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

with DAG(
    dag_id="carga_inicial",
    description="Lanza el contenedor Ingesta una sola vez (carga inicial a raw.personas)",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@once",
    catchup=False,
    tags=["raw", "carga_inicial"],
) as dag_inicial:
    DockerOperator(
        task_id="ejecutar_ingesta_inicial",
        image="ingesta:latest",
        api_version="auto",
        auto_remove="success",
        command="python ingesta_inicial.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="medallon_net",
    )
