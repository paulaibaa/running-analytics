# Permite guardar y leer los datos originales.
import json
import argparse
import hashlib
import shutil

# Permite identificar cada extracción con su fecha y hora.
from datetime import datetime, timezone

# Permite introducir la contraseña sin mostrarla.
from getpass import getpass

# Permite trabajar con rutas.
from pathlib import Path

# Permite preparar y validar las tablas.
import pandas as pd

# Permite conectarnos a Garmin.
from garminconnect import Garmin

# El dashboard utiliza el CSV preparado; no vuelve a consultar Garmin.
from generar_dashboard import generar_dashboard


# Campos que acordamos conservar durante la exploración.
columnas_conservar = [
    # Identificación, fechas, modalidad y récord personal.
    "activityId",
    "activityName",
    "startTimeLocal",
    "startTimeGMT",
    "activityType",
    "isPR",

    # Distancia, duración y velocidad.
    "distance",
    "duration",
    "elapsedDuration",
    "movingDuration",
    "averageSpeed",
    "maxSpeed",

    # Frecuencia cardiaca.
    "averageHR",
    "maxHR",

    # Desnivel y altitud.
    "elevationGain",
    "elevationLoss",
    "minElevation",
    "maxElevation",
    "avgElevation",

    # Cadencia y pasos.
    "averageRunningCadenceInStepsPerMinute",
    "maxRunningCadenceInStepsPerMinute",
    "steps",

    # Calorías y temperatura.
    "calories",
    "bmrCalories",
    "minTemperature",
    "maxTemperature",

    # Potencia.
    "avgPower",
    "maxPower",
    "normPower",

    # Efecto del entrenamiento.
    "aerobicTrainingEffect",
    "anaerobicTrainingEffect",
    "trainingEffectLabel",
    "aerobicTrainingEffectMessage",
    "anaerobicTrainingEffectMessage",

    # Dinámica de carrera.
    "avgStrideLength",
    "avgGroundContactTime",
    "avgVerticalOscillation",
    "avgVerticalRatio",

    # Tiempo en zonas de frecuencia cardiaca.
    "hrTimeInZone_1",
    "hrTimeInZone_2",
    "hrTimeInZone_3",
    "hrTimeInZone_4",
    "hrTimeInZone_5",

    # Tiempo en zonas de potencia.
    "powerTimeInZone_1",
    "powerTimeInZone_2",
    "powerTimeInZone_3",
    "powerTimeInZone_4",
    "powerTimeInZone_5",

    # Mejores tramos.
    "fastestSplit_1000",
    "fastestSplit_1609",
    "fastestSplit_5000",
    "fastestSplit_10000",
    "fastestSplit_21098",

    # VO₂ máximo.
    "vO2MaxValue"
]


# Garmin utilizará esta función si necesita el código de verificación.
def pedir_codigo():
    return input("Código de verificación de Garmin: ").strip()


# Pedimos las credenciales y devolvemos una conexión iniciada.
def conectar_garmin():
    email = input("Correo de Garmin: ").strip()
    password = getpass("Contraseña de Garmin: ")

    cliente = Garmin(
        email=email,
        password=password,
        prompt_mfa=pedir_codigo
    )

    cliente.login()
    print("Sesión iniciada correctamente.")

    return cliente


# Descargamos las actividades de running por páginas.
def extraer_carreras(cliente):
    tamano_pagina = 20
    inicio = 0
    carreras = []

    while True:
        # El nombre del argumento es activitytype, en minúsculas.
        pagina = cliente.get_activities(
            start=inicio,
            limit=tamano_pagina,
            activitytype="running"
        )

        # Terminamos cuando la consulta devuelve una lista vacía.
        if not pagina:
            break

        # Acumulamos las actividades y avanzamos a la siguiente página.
        carreras.extend(pagina)
        inicio = inicio + len(pagina)

        print("Carreras acumuladas:", len(carreras))

    return carreras


