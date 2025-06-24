import os
import shutil
import unicodedata
from datetime import date
import sys

BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
ORIGEN_FACTURAS = os.path.join(BASE_PATH, "..", "..", "facturas_nuevas")
CARPETAS_CLIENTES = os.path.join(BASE_PATH, "..", "..", "clientes")
pendientes_email = []
facturas_agregadas = 0

def normalizar(texto):
    texto = texto.upper().replace(" ", "_")
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto

# Crear carpeta 'clientes' si no existe
os.makedirs(CARPETAS_CLIENTES, exist_ok=True)

carpetas_map = {}
for carpeta in os.listdir(CARPETAS_CLIENTES):
    ruta = os.path.join(CARPETAS_CLIENTES, carpeta)
    if os.path.isdir(ruta):
        normalizado = normalizar(carpeta)
        carpetas_map[normalizado] = carpeta

for carpeta_real in carpetas_map.values():
    carpeta_path = os.path.join(CARPETAS_CLIENTES, carpeta_real)
    for file in os.listdir(carpeta_path):
        if file.lower().endswith(".pdf"):
            os.remove(os.path.join(carpeta_path, file))
            print(f"[LIMPIEZA] PDF eliminado: {carpeta_real}/{file}")

for archivo in os.listdir(ORIGEN_FACTURAS):
    if not archivo.lower().endswith(".pdf"):
        continue

    partes = archivo.split("_")
    if len(partes) < 2:
        print(f"[IGNORADO] Nombre inválido: {archivo}")
        continue

    nombre_cliente_raw = partes[-1].replace(".PDF", "").replace(".pdf", "").strip()
    nombre_cliente_normalizado = normalizar(nombre_cliente_raw)

    if nombre_cliente_normalizado in carpetas_map:
        carpeta_real = carpetas_map[nombre_cliente_normalizado]
    else:
        carpeta_real = nombre_cliente_normalizado
        ruta_nueva = os.path.join(CARPETAS_CLIENTES, carpeta_real)

        if os.path.exists(ruta_nueva) and not os.path.isdir(ruta_nueva):
            os.remove(ruta_nueva)

        os.makedirs(ruta_nueva, exist_ok=True)
        email_txt = os.path.join(ruta_nueva, "email.txt")
        with open(email_txt, "w") as f:
            pass
        print(f"[CREADO] Carpeta nueva: {carpeta_real} — completar email.txt")
        pendientes_email.append(carpeta_real)

    hoy = date.today().strftime("%Y-%m-%d")
    nombre_pdf = f"FACTURA {nombre_cliente_normalizado} - ({hoy}).pdf"
    carpeta_destino = os.path.join(CARPETAS_CLIENTES, carpeta_real)
    destino_pdf = os.path.join(carpeta_destino, nombre_pdf)
    origen_pdf = os.path.join(ORIGEN_FACTURAS, archivo)

    shutil.copy(origen_pdf, destino_pdf)
    print(f"[CLASIFICADO] {archivo} → {carpeta_real}")
    facturas_agregadas += 1

if pendientes_email:
    print("\n[ATENCIÓN] Clientes nuevos con email vacio:")
    for cliente in pendientes_email:
        print(f" - {cliente}")

print(f"\n[RESUMEN] Total de facturas cargadas: {facturas_agregadas}")

sys.exit()
