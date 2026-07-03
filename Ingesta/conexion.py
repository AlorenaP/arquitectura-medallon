import os
import time
import psycopg2

def conectar(reintentos=10, espera=3):
    parametros = dict(
        host=os.environ.get("DB_HOST", "bbdd"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "ejercicio_db"),
        user=os.environ.get("DB_USER", "admin"),
        password=os.environ.get("DB_PASSWORD", "admin123"),
    )
    for intento in range(1, reintentos + 1):
        try:
            conn = psycopg2.connect(**parametros)
            print(f"[conexion] Conectado a Postgres (intento {intento})")
            return conn
        except psycopg2.OperationalError as e:
            print(f"[conexion] Postgres no disponible aún (intento {intento}/{reintentos}): {e}")
            time.sleep(espera)
    raise RuntimeError("No se pudo conectar a Postgres tras varios intentos")
