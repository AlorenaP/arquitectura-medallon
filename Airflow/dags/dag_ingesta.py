from datetime import datetime, timedelta
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

with DAG(
    dag_id="carga_continua",
    description="Lanza el contenedor Ingesta cada minuto (lote nuevo a raw.personas)",
    start_date=datetime(2026, 1, 1),
    schedule_interval=timedelta(minutes=1),
    catchup=False,
    tags=["raw", "carga_continua"],
) as dag_continua:
    DockerOperator(
        task_id="ejecutar_ingesta_continua",
        image="ingesta:latest",
        api_version="auto",
        auto_remove="success",
        command="python ingesta_continua.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="medallon_net",
    )
