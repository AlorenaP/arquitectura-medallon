import requests
from conexion import conectar

REGISTROS_POR_LOTE = 5
API_URL = "https://randomuser.me/api/"

def obtener_personas(cantidad):
    r = requests.get(API_URL, params={"results": cantidad, "nat": "es"}, timeout=10)
    r.raise_for_status()
    return r.json()["results"]

def main():
    conn = conectar()
    conn.autocommit = True
    cur = conn.cursor()
    personas = obtener_personas(REGISTROS_POR_LOTE)
    for p in personas:
        nombre = f"{p['name']['first']} {p['name']['last']}"
        direccion = f"{p['location']['street']['name']} {p['location']['street']['number']}, {p['location']['city']}, {p['location']['country']}"
        fecha_nacimiento = p["dob"]["date"][:10]
        cur.execute(
            "INSERT INTO raw.personas (nombre, email, direccion, telefono, fecha_nacimiento) VALUES (%s, %s, %s, %s, %s)",
            (nombre, p["email"], direccion, p["phone"], fecha_nacimiento),
        )
    print(f"[ingesta_continua] Insertado lote de {len(personas)} registros")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
