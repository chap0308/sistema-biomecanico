# Guion sincronizado de la presentacion tecnica del sistema

## 1. Proposito

Este archivo mantiene la trazabilidad entre la presentacion, la demostracion web y la evidencia tecnica del caso `dev_valgo_izq_002`. La presentacion explica el razonamiento; la web permite verificarlo sobre el video y sus datos; los CSV, JSON, imagenes y videos overlay conservan la evidencia reproducible.

La exposicion debe responder una pregunta central:

> Como transforma el sistema un video frontal de una sentadilla en mediciones y clasificaciones que otra persona puede revisar y discutir?

## 2. Convenciones de exposicion

- **PPT:** comunica el problema, la logica, las formulas y las decisiones metodologicas.
- **Web:** demuestra la sincronizacion entre video, fotograma, senal, geometria y regla.
- **Artefactos:** permiten auditar el resultado sin depender de la interfaz.
- **Alcance:** el sistema mide compensaciones observables; no diagnostica patologias ni infiere su causa anatomica.
- **Caso conductor:** repeticion 3 de `dev_valgo_izq_002`, maxima profundidad en el fotograma 592 (`24.63 s`).

## 3. Secuencia de diapositivas

### Diapositiva 1. Del video a una decision auditable

**Mensaje visible:**

Sistema de vision por computadora para detectar compensaciones observables durante la sentadilla bilateral.

**Guion:**

La contribucion no consiste solamente en dibujar puntos sobre un video. El sistema conserva una cadena verificable: detecta puntos, controla su calidad, identifica cada repeticion, calcula geometria y aplica criterios interpretables. Cada resultado puede rastrearse hasta un fotograma y una formula.

**Evidencia:** captura de maxima profundidad con overlay.

### Diapositiva 2. Ver no equivale a medir

**Mensaje visible:**

Una compensacion evidente puede observarse a simple vista; el problema cientifico es medirla de forma repetible, explicable y comparable.

**Guion:**

La observacion humana sigue siendo la referencia del estudio, pero puede variar entre evaluadores. El sistema aporta valores, direccion, instante de medicion y trazabilidad. La pregunta no es si alguien puede notar que una rodilla entra, sino si el procedimiento produce la misma definicion, unidad y regla para todos los casos.

### Diapositiva 3. Cadena de transformacion

**Mensaje visible:**

Video -> pose 2D -> senal temporal -> variables biomecanicas -> reglas -> comparacion experta.

**Guion:**

Explicar las fases 2 a 5 como una cadena. Una fase no puede compensar el fallo de la anterior: si la pose no es estable, la repeticion no debe alimentar las formulas; si no existe una repeticion valida, no existe clasificacion biomecanica defendible.

**Conexion web:** mostrar brevemente las cuatro pestanas de trazabilidad: Pose 2D, Segmentacion, Variables y Reglas.

### Diapositiva 4. Responsabilidad de cada tecnologia

**Mensaje visible:**

- OpenCV: lectura, metadatos, fotogramas y video overlay.
- MediaPipe Pose: coordenadas normalizadas y visibilidad de la pose 2D.
- pandas y NumPy: series temporales, limpieza, estadistica y geometria.
- Conceptos de SciPy: maximos locales, distancia y prominencia.
- Matplotlib: evidencia grafica exportable.
- FastAPI y Next.js: contrato de datos y explicacion interactiva.

**Guion:**

SciPy sirve como referencia conceptual para prominencia, pero el prototipo implementa su propia deteccion equivalente y trazable. La interfaz no vuelve a calcular los resultados: presenta el contrato generado por el backend.

### Diapositiva 5. De 33 puntos a 13 referencias relevantes

**Mensaje visible:**

El sistema conserva nariz, hombros, caderas, rodillas, tobillos, talones y puntas de pie.

**Guion:**

MediaPipe devuelve mas puntos, pero el analisis frontal necesita 13 referencias. Un fotograma es analiticamente elegible cuando los puntos criticos requeridos superan la confianza minima y la calidad global cumple el criterio. La evidencia combina el overlay, `landmarks.csv` y el resumen por fotograma de `frame_quality.csv`.

**Conexion web:** pestana Pose 2D; mover el video y mostrar el cursor sincronizado.

### Diapositiva 6. La cadera convierte el movimiento en una senal

**Mensaje visible:**

`hip_midpoint_y = (y_cadera_izquierda + y_cadera_derecha) / 2`

**Guion:**

En una imagen el origen esta arriba a la izquierda y el eje Y crece hacia abajo. Por ello, cuando la persona desciende, `hip_midpoint_y` aumenta. En reposo el punto medio aparece mas arriba; en maxima profundidad alcanza un maximo local. La senal no representa fuerza ni angulo articular: representa posicion vertical normalizada en el plano de la imagen.

**Evidencia:** capturas del fotograma 474 y 592 conectadas con sus posiciones sobre la curva.

### Diapositiva 7. Antes de buscar repeticiones se limpia la senal

