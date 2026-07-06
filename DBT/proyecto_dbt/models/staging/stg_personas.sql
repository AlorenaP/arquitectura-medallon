/* Limpieza básica: quita espacios sobrantes,
 normaliza email a minúsculas, descarta filas sin email.
*/
select
    id,
    trim(nombre) as nombre,
    lower(trim(email)) as email,
    trim(direccion) as direccion,
    telefono,
    fecha_nacimiento,
    fecha_ingesta
from raw.personas
where email is not null
