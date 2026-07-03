# Arquitectura Medallón — Fase 1 (Raw)

Stack con Docker Compose: contenedor Python (ingesta inicial + ingesta continua)
y contenedor PostgreSQL, aterrizando datos de personas en el schema `raw`.


Los datos se obtienen consumiendo la API pública [randomuser.me](https://randomuser.me/),
en vez de generarse con Faker.

## Componentes

- **Ingesta**: contenedor Python con dos jobs secuenciales:
  - `ingesta_inicial.py`: carga inicial de 500 registros desde randomuser.me.
  - `ingesta_continua.py`: cada 15 segundos, inserta un lote de 5 registros nuevos.
- **BBDD**: contenedor PostgreSQL. Al arrancar por primera vez, crea automáticamente
  el schema `raw` (ver `BBDD/init.sql`).

## Levantar el stack

\`\`\`bash
docker compose up -d --build
\`\`\`

## Ver logs de la ingesta

\`\`\`bash
docker compose logs -f ingesta
\`\`\`

## Verificar datos

\`\`\`bash
docker exec -it bbdd_postgres psql -U admin -d ejercicio_db -c "SELECT COUNT(*) FROM raw.personas;"
\`\`\`

## Notas

- La tabla `raw.personas` se crea automáticamente en el primer arranque de la ingesta inicial.
- La ingesta continua depende de la disponibilidad de la API externa; si falla una petición,
  registra el error en el log y reintenta en el siguiente ciclo (no detiene el contenedor).
