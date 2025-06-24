import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from datetime import date
import sys

BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
env_path = os.path.join(BASE_PATH, ".env")

if not os.path.exists(env_path):
    with open(env_path, "w") as f:
        f.write("EMAIL_USER=\n")
        f.write("EMAIL_PASS=\n")
        f.write("SMTP_SERVER=\n")
        f.write("SMTP_PORT=465\n")
    print("Archivo .env generado. Completá tus credenciales antes de continuar.")
    sys.exit()

load_dotenv(env_path)
EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")

faltantes = []
if not EMAIL: faltantes.append("EMAIL_USER")
if not PASSWORD: faltantes.append("EMAIL_PASS")
if not SMTP_SERVER: faltantes.append("SMTP_SERVER")
if not SMTP_PORT: faltantes.append("SMTP_PORT")
if faltantes:
    print("\nLas siguientes variables faltan o están vacías en el .env:")
    for f in faltantes:
        print(f"- {f}")
    print("\nCompletá el archivo .env antes de continuar.")
    sys.exit()
SMTP_PORT = int(SMTP_PORT)

CLIENTES_DIR = os.path.abspath(os.path.join(BASE_PATH, "..", "..", "clientes"))
hoy = date.today().strftime("%Y-%m-%d")
clientes_a_enviar = []
errores_bloqueantes = []

for cliente in os.listdir(CLIENTES_DIR):
    ruta = os.path.join(CLIENTES_DIR, cliente)
    if not os.path.isdir(ruta):
        continue

    pdfs = [f for f in os.listdir(ruta) if f.lower().endswith(".pdf")]
    if not pdfs:
        continue

    email_path = os.path.join(ruta, "email.txt")
    if not os.path.exists(email_path):
        errores_bloqueantes.append(f"[FALTA] email.txt en {cliente}")
        continue

    with open(email_path, "r") as f:
        email_dest = f.read().strip()

    if not email_dest:
        errores_bloqueantes.append(f"[VACÍO] Completar email.txt en {cliente}")
        continue

    pdf_path = max([os.path.join(ruta, f) for f in pdfs], key=os.path.getmtime)
    clientes_a_enviar.append((cliente, ruta, pdf_path, email_dest))

# Verificar errores antes de continuar
if errores_bloqueantes:
    print("\n[ERROR] No se puede continuar. Se encontraron problemas con clientes:")
    for error in errores_bloqueantes:
        print(f" - {error}")
    print("\nSolucioná estos problemas en la carpeta clientes antes de continuar. ")
    print("(agregando su email o eliminando el PDF -> se omite el envio)\n")
    sys.exit()

print(f"\nSe enviarán {len(clientes_a_enviar)} factura(s). ¿Deseás continuar? (s/n): ", end="")
confirm = input().strip().lower()
if confirm != "s":
    print("Envío cancelado por el usuario.")
    sys.exit()

print("\nClientes que recibirán factura:")
for cliente, *_ in clientes_a_enviar:
    print(f"- {cliente.replace('_', ' ')}")

enviados = 0
for cliente, ruta, pdf_path, email_dest in clientes_a_enviar:
    msg = EmailMessage()
    msg["Subject"] = f"Factura - {cliente.replace('_', ' ')} ({hoy})"
    msg["From"] = EMAIL
    msg["To"] = email_dest
    msg.set_content(f"Buen día, {cliente.replace('_', ' ')},\n\nAdjuntamos la factura de honorarios correspondiente.\n\nSaludos cordiales.")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(pdf_path)
        )

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
            print(f"Enviado a {email_dest}")
            enviados += 1
    except Exception as e:
        print(f"No se pudo enviar a {email_dest}: {e}")

print(f"\nEnvío finalizado. Total enviados: {enviados} de {len(clientes_a_enviar)}.")
