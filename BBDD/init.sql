/*
Esto crea el schema raw automaticamente la privera vez que Postgres inicializa sus datos
(Postgres ejecuta solo, en orden alfabético, todo lo que encuentre en /docker-entrypoint-initdb.d)
*/
CREATE SCHEMA IF NOT EXISTS raw;
