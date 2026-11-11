# Running Analytics

Proyecto personal para analizar la evolución de entrenamientos reales de Garmin Connect: extracción, preparación, análisis con Python y dashboard HTML.

[Demo pública](https://paulaibaa.github.io/running-analytics/) · [Instalación paso a paso](docs/INSTALACION.md)

Los datos y gráficos de la demo pertenecen a la autora. Para reproducir el proyecto, utiliza tu propia cuenta de Garmin. El HTML contiene datos que pueden copiarse y exportarse; no contiene credenciales de Garmin.

## Qué está implementado

- Descarga paginada del historial de running con la biblioteca no oficial `garminconnect`.
- Conservación de originales JSON, preparación y validación de un CSV actual.
- Registro de las fechas de inicio y fin de extracción, en UTC, junto al CSV.
- Exploración, calidad y análisis descriptivo mediante notebooks.
- Dashboard con filtros, volumen, frecuencia, distribuciones, pulso, técnica, objetivos, mejores tiempos e historial exportable.

El análisis distingue exterior y cinta. Estudia volumen mensual y semanal, distancia y duración, grupos de distancia y contexto de ritmo, pulso y ascenso. Las comparaciones son descriptivas: no demuestran causalidad ni mejoras fisiológicas. El trabajo analítico está en pausa; no hay informe final cerrado, modelos predictivos, base de datos SQL ni asistente.

## Archivos del proyecto

| Archivo | Para qué sirve |
|---|---|
| `notebooks/01_exploracion_garmin.ipynb` | Aprender la conexión, explorar una muestra y documentar los campos. |
| `notebooks/02_calidad_y_preparacion.ipynb` | Investigar calidad y justificar la preparación sobre una extracción histórica. |
| `notebooks/03_analisis_running.ipynb` | Analizar el CSV preparado actual. Se actualiza reiniciando el kernel y ejecutando todas las celdas. |
| `src/actualizar_running.py` | Descargar, conservar originales, preparar, validar y generar el dashboard. |
| `src/extraer_garmin.py` | Extractor inicial didáctico; no hace falta ejecutarlo antes del actualizador. |
| `src/generar_dashboard.py` | Generar el HTML desde el CSV, sin conectar con Garmin. |
| `src/dashboard_template.html` | Plantilla de la interfaz; aquí se modifica el diseño. |
| `data/raw/` | Originales JSON locales, uno por extracción. |
| `data/processed/running_preparado.csv` | Historial preparado, reconstruido completo en cada actualización. |
| `data/processed/running_preparado.metadata.json` | Fechas de extracción, nombres de archivos, número de actividades y huella del CSV. |
| `dashboard/running_dashboard.html` | Dashboard local generado con los datos incrustados. |
| `docs/index.html` | Copia elegida para GitHub Pages. |
| `tests/` | Comprobaciones del flujo de actualización y las interacciones del dashboard. |
| `requirements.txt` | Dependencias Python del proyecto. |

Los notebooks 01 y 02 conservan su propósito didáctico y no se ejecutan en cada actualización. La antigua guía se sustituyó por la [guía de instalación](docs/INSTALACION.md).

## Actualización habitual

Desde la raíz del proyecto, con el entorno activado:

```powershell
python src/actualizar_running.py
```

Actualiza los datos y `dashboard/running_dashboard.html`. Para hacer lo mismo **y copiar además el HTML a `docs/index.html`**, utiliza en su lugar:

```powershell
python src/actualizar_running.py --copiar-a-docs
```

Esta opción reemplaza la copia local de `docs/index.html`. No hace commit ni push: la web pública solo cambiará cuando publiques esos cambios en GitHub. No es necesario ejecutar ambos comandos.

Para regenerar únicamente el HTML desde el CSV existente:

```powershell
python src/generar_dashboard.py
```

Después, recarga el HTML abierto. Los pasos y las métricas proceden del CSV preparado; el dashboard no consulta Garmin. Los objetivos creados en la página deben descargarse como JSON para conservarlos.

## Fechas y límites

Los metadatos de extracción se crean desde la próxima descarga y se incrustan en el HTML si corresponden al mismo CSV. No se inventan fechas para archivos antiguos. La fecha de generación del HTML y la modificación del CSV son conceptos distintos. El notebook 03 conserva provisionalmente su criterio anterior basado en la modificación del CSV; no se ha cambiado durante la pausa analítica.

El HTML abre sin servidor, pero sus gráficos necesitan Internet para cargar Chart.js. Los valores ausentes no se interpretan como cero. Las comparaciones entre periodos dependen de su cobertura y de las métricas disponibles.

La [revisión visual](docs/REVISION_VISUAL.md) registra las comprobaciones de escritorio y las limitaciones observadas en móvil.

## Privacidad y comprobaciones

Los originales, CSV, entorno virtual y archivos de sesión están excluidos de Git. La copia de `docs/index.html` sí contiene el historial publicado. El correo y la contraseña de Garmin se solicitan al ejecutar el programa; no se escriben en el código ni en la documentación. Nunca publiques contraseñas, códigos de verificación ni tokens. El correo de autor de los commits es independiente del acceso a Garmin.

```powershell
python -m unittest discover -s tests -p "test_*.py"
node tests/verificar_dashboard.cjs
```

Las pruebas Python usan archivos temporales y no conectan con Garmin. Las de JavaScript simulan el DOM; complementan la revisión visual. La reproducción completa en una instalación nueva no se ha verificado.