**Mensaje visible:**

Hueco aislado -> interpolacion temporal. Salto puntual -> mediana movil. Vibracion residual -> promedio movil.

**Guion:**

La interpolacion temporal estima una muestra faltante entre dos observaciones conocidas. No convierte un fotograma deficiente en valido; `valid_for_analysis` conserva la decision de calidad. La mediana de cinco fotogramas elimina valores atipicos y el promedio de cinco fotogramas suaviza cambios pequenos. La ventana equivale aproximadamente a `0.2 s` para este video.

**Formula:**

`y(t) = y_a + ((t - t_a) / (t_b - t_a)) x (y_b - y_a)`

**Evidencia:** figura `01_limpieza_interpolacion_suavizado.png`.

### Diapositiva 8. Prominencia: cuanto sobresale una profundidad

**Mensaje visible:**

`prominencia(p) = senal(p) - max(base_izquierda, base_derecha)`

**Guion:**

Un maximo local no basta: una oscilacion pequena tambien puede ser un maximo. La prominencia mide cuanto sobresale el candidato respecto de la base lateral mas alta. El umbral es adaptativo: `max(0.03, 0.18 x rango_robusto)`. Para este caso, el rango robusto fue `0.17472` y el minimo `0.03145`. Las tres profundidades aceptadas obtuvieron `0.06266`, `0.06623` y `0.08787`.

**Evidencia:** figura `02_prominencia_picos_reales.png`.

### Diapositiva 9. La recuperacion evita contar una pausa como otra sentadilla

**Mensaje visible:**

Tiempo separado no implica una nueva repeticion; tambien debe existir recuperacion vertical suficiente.

**Guion:**

En el caso de error, dos candidatos estaban separados `2.002 s`, pero entre ellos la persona solo recupero `0.000204`, muy por debajo de `0.03`. El algoritmo anterior conto cuatro repeticiones. La validacion actual fusiona los candidatos cuando el valle intermedio no recupera al menos la prominencia minima y conserva el pico mas profundo.

**Evidencia:** figura `03_error_doble_pico_recuperacion.png`.

### Diapositiva 10. De los picos a las fases de cada ejecucion

**Mensaje visible:**

Reposo -> inicio del descenso -> maxima profundidad -> ascenso -> cierre.

**Guion:**

La maxima profundidad es el pico aceptado. A ambos lados se buscan regiones de retorno hacia la posicion alta para delimitar inicio y cierre. Descenso y ascenso son los intervalos anterior y posterior al pico. La segmentacion produce para la repeticion 3: inicio en el fotograma 474, profundidad en 592 y final en 621.

**Conexion web:** pestana Segmentacion; seleccionar la repeticion 3 y recorrer inicio, profundidad y final.

### Diapositiva 11. `W0` convierte distancias de imagen en proporciones corporales

**Mensaje visible:**

`W0 = mediana del ancho de hombros en los fotogramas iniciales validos`

**Guion:**

Los grados ya son independientes de la escala, pero una distancia horizontal en coordenadas normalizadas sigue dependiendo del tamano aparente de la persona. Dividir entre `W0` expresa el desplazamiento como porcentaje de una referencia corporal relativamente estable. En este caso, `W0 = 0.258264` del ancho de la imagen, aproximadamente `123.45 px` en un video de 478 px de ancho.

**Advertencia:** `W0` es una referencia inicial; no es el ancho instantaneo de hombros en maxima profundidad.

### Diapositiva 12. Dos preguntas geometricas distintas

**Mensaje visible:**

- Inclinacion del tronco: orientacion respecto de la vertical, en grados.
- Desplazamiento de pelvis: traslacion lateral corregida respecto de los tobillos, en `% de W0`.

**Guion:**

El tronco usa `atan2(delta_x, delta_y)` porque la pregunta es cuanto se inclina un segmento. La pelvis compara el centro de caderas con el centro de tobillos y resta el offset inicial porque la pregunta es cuanto se traslado lateralmente la pelvis durante la ejecucion. Son magnitudes distintas, por eso no comparten unidad.

**Resultados R3:** tronco `12.38 grados`; pelvis `9.55 % de W0`.

### Diapositiva 13. Alineacion cadera-rodilla-tobillo

**Mensaje visible:**

La interpolacion espacial estima donde deberia cruzar la rodilla el eje cadera-tobillo a la misma altura vertical.

**Guion:**

Para cada lado se toman cadera `H`, rodilla real `K` y tobillo `A`. Primero se calcula la proporcion vertical `t = (Ky - Hy) / (Ay - Hy)`. Luego se interpola `Kx_esperado = Hx + t(Ax - Hx)`. La diferencia `Kx_real - Kx_esperado`, orientada hacia medial y dividida entre `W0`, produce la desviacion porcentual. Esta interpolacion es espacial y ocurre dentro de un solo fotograma; no debe confundirse con la interpolacion temporal usada para completar la senal.

**Ejemplo R3 izquierda:**

- `H=(0.607777, 0.750241)`
- `K=(0.544360, 0.812981)`
- `A=(0.621215, 0.869815)`
- `t=0.524693`
- `Kx_esperado=0.614828`
- desviacion medial `= 27.29 % de W0`

**Resultado bilateral:** izquierda `27.29 %`, derecha `-37.39 %`; diferencia absoluta `64.67 %`.

### Diapositiva 14. Medir no es todavia clasificar

**Mensaje visible:**

Cada variable conserva valor, direccion, unidad, regla y estado: ausente, no concluyente o presente.

**Guion:**

Los umbrales actuales son provisionales y existen para construir y probar el prototipo. Cada patron se evalua de forma independiente, por lo que una repeticion puede contener varias compensaciones. La evaluacion final de desempeno compara la salida del sistema con la referencia experta mediante exactitud, precision, sensibilidad, especificidad, F1-score y concordancia.

**Conexion web:** pestanas Variables y Reglas; mostrar el mismo valor en la geometria, la tabla y la clasificacion.

### Diapositiva 15. Demostracion auditable en la web

**Mensaje visible:**

Video, cursor temporal, fotograma, coordenadas, formula y clasificacion deben contar la misma historia.

**Guion de demostracion:**

1. Seleccionar la repeticion 3.
2. En Pose 2D, confirmar calidad y disponibilidad de puntos.
3. En Segmentacion, ubicar el fotograma 592 como maxima profundidad.
4. En Variables, seleccionar alineacion cadera-rodilla-tobillo y mostrar las coordenadas y la interpolacion espacial.
5. En Reglas, comprobar como el valor entra en la banda correspondiente.
6. Descargar los artefactos tecnicos para evidenciar reproducibilidad.

### Diapositiva 16. Que demuestra el sistema

**Mensaje visible:**

El sistema hace medible y auditable una observacion; no reemplaza una evaluacion clinica.

**Guion:**

Demuestra deteccion de pose 2D, segmentacion de ejecuciones, calculo de variables observables y aplicacion transparente de reglas. No determina por si solo la causa de una compensacion, una patologia ni un tratamiento. Su validez debe estimarse frente a evaluadores expertos y bajo el protocolo frontal definido.

## 4. Correspondencia PPT-web-artefactos

| Tema | PPT | Web | Artefacto principal |
|---|---|---|---|
| Pose y calidad | 5 | Pose 2D | `overlay.mp4`, `landmarks.csv`, `frame_quality.csv` |
| Senal de cadera | 6 | Segmentacion | `segmentation_frames.csv` |
| Limpieza | 7 | Segmentacion, detalle metodologico | `01_limpieza_interpolacion_suavizado.png` |
| Prominencia | 8 | Segmentacion, detalle metodologico | `02_prominencia_picos_reales.png` |
| Recuperacion | 9 | Segmentacion, detalle metodologico | `03_error_doble_pico_recuperacion.png` |
| Fases | 10 | Segmentacion | `repetitions.csv`, capturas de eventos |
| `W0` | 11 | Variables | `biomechanical_summary.json` |
| Tronco y pelvis | 12 | Variables | `biomechanical_frame_metrics.csv` |
| Rodilla | 13 | Variables, geometria | `peak_rep_3.png`, contrato explicativo |
| Reglas | 14 | Reglas | `criteria_summary.json` |

## 5. Preguntas previsibles y respuesta breve

### Por que no usar solo el fotograma de maxima profundidad para detectar repeticiones?

Porque primero debe conocerse donde empieza y termina cada ejecucion. La senal completa permite distinguir repeticiones, pausas y recuperaciones.

### Por que interpolar si un fotograma fue deficiente?

La interpolacion conserva continuidad para procesar la senal, pero no cambia el indicador original de calidad ni convierte ese fotograma en evidencia valida.

### Prominencia significa confianza del modelo?

No. Es una propiedad geometrica de una senal unidimensional: cuanto sobresale un pico respecto de sus bases laterales.

### Por que hay grados y porcentajes?

Los grados describen orientacion; los porcentajes describen distancias normalizadas respecto de `W0`. Responden preguntas geometricas diferentes.

### Por que usar interpolacion lineal para la rodilla?

Porque se necesita localizar el punto del segmento cadera-tobillo que tiene la misma coordenada vertical que la rodilla y comparar su coordenada horizontal con la rodilla real.

### Los umbrales son clinicos?

No. Son criterios provisionales del prototipo que deben calibrarse y validarse frente a referencia experta.

## 6. Fuentes tecnicas para la exposicion

- MediaPipe Pose Landmarker: deteccion y coordenadas de pose 2D.
- OpenCV: lectura y procesamiento de video.
- pandas `Series.interpolate`: interpolacion de valores faltantes.
- SciPy `find_peaks` y `peak_prominences`: fundamento de maximos locales, distancia y prominencia.
- Documentacion tecnica del caso `dev_valgo_izq_002` y artefactos generados por el pipeline.