# Guardamos la respuesta original sin modificar sus campos.
def guardar_original(carreras, carpeta_raw):
    carpeta_raw.mkdir(parents=True, exist_ok=True)

    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_json = carpeta_raw / f"garmin_running_{marca_tiempo}.json"

    # El modo x evita sobrescribir un archivo existente.
    with ruta_json.open("x", encoding="utf-8") as archivo:
        json.dump(
            carreras,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    print("Original guardado:", ruta_json)
    return ruta_json


# Seleccionamos, validamos y transformamos los datos.
def preparar_carreras(carreras, columnas_conservar):
    # Evitamos generar un historial preparado vacío.
    if not carreras:
        raise ValueError("No se han recibido actividades para preparar.")

    # Convertimos la lista de diccionarios en una tabla.
    df_original = pd.DataFrame(carreras)

    # Comprobamos que existen los campos seleccionados.
    columnas_faltantes = []

    for columna in columnas_conservar:
        if columna not in df_original.columns:
            columnas_faltantes.append(columna)

    if columnas_faltantes:
        raise ValueError(
            f"Faltan columnas necesarias: {columnas_faltantes}"
        )

    # Creamos df antes de utilizarlo en las comprobaciones.
    df = df_original[columnas_conservar].copy()

    # Los identificadores deben estar presentes y ser únicos.
    if df["activityId"].isna().any():
        raise ValueError("Hay actividades sin identificador.")

    if df["activityId"].duplicated().any():
        raise ValueError("Hay identificadores de actividad repetidos.")

    # Limpiamos los extremos de los nombres.
    df["activityName"] = df["activityName"].str.strip()

    # Extraemos la modalidad del diccionario original.
    modalidades = []

    for tipo in df["activityType"]:
        modalidades.append(tipo["typeKey"])

    df["modalidad"] = modalidades

    # Convertimos el texto a fecha y hora local.
    df["fecha_local"] = pd.to_datetime(
        df["startTimeLocal"],
        format="%Y-%m-%d %H:%M:%S",
        errors="raise"
    )

    # Una fecha ausente también debe detener la preparación.
    if df["fecha_local"].isna().any():
        raise ValueError("Hay actividades sin fecha local.")

    # Revisamos los datos necesarios para calcular el ritmo.
    faltan_datos = df[["distance", "duration"]].isna().any().any()

    valores_no_positivos = (
        (df["distance"] <= 0) | (df["duration"] <= 0)
    ).any()

    if faltan_datos or valores_no_positivos:
        raise ValueError(
            "Hay distancias o duraciones ausentes, iguales a cero o negativas."
        )

    # Creamos las unidades derivadas antes de calcular el ritmo.
    df["distance_km"] = df["distance"] / 1000
    df["duration_min"] = df["duration"] / 60

    # Utilizamos el tiempo del cronómetro para calcular el ritmo.
    df["pace_min_km"] = df["duration_min"] / df["distance_km"]

    # La modalidad ya está representada como texto.
    df = df.drop(columns=["activityType"])

    return df


# Guardamos primero un temporal y comprobamos su lectura.
def guardar_preparado(df, carpeta_processed):
    carpeta_processed.mkdir(parents=True, exist_ok=True)

    ruta_final = carpeta_processed / "running_preparado.csv"
    ruta_temporal = carpeta_processed / "running_preparado_temporal.csv"

    # El historial definitivo todavía no se modifica.
    df.to_csv(
        ruta_temporal,
        index=False,
        encoding="utf-8"
    )

    comprobacion = pd.read_csv(
        ruta_temporal,
        parse_dates=["fecha_local"]
    )

    # Comparamos con la tabla nueva, no con el historial anterior.
    if comprobacion.shape != df.shape:
        raise ValueError(
            "El CSV guardado no conserva el tamaño de la tabla."
        )

    if not comprobacion.columns.equals(df.columns):
        raise ValueError(
            "El CSV guardado no conserva las columnas."
        )

    if not comprobacion["activityId"].equals(df["activityId"]):
        raise ValueError(
            "El CSV guardado no conserva los identificadores."
        )

    # Reemplazamos el definitivo tras superar las comprobaciones.
    ruta_temporal.replace(ruta_final)

    print("Historial preparado guardado:", ruta_final)
    return ruta_final


def copiar_a_docs(ruta_html, carpeta_docs):
    """Prepara una copia local para Pages. No ejecuta Git ni publica."""
    carpeta_docs.mkdir(parents=True, exist_ok=True)
    destino = carpeta_docs / "index.html"
    temporal = carpeta_docs / "index.html.tmp"
    shutil.copyfile(ruta_html, temporal)
    temporal.replace(destino)
    (carpeta_docs / ".nojekyll").touch()
    print("Copia local preparada en:", destino)
    print("No se ha publicado nada. Revisa la copia antes de hacer commit y push.")
    return destino


def guardar_metadatos(ruta_csv, ruta_json, inicio, fin, n_actividades):
    """Conserva cuándo se descargó el historial y a qué CSV corresponde."""
    metadatos = {
        "schema_version": 1,
        "extraction_started_at": inicio.isoformat(),
        "extraction_finished_at": fin.isoformat(),
        "raw_file": ruta_json.name,
        "prepared_file": ruta_csv.name,
        "activities": n_actividades,
        "csv_sha256": hashlib.sha256(ruta_csv.read_bytes()).hexdigest(),
    }
    destino = ruta_csv.with_suffix(".metadata.json")
    temporal = destino.with_suffix(".json.tmp")
    temporal.write_text(json.dumps(metadatos, ensure_ascii=False, indent=2), encoding="utf-8")
    temporal.replace(destino)
    return destino


def leer_opciones(argv=None):
    parser = argparse.ArgumentParser(description="Actualiza el historial y el dashboard local.")
    parser.add_argument(
        "--copiar-a-docs", action="store_true",
        help="Copia también el dashboard a docs/index.html, sin commit ni push."
    )
    return parser.parse_args(argv)


def main(argv=None):
    opciones = leer_opciones(argv)
    # Calculamos las rutas desde la ubicación del script.
    raiz_proyecto = Path(__file__).resolve().parent.parent
    carpeta_raw = raiz_proyecto / "data" / "raw"
    carpeta_processed = raiz_proyecto / "data" / "processed"

    # Conectamos y descargamos el historial.
    cliente = conectar_garmin()
    inicio_extraccion = datetime.now(timezone.utc)
    carreras = extraer_carreras(cliente)
    fin_extraccion = datetime.now(timezone.utc)

    # Conservamos los originales antes de preparar los datos.
    ruta_json = guardar_original(carreras, carpeta_raw)

    # Preparamos, validamos y guardamos el historial actualizado.
    df_preparado = preparar_carreras(carreras, columnas_conservar)
    ruta_csv = guardar_preparado(df_preparado, carpeta_processed)
    guardar_metadatos(ruta_csv, ruta_json, inicio_extraccion, fin_extraccion, len(df_preparado))

    # Regeneramos el HTML tras guardar y verificar el historial preparado.
    ruta_html = generar_dashboard(ruta_csv)

    # Esta opción solo copia archivos locales. GitHub permanece sin cambios.
    if opciones.copiar_a_docs:
        copiar_a_docs(ruta_html, raiz_proyecto / "docs")

    print(
        "Actualización terminada. Filas y columnas:",
        df_preparado.shape
    )


if __name__ == "__main__":
    main()
