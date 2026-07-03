import requests
from conexion import conectar

NUM_REGISTROS = 500
API_URL = "https://randomuser.me/api/"

def crear_tabla(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.personas (
            id SERIAL PRIMARY KEY,
            nombre TEXT,
            email TEXT,
            direccion TEXT,
            telefono TEXT,
            fecha_nacimiento DATE,
            fecha_ingesta TIMESTAMP DEFAULT NOW()
        );
    """)

def obtener_personas(cantidad):
    respuesta = requests.get(API_URL, params={"results": cantidad, "nat": "es"}, timeout=10)
    respuesta.raise_for_status()
    return respuesta.json()["results"]

def main():
    conn = conectar()
    conn.autocommit = True
    cur = conn.cursor()
    crear_tabla(cur)

    personas = obtener_personas(NUM_REGISTROS)
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

    print(f"[ingesta_inicial] Se insertaron {len(personas)} registros desde randomuser.me en raw.personas")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
