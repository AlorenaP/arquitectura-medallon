import time
import requests
from conexion import conectar

INTERVALO_SEGUNDOS = 15
REGISTROS_POR_LOTE = 5
API_URL = "https://randomuser.me/api/"

def obtener_personas(cantidad):
    respuesta = requests.get(API_URL, params={"results": cantidad, "nat": "es"}, timeout=10)
    respuesta.raise_for_status()
    return respuesta.json()["results"]

def main():
    conn = conectar()
    conn.autocommit = True
    cur = conn.cursor()

    print("[ingesta_continua] Iniciando bucle de ingesta continua desde randomuser.me...")
    while True:
        try:
            personas = obtener_personas(REGISTROS_POR_LOTE)
            for p in personas:
                nombre = f"{p['name']['first']} {p['name']['last']}"
                direccion = f"{p['location']['street']['name']} {p['location']['street']['number']}, {p['location']['city']}, {p['location']['country']}"
                fecha_nacimiento = p["dob"]["date"][:10]

                cur.execute(
                    """
                    INSERT INTO raw.personas (nombre, email, direccion, telefono, fecha_nacimiento)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (nombre, p["email"], direccion, p["phone"], fecha_nacimiento),
                )
            print(f"[ingesta_continua] Insertado lote de {len(personas)} registros")
        except requests.exceptions.RequestException as e:
            print(f"[ingesta_continua] Error consumiendo la API: {e}")

        time.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    main()
