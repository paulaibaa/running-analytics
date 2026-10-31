# Running Analytics

Proyecto personal de aprendizaje de Data Analytics y Data Science
a partir de mis entrenamientos de running.

## Objetivo

Construir un historial de entrenamientos actualizable desde Garmin
Connect y analizar cómo evoluciona mi entrenamiento a lo largo del tiempo.

## Fuente de datos

Garmin Connect será la fuente principal, ya que contiene mi historial
completo de actividades.

Exploraremos la extracción mediante la biblioteca no oficial
garminconnect de Python y comprobaremos qué datos proporciona.

## Unidad de análisis

Cada fila del historial representará una actividad de running registrada
en Garmin Connect, identificada por su ID único.

Conservaremos la modalidad de carrera para distinguir los distintos
tipos de entrenamiento.

La primera versión analizará resúmenes por actividad. Los datos de vueltas
y las mediciones dentro de cada carrera quedan para una ampliación posterior.

## Preguntas iniciales

- ¿Cómo evolucionan los kilómetros y la frecuencia de entrenamiento?
- ¿Cómo cambian la duración y el ritmo de las carreras?
- ¿Qué diferencias existen entre entrenamientos cortos y largos?
- ¿Cómo se relacionan el ritmo, la frecuencia cardiaca y el desnivel?

Las preguntas se ajustarán según la disponibilidad y calidad de los datos.

## Fases del proyecto

1. Definir el alcance y las preguntas de análisis.
2. Extraer y conservar los datos originales de Garmin.
3. Explorar su estructura, significado y calidad.
4. Diseñar un proceso de transformación y validación.
5. Almacenar el historial preparado.
6. Analizar los entrenamientos y presentar los resultados.

## Entregables previstos

- Un proceso reproducible de extracción y preparación.
- Un historial de carreras organizado y actualizable.
- Notebooks de exploración y análisis.
- Un informe visual con conclusiones y limitaciones.
- Un repositorio documentado.

## Estado actual

Definición del proyecto. La extracción desde Garmin todavía no está
implementada.
