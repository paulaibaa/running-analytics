# Permite guardar y leer archivos JSON.
import json

# Permite incluir fecha y hora en el nombre del archivo.
from datetime import datetime

# Permite introducir la contraseña sin mostrarla.
from getpass import getpass

# Permite construir rutas a carpetas y archivos.
from pathlib import Path

# Permite crear la conexión con Garmin Connect.
from garminconnect import Garmin


# Localizamos la raíz del proyecto desde la ubicación del script.
# El primer parent llega a src; el segundo, a running-analytics.
raiz_proyecto = Path(__file__).resolve().parent.parent

# Definimos la carpeta de datos originales.
carpeta_raw = raiz_proyecto / "data" / "raw"

# Creamos la carpeta si falta, sin modificar su contenido si ya existe.
carpeta_raw.mkdir(parents=True, exist_ok=True)


# Pedimos las credenciales sin escribirlas en el código.
email = input("Correo de Garmin: ").strip()
password = getpass("Contraseña de Garmin: ")


# Esta función se ejecutará si Garmin solicita un código de verificación.
def pedir_codigo():
    return input("Código de verificación de Garmin: ").strip()


# Creamos el cliente con las credenciales y la función de verificación.
cliente = Garmin(
    email=email,
    password=password,
    prompt_mfa=pedir_codigo
)

# Iniciamos sesión.
cliente.login()
print("Sesión iniciada correctamente.")


# Definimos cuántas actividades pediremos por consulta.
tamano_pagina = 20

# Empezamos sin saltarnos ninguna actividad.
inicio = 0

# Preparamos la lista donde acumularemos las carreras.
carreras = []

# Consultamos páginas hasta recibir una vacía.
while True:
    pagina = cliente.get_activities(
        start=inicio,
        limit=tamano_pagina,
        activitytype="running"
    )

    # Una página vacía indica que no hay más actividades en la consulta.
    if not pagina:
        break

    # Añadimos las actividades recibidas a la lista acumulada.
    carreras.extend(pagina)

    # Avanzamos la posición para consultar la siguiente página.
    inicio = inicio + len(pagina)

    print("Carreras acumuladas:", len(carreras))

print("Extracción terminada:", len(carreras))


# Convertimos la fecha y hora del ordenador en texto para el nombre.
marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")

# La f permite insertar el valor de marca_tiempo entre las llaves.
ruta_salida = carpeta_raw / f"garmin_running_{marca_tiempo}.json"

# Creamos un archivo nuevo. El modo x impide sobrescribir uno existente.
with ruta_salida.open("x", encoding="utf-8") as archivo:
    json.dump(
        carreras,
        archivo,
        ensure_ascii=False,
        indent=2
    )


# Leemos el archivo para comprobar que se ha guardado correctamente.
with ruta_salida.open("r", encoding="utf-8") as archivo:
    carreras_guardadas = json.load(archivo)

# Mostramos el destino, el recuento y la comparación de contenidos.
print("Archivo guardado:", ruta_salida)
print("Actividades recuperadas:", len(carreras_guardadas))
print("¿El contenido coincide?", carreras_guardadas == carreras)