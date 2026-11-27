# Notas de trabajo · Encaminados por Jesús

Documento de referencia para mantener la web sin depender de carpetas locales. No contiene credenciales.

## Dónde está cada cosa

- **Web publicada:** https://enkmina2.github.io/encaminados-por-jesus/ (GitHub Pages, rama `main`, carpeta raíz).
- **Repositorio:** https://github.com/Enkmina2/encaminados-por-jesus
- **Contenido diario:** `datos/dias.json`. Cada entrada tiene fecha, tema, versículo, estudio, «para hoy», concordancia y `aprobado`.
- **Textos diarios de la web:** `index.html` (función `pintarDia` y `pintarDiaI18n`) y `pintarReflexion`, que rellena la sección «Reflexiones».
- **Noticias y vídeos:** `datos/noticias.json` y `datos/videos.json`, actualizados por `.github/workflows/actualizar.yml` dos veces al día.

## Cómo funciona el tema del día

1. La web toma la entrada cuya `fecha` es hoy, o la última anterior.
2. Solo muestra entradas con `"aprobado": true` (o sin el campo). Si una entrada tiene `"aprobado": false`, la web la salta.
3. La reflexión usa el mismo día: su versículo, su `resumen`, sus `parrafos` y su `para_hoy`. Si el día no tiene estudio, usa el último estudio disponible.
4. Las concordancias se muestran como «Pasajes relacionados» en la sección «Lectura bíblica» y en la reflexión.

## Cómo añadir días

- Escribe las entradas con el mismo formato que las existentes (copia la última).
- Los versículos deben tener el texto exacto de la Reina-Valera 1960. Compruébalo en BibleGateway antes de aprobar.
- Pon `"aprobado": false` hasta haber revisado el texto y los títulos.
- Después de revisar, cambia a `"aprobado": true`, haz commit y push a `main`.

## Tareas programadas (claude.ai)

- **«Hoy en el mundo»** (diaria, 19:43, Madrid): escribe la línea del día siguiente si la entrada existe y está vacía. Si la entrada no existe, no hace nada y no avisa.
- **«Estudios de la semana»** (sábados, 9:47, Madrid): debería preparar los 7 días siguientes. Desde el 7 de noviembre no tiene acceso de escritura al repositorio y falla antes de empezar.

Para revisar una tarea: claude.ai → tareas programadas → comprobar que tiene acceso de escritura a este repositorio. Para ver sus ejecuciones, usa el historial de la tarea en claude.ai.

## Pendientes conocidos

- Renovar el acceso de escritura de la tarea semanal.
- Revisar que los días del 5 de diciembre en adelante existan antes de cada fin de semana.
- Tienda `enkmina2shop.es`: verificar en Google Search Console (registro TXT en DonDominio).

## Concordancia del Nuevo Testamento

- `datos/concordancia-nt.json`: para cada versículo del Antiguo Testamento, hasta 5 pasajes del Nuevo Testamento que lo citan, cumplen o iluminan. Formato: `"Gen.28.12": ["Juan 1:51", ...]`.
- Origen: referencias cruzadas de openbible.info (licencia CC BY, https://www.openbible.info/labs/cross-references/). Ordenadas por votos y solo desde el Antiguo Testamento.
- No se filtra ningún pasaje por doctrina: los textos se explican en el estudio desde la unicidad (Dios manifestado en carne).
