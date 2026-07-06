FROM python:3.12-slim
WORKDIR /usr/app/proyecto_dbt
RUN pip install --no-cache-dir dbt-postgres
COPY proyecto_dbt /usr/app/proyecto_dbt
ENV DBT_PROFILES_DIR=/usr/app/proyecto_dbt
CMD ["dbt", "run"]
