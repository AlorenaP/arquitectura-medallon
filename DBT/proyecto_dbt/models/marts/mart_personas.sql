/* Agregación simple: cuántas personas se ingestaron
 por día — un ejemplo claro de "agregar el dato".
*/

select
    date_trunc('day', fecha_ingesta) as fecha,
    count(*) as total_personas
from {{ ref('stg_personas') }}
group by 1
order by 1
