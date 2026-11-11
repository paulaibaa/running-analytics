# Running Analytics

Proyecto personal de aprendizaje de análisis de datos con entrenamientos reales
de Garmin Connect. Combina extracción, preparación, exploración y un dashboard
HTML local. Cada fila del historial preparado representa una actividad.

## Demo y código

- [Repositorio](https://github.com/paulaibaa/running-analytics)
- [Demo personal en GitHub Pages](https://paulaibaa.github.io/running-analytics/)

La demo muestra los entrenamientos de la autora y permite consultar o exportar
sus datos. Para reproducir el proyecto con otro historial, utiliza tu propia
cuenta de Garmin. No se publican credenciales ni sesiones de Garmin.

## Objetivo y preguntas

Analizar cómo evoluciona el entrenamiento de running:

- ¿Cómo cambian los kilómetros y la frecuencia por mes y semana?
- ¿Cómo se distribuyen distancia y duración, y cómo evoluciona la duración?
- ¿Qué diferencias descriptivas hay entre carreras cortas, medias y largas?
- ¿Qué contexto aportan el año, las pulsaciones y el ascenso al interpretar el ritmo?
- ¿Qué parte del volumen registrado corresponde a exterior y a cinta?

El análisis no demuestra mejoras fisiológicas ni efectos causales. Los ritmos
mensuales o las diferencias de pulsaciones no son, por sí solos, indicadores
concluyentes de progreso. Las métricas opcionales pueden faltar según reloj,
modalidad y periodo. Exterior y cinta se distinguen; la distancia en cinta se
ajusta según su pantalla, conforme al procedimiento de la autora.

## Qué funciona actualmente

- Descarga paginada de actividades de running mediante el cliente no oficial
  `garminconnect`, incluidas las modalidades que devuelve ese filtro.
- Conservación de cada extracción original en un JSON fechado.
- Selección de campos, limpieza de nombres, extracción de modalidad, conversión
  de fecha local y cálculo de kilómetros, minutos y ritmo del cronómetro.
- Comprobaciones de columnas, IDs, fechas y distancia/duración presentes y positivas.
- Guardado temporal y comprobación de tamaño, columnas e IDs antes de reemplazar
  `data/processed/running_preparado.csv`. No se comparan todas las celdas del CSV.
- Regeneración del dashboard al terminar la actualización del CSV.
- Notebooks de exploración, calidad y análisis descriptivo.

No hay base de datos SQL, modelos predictivos ni asistente de entrenamiento.
Tampoco hay un informe final cerrado con conclusiones ligado a una extracción.
Estas partes no se presentan como entregables terminados.

## Organización de archivos

| Archivo o carpeta | Responsabilidad |
|---|---|
| `src/actualizar_running.py` | Flujo principal: conexión, extracción, originales, preparación, validación y regeneración del dashboard. |
| `src/extraer_garmin.py` | Primera versión didáctica de extracción, conservada como referencia. Solo genera JSON: no es necesaria antes del actualizador. Se ejecuta directamente, no se importa como módulo. |
| `src/generar_dashboard.py` | Genera el HTML desde el CSV preparado; no conecta con Garmin. Expone `generar_dashboard()` para el flujo principal y un comando independiente. |
| `src/dashboard_template.html` | Código fuente de la interfaz. Contiene un marcador de datos, no el historial completo. Editar aquí para cambiar el diseño. |
| `notebooks/01_exploracion_garmin.ipynb` | Conexión, muestra, estructura, diccionario de datos y selección inicial. Es exploración de aprendizaje. |
| `notebooks/02_calidad_y_preparacion.ipynb` | Investigación y justificación de la preparación sobre una extracción histórica concreta. Sus rutas, ejemplos y cifras no se actualizan automáticamente. |
| `notebooks/03_analisis_running.ipynb` | Análisis del CSV actual: volumen mensual/semanal, distribuciones, duración, grupos de distancia, pulso, ascenso y cinta. |
| `data/raw/` | JSON originales locales, uno por extracción, y una muestra. |
| `data/processed/running_preparado.csv` | Único historial preparado actual. Se reconstruye completo en cada actualización. |
| `dashboard/running_dashboard.html` | Única salida HTML generada y actual para abrir o, si se decide, publicar. Contiene los datos incrustados. |
| `docs/04_inspeccion_dashboard.md` | Inspección histórica previa del dashboard, no un informe actualizado. Puede mostrar cifras de una extracción anterior. |
| `tests/test_actualizacion.py` | Pruebas locales de paginación y del flujo preparación → CSV → HTML, sin acceso a Garmin. |
| `tests/verificar_dashboard.cjs` | Pruebas de cálculos e interacciones del HTML con un DOM simulado y datos incrustados. |
| `requirements.txt` | Dependencias Python fijadas al entorno del proyecto. |
| `.gitignore` | Excluye entorno, datos, entregables personales generados y archivos habituales de sesión. No elimina archivos de commits anteriores. |

La guía antigua `GUIA_PASO_A_PASO.md` se ha eliminado para reconstruirla en otra etapa.
No es necesaria para ejecutar el proyecto.

## Instalación

Entorno de desarrollo: Python 3.14 en Windows, VS Code y extensión Jupyter.
Desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Seleccionar `.venv` como kernel en los notebooks. Node.js solo es necesario para
la prueba JavaScript; no para usar los scripts Python ni abrir el dashboard.
Las versiones fijadas documentan el entorno utilizado, no compatibilidad con
cualquier dispositivo, sistema o futura versión de Garmin.

## Actualizar el historial y el dashboard

```powershell
python src/actualizar_running.py
```

El programa pide las credenciales de la cuenta propia y, si Garmin lo requiere,
el código de verificación. Descarga el historial completo, conserva el JSON,
prepara el CSV y genera el HTML. No es una sincronización programada: hay que
ejecutar el comando cuando se quiera actualizar.

Abrir o recargar `dashboard/running_dashboard.html` después de terminar.
Una pestaña abierta no vuelve a leer el CSV automáticamente. Para el análisis,
reiniciar el kernel del notebook 03 y ejecutar todas sus celdas. No es necesario
repetir los notebooks 01 y 02 ni ejecutar el extractor anterior.

Si falla la preparación, no se reemplaza el CSV anterior. Si falla después la
regeneración del dashboard, el CSV puede estar actualizado y el HTML seguir
siendo antiguo: el error se muestra y se puede regenerar por separado.

## Regenerar solo el dashboard

```powershell
python src/generar_dashboard.py
```

También se pueden indicar archivos preparados compatibles:

```powershell
python src/generar_dashboard.py --input data/processed/running_preparado.csv --output dashboard/running_dashboard.html
```

La fuente es el CSV preparado, no una exportación CSV directa de la web de Garmin.
`steps` y las demás métricas proceden de los campos descargados de Garmin que
conserva el actualizador. El dashboard no consulta la cuenta: el generador lee
el CSV, convierte los valores e incrusta el resultado en el HTML. Los nulos se
conservan; los valores no positivos de pulso, cadencia y zancada se tratan como
ausentes en el generador.

Antes se generaban `running_dashboard.html` y `running_dashboard_v4.html` con
contenido idéntico. Se ha retirado el alias `_v4`; solo se genera el primero.
Los objetivos exportados se guardan por separado en JSON y pueden volver a
cargarse en una nueva generación del dashboard.

## Dashboard: alcance y límites

La interfaz incluye Resumen, Análisis, Objetivos, Mejores tiempos e Historial:

- Filtros de periodo, modalidad y distancia; tablas y detalle de actividades.
- Volumen, frecuencia, calendario y métricas disponibles de ritmo, pulso y técnica.
- Comparación descriptiva con el periodo anterior cuando hay cobertura.
- Mejores tramos Garmin y estimaciones identificadas desde sesiones cercanas
  a una distancia; no son récords oficiales.
- Creación, edición y exportación/importación de objetivos. Permanecen en memoria
  al usar la página; deben descargarse para conservarlos tras cerrarla.
- Exportación CSV de la selección. Publicar el HTML permite descargar sus datos.

El ritmo global es tiempo total del cronómetro dividido entre distancia total.
Las medias y sumas de métricas opcionales utilizan los valores presentes y muestran
cobertura. Los ceros de periodos sin sesiones no equivalen a métricas ausentes.
Los periodos iniciales/finales pueden ser parciales. Las zonas no incluyen límites
fisiológicos inventados y el cociente ritmo/pulso no es una prueba validada de eficiencia.

El archivo abre sin servidor. Los gráficos requieren conexión para cargar Chart.js
4.4.8 desde un CDN; no es una aplicación completamente autónoma sin Internet.
Sin esa biblioteca siguen disponibles las funciones que no dependen de sus gráficos.
Los metadatos incrustados registran generación y modificación de la fuente.

## Datos personales y credenciales

Los ejemplos, resultados y gráficos pertenecen a la autora. Para replicar el método,
cada persona debe utilizar su propia cuenta de Garmin y generar su historial.
Las contraseñas se solicitan con `getpass`; no deben escribirse como literales,
imprimirse ni guardarse en Git. Nunca publicar códigos de verificación ni tokens
u otros archivos de sesión. La biblioteca es no oficial y puede dejar de funcionar
si Garmin cambia sus servicios.

Los JSON, CSV y HTML generados permanecen ignorados por Git. La plantilla HTML,
el generador, las pruebas, notebooks y documentación son código fuente compartible
tras su revisión. Una publicación del HTML generado es una decisión separada:
contiene el historial y permite copiarlo. No existe protección que impida copiar
los datos visibles de una página pública. El correo de autor de los commits se
mantiene por decisión de la autora; no es una credencial de Garmin.

El código, notebooks, README y dependencias se comparten en el repositorio.
La demo pública es una copia explícita en `docs/index.html`. Los JSON y CSV
completos de trabajo permanecen excluidos de Git; los registros incrustados en
la demo sí se publican por decisión de la autora. No hay autenticación de Garmin
en GitHub Pages: es una web estática.

### Actualizar la demo publicada

La actualización local regenera `dashboard/running_dashboard.html`. Para publicar
esa nueva versión, revisarla y copiarla a la carpeta pública:

```powershell
Copy-Item dashboard/running_dashboard.html docs/index.html
# Preparar, revisar y guardar la nueva instantánea pública.
git add docs/index.html
git commit -m "Actualiza la demo de running"
git push
```

GitHub Pages publica la carpeta `/docs` de la rama `master`. La copia pública
no cambia hasta realizar este paso; ejecutar Python localmente no publica datos
por sí solo. `.nojekyll` permite servir el HTML estático sin procesamiento Jekyll.

## Comprobaciones

```powershell
python -m unittest discover -s tests -p "test_*.py"
node tests/verificar_dashboard.cjs
```

Las pruebas Python usan archivos temporales. La prueba JavaScript lee el HTML
generado y simula el DOM: valida cálculos, filtros, navegación, objetivos, detalle,
exportación y configuración de gráficos. No sustituye una prueba visual real.
En esta revisión no fue posible abrir archivos locales en el navegador integrado
por su política de seguridad; la revisión visual actual queda pendiente.

## Pendientes conocidos

- Validación visual en navegador de escritorio y móvil antes de publicar el HTML.
- Instalación y reproducción en un entorno nuevo; dependencias opcionales según Garmin.
- Adaptar campos opcionales para otros relojes: la preparación exige los campos seleccionados.
- Registrar explícitamente los metadatos de extracción; el notebook usa provisionalmente
  la modificación del CSV para identificar el periodo semanal abierto.
- Ampliar validaciones de datos y comprobación del contenido completo del CSV.
- Preparar un informe de cierre si se quiere una entrega con respuestas sintetizadas.
- Base de datos, modelos predictivos y asistente, solo como ampliaciones futuras.
