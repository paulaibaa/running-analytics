# Instalación y uso paso a paso

Esta guía prepara una copia del proyecto con tu propio historial. Entorno utilizado: Windows, Python 3.14 y VS Code.

## 1. Preparar las herramientas

Instala Python desde su web oficial y VS Code. En VS Code instala las extensiones Python y Jupyter de Microsoft. Git permite descargar el repositorio y guardar cambios; Node.js solo se necesita para las pruebas JavaScript, no para utilizar el proyecto.

Abre una terminal en VS Code desde **Terminal → Nueva terminal**. Comprueba Python:

```powershell
python --version
```

## 2. Descargar y abrir el proyecto

Con Git instalado, ejecuta en la carpeta donde quieras guardar el proyecto:

```powershell
git clone https://github.com/paulaibaa/running-analytics.git
cd running-analytics
code .
```

También puedes descargar el ZIP desde GitHub, descomprimirlo y abrir la carpeta con **Archivo → Abrir carpeta**. La raíz es la carpeta que contiene `README.md`, `requirements.txt`, `src` y `notebooks`.

## 3. Crear un entorno virtual

Desde la terminal situada en esa raíz:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

El entorno virtual guarda las bibliotecas de este proyecto por separado. Si está activo, verás `(.venv)` al principio de la terminal.

Si PowerShell bloquea la activación, puedes continuar sin cambiar su configuración utilizando directamente el Python del entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Instalar las bibliotecas

Con el entorno activado:

```powershell
python -m pip install -r requirements.txt
```

`requirements.txt` enumera las bibliotecas y versiones utilizadas. Pandas prepara tablas, Matplotlib dibuja gráficos, ipykernel permite ejecutar notebooks y garminconnect conecta con Garmin mediante un cliente no oficial.

## 5. Descargar tu historial

Sincroniza primero el reloj con Garmin Connect. Después, desde la raíz:

```powershell
python src/actualizar_running.py
```

Si no activaste el entorno, sustituye `python` por `.\.venv\Scripts\python.exe`.

El programa pide correo, contraseña y, cuando Garmin lo solicita, un código de verificación. La contraseña no aparece al escribir. No añadas estas credenciales al archivo Python ni las pegues en capturas o notebooks.

La ejecución descarga el historial completo, conserva un JSON fechado en `data/raw`, valida y reemplaza `data/processed/running_preparado.csv`, guarda `running_preparado.metadata.json` y genera `dashboard/running_dashboard.html`.

Los metadatos conservan cuándo empezó y terminó la descarga en UTC. La huella del CSV permite comprobar que las fechas pertenecen a ese archivo. Una extracción antigua sin metadatos no recibe una fecha inventada. Si la preparación falla, no se reemplaza el CSV previo; si falla posteriormente el HTML, el CSV puede ser nuevo y el dashboard anterior.

## 6. Abrir el dashboard

En el explorador de archivos, abre `dashboard/running_dashboard.html` con un navegador. Los gráficos necesitan conexión a Internet para cargar Chart.js. Después de actualizar los datos, recarga la página.

Los objetivos creados en la interfaz permanecen en memoria: utiliza su descarga JSON y vuelve a cargarlos cuando los necesites.

## 7. Trabajar con los notebooks

Abre un `.ipynb` en VS Code y pulsa **Seleccionar kernel**. Elige Python de `.venv`. El kernel es el proceso que ejecuta las celdas.

Los notebooks 01 y 02 documentan el aprendizaje y decisiones sobre extracciones concretas. Para analizar el historial actualizado utiliza el 03: reinicia su kernel y ejecuta todas las celdas en orden. Actualizar el CSV no actualiza automáticamente las salidas que ya ves en un notebook.

## 8. Actualizaciones posteriores

Ejecuta de nuevo el actualizador cuando quieras incorporar actividades. No necesitas instalar otra vez las bibliotecas ni repetir los notebooks 01 y 02.

Si además quieres dejar preparada la copia que utiliza GitHub Pages, utiliza **en lugar del comando habitual**:

```powershell
python src/actualizar_running.py --copiar-a-docs
```

Hace la descarga y preparación habituales y después copia el HTML generado a `docs/index.html`. Reemplaza esa copia local; no ejecuta Git ni publica. Revisa el archivo antes de decidir subirlo. No hace falta ejecutar los dos comandos seguidos.

La web configurada en este repositorio utiliza la carpeta `/docs` de la rama `master`. Para un repositorio propio debes configurar tu propio GitHub Pages. El HTML contiene los registros incrustados: al publicarlo permites que otras personas los copien.

## 9. Comprobaciones y problemas habituales

Para comprobar el código sin conectar con Garmin:

```powershell
python -m unittest discover -s tests -p "test_*.py"
node tests/verificar_dashboard.cjs
```

- **No encuentra `src/actualizar_running.py`:** sitúa la terminal en la raíz del proyecto, no en `notebooks` ni en `src`.
- **No encuentra una biblioteca:** comprueba que estás utilizando el Python de `.venv` y que instalaste `requirements.txt`.
- **No encuentra el CSV:** ejecuta primero el actualizador con tu cuenta.
- **Error de autenticación:** revisa las credenciales y el código solicitado. El cliente es no oficial y puede fallar si Garmin modifica el servicio.
- **Error de columnas o validación:** conserva el mensaje y revisa la extracción antes de cambiar datos; el script detiene la preparación cuando no se cumplen sus comprobaciones.
- **HTML antiguo:** comprueba qué copia abriste. `dashboard` es la local; `docs` solo cambia con la opción de copia. La web pública requiere publicar después en GitHub.
- **Gráficos ausentes:** comprueba Internet y si el navegador ha bloqueado la carga de Chart.js.

No subas a Git credenciales, tokens ni archivos de sesión. Los datos de trabajo están ignorados; `docs/index.html` es una excepción pública deliberada.
