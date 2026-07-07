# Arquitectura Medallón con Docker Compose

Pipeline de datos completo usando **Docker Compose**, con **Apache Airflow** como orquestador,
**PostgreSQL** como almacén, y **dbt** como capa de transformación, siguiendo el patrón de
arquitectura medallón (Raw → Staging → Marts).

## Arquitectura

```mermaid
graph TD
    subgraph Airflow["Contenedor Airflow (orquestador)"]
        DAG1["DAG: carga_inicial<br/>(una sola vez)"]
        DAG2["DAG: pipeline_medallon<br/>(cada 1 minuto)"]
    end

    subgraph Tareas["Tareas de pipeline_medallon (DockerOperator, en orden)"]
        T1["1. carga_continua"] --> T2["2. staging"] --> T3["3. test"] --> T4["4. marts"]
    end

    ING["Contenedor Ingesta<br/>(efímero, imagen: ingesta:latest)<br/>Python + randomuser.me API"]
    DBT["Contenedor dbt<br/>(efímero, imagen: dbt:latest)"]
    PG[("PostgreSQL<br/>schemas: raw / staging / marts")]
    DOCS["Contenedor dbt-docs<br/>(persistente, puerto 8082)"]
    ADM["Contenedor Adminer<br/>(persistente, puerto 8080)"]

    DAG1 -.lanza vía docker.sock.-> ING
    T1 -.lanza vía docker.sock.-> ING
    T2 -.lanza vía docker.sock.-> DBT
    T3 -.lanza vía docker.sock.-> DBT
    T4 -.lanza vía docker.sock.-> DBT

    ING -->|INSERT| PG
    DBT -->|raw -> staging (vistas, limpieza)| PG
    DBT -->|staging -> marts (tablas, agregación)| PG
    DOCS --> PG
    ADM --> PG
```

## Fases del proyecto

### Fase 1 — Ingesta + orquestación
- **Ingesta** (`Ingesta/`): contenedor Python que consume la API pública [randomuser.me](https://randomuser.me/)
  y escribe en `raw.personas`. No corre solo — Airflow lo lanza bajo demanda.
- **BBDD** (`BBDD/`): PostgreSQL con 3 esquemas creados desde el arranque (`init.sql`): `raw`, `staging`, `marts`.
- **Airflow** (`Airflow/`): orquesta todo vía `DockerOperator`, usando el socket de Docker del host
  (`/var/run/docker.sock`) para lanzar los contenedores `ingesta:latest` y `dbt:latest` como tareas.

### Fase 2 — Transformación con dbt
- **DBT** (`DBT/`): proyecto dbt que transforma los datos:
  - `models/staging/stg_personas.sql` → **vista**, limpia el dato crudo de `raw.personas`
    (trim de texto, email en minúsculas, descarta filas sin email).
  - `models/staging/schema.yml` → tests (`unique`, `not_null`) sobre `stg_personas`.
  - `models/marts/mart_personas.sql` → **tabla**, agrega el dato de `staging` (conteo de personas por día).

### Fase 3 — UI de Airflow expuesta
- Airflow corre en modo `standalone`, con su webserver publicado en el puerto `8081` del host.
- Autenticación con usuario `admin` y contraseña autogenerada (ver sección de credenciales abajo).

## Estructura del repositorio

medallon/
├── docker-compose.yml
├── README.md
├── .gitignore
├── BBDD/
│   ├── Dockerfile
│   └── init.sql
├── Ingesta/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── conexion.py
│   ├── ingesta_inicial.py
│   └── ingesta_continua.py
├── DBT/
│   ├── Dockerfile
│   └── proyecto_dbt/
│       ├── dbt_project.yml
│       ├── profiles.yml
│       ├── macros/
│       │   └── generate_schema_name.sql
│       └── models/
│           ├── staging/
│           │   ├── stg_personas.sql
│           │   └── schema.yml
│           └── marts/
│               └── mart_personas.sql
└── Airflow/
├── Dockerfile
├── requirements.txt
└── dags/
├── dag_ingesta.py         # DAG: carga_inicial (@once)
└── pipeline_medallon.py   # DAG: carga_continua -> staging -> test -> marts (cada 1 min)

## Puesta en marcha

```bash
# 1. Construir las imágenes que Airflow lanzará bajo demanda
docker compose build ingesta dbt

# 2. Levantar Postgres, Airflow, y la UI de documentación de dbt
docker compose up -d --build bbdd airflow dbt-docs

# 3. (Opcional) Adminer para explorar la base de datos visualmente
docker run -d --name adminer -p 8080:8080 --network medallon_net adminer
```

## Accesos

| Servicio | URL | Credenciales |
|---|---|---|
| Airflow UI | http://localhost:8081 | usuario `admin`, contraseña: ver comando abajo |
| Adminer | http://localhost:8080 | servidor `bbdd_postgres`, usuario `admin`, contraseña `admin123`, BD `ejercicio_db` |
| dbt docs | http://localhost:8082 | sin autenticación |

Obtener la contraseña de Airflow:
```bash
docker exec -it airflow_orquestador cat /opt/airflow/standalone_admin_password.txt
```

> Si accedes desde fuera de la VM (por ejemplo VirtualBox con NAT), recuerda crear una regla de
> reenvío de puertos por cada uno de estos servicios.

## Verificación

```bash
# Confirmar los 3 esquemas
docker exec -it bbdd_postgres psql -U admin -d ejercicio_db -c "\dn"

# Confirmar que raw sigue creciendo (ingesta continua)
docker exec -it bbdd_postgres psql -U admin -d ejercicio_db -c "SELECT COUNT(*) FROM raw.personas;"

# Confirmar la vista de staging (dato limpio)
docker exec -it bbdd_postgres psql -U admin -d ejercicio_db -c "SELECT * FROM staging.stg_personas LIMIT 5;"

# Confirmar la tabla de marts (dato agregado)
docker exec -it bbdd_postgres psql -U admin -d ejercicio_db -c "SELECT * FROM marts.mart_personas;"
```

## Notas técnicas

- **DockerOperator + socket de Docker**: Airflow monta `/var/run/docker.sock` para lanzar contenedores
  "hermanos" (no hijos) desde dentro de sí mismo. Cada tarea especifica explícitamente
  `network_mode="medallon_net"` porque los contenedores lanzados así no heredan la red de Airflow automáticamente.
- **`ref()` en dbt**: los modelos de `marts` referencian los de `staging` con `{{ ref('stg_personas') }}`
  en vez de escribir el nombre de esquema a mano — esto es lo que le permite a dbt calcular el orden
  correcto de ejecución (su propio grafo de dependencias interno).
- **Recursos de la VM**: Airflow completo (webserver + scheduler + triggerer) necesita un mínimo
  razonable de RAM (se recomienda 4GB+) para que el webserver levante sus workers de gunicorn a tiempo.
