# Guion sincronizado de la presentación técnica

## Propósito

Explicar a un público no especializado cómo el sistema transforma un video frontal de sentadilla bilateral en mediciones interpretables y auditables. La presentación resume conceptos y decisiones; la aplicación web conserva la evidencia interactiva y los artefactos descargables.

## Caso conductor

- Caso: `dev_valgo_izq_002`.
- Repetición principal: repetición 3.
- Máxima profundidad: fotograma 592, aproximadamente `24.63 s`.
- Evidencia principal: `overlay.mp4`, `frame_quality.csv`, `frame_phases.csv`, `biomechanical_frame_metrics.csv`, `repetitions.csv` y capturas de eventos.

## Dirección visual

- Fondo marfil, texto azul petróleo, acentos turquesa, ámbar y coral.
- Una pregunta y una conclusión por diapositiva.
- Los datos reales se distinguen de las demostraciones controladas.
- Las fórmulas se muestran únicamente cuando explican una decisión del algoritmo.

## Diapositiva 1. Del video a una decisión auditable

**Mensaje visible:** Sistema de visión por computadora para analizar compensaciones observables durante la sentadilla bilateral.

**Guion:** El aporte no consiste solamente en dibujar puntos sobre una persona. El sistema conserva una cadena verificable desde el fotograma original hasta la variable calculada, la regla aplicada y la clasificación obtenida.

**Evidencia:** fotograma de máxima profundidad con superposición de pose.

## Diapositiva 2. Observar no equivale a medir

**Mensaje visible:** Una observación humana puede reconocer un patrón; el sistema debe cuantificarlo, repetirlo y dejar evidencia.

**Guion:** Decir que el tronco se inclina o que una rodilla se desplaza medialmente puede ser sencillo cuando el movimiento es notorio. La dificultad técnica está en definir referencias, controlar la calidad, localizar la ejecución correcta, calcular una magnitud comparable y documentar por qué se asignó una clasificación.

## Diapositiva 3. Cinco transformaciones, una misma evidencia

**Mensaje visible:** Video → pose 2D → señal temporal → geometría → regla interpretable.

**Guion:** OpenCV decodifica el video; MediaPipe estima puntos y visibilidad; pandas organiza e interpola la señal; NumPy y funciones propias calculan la segmentación y la geometría; OpenCV y Matplotlib producen evidencia visual; openpyxl genera los libros normalizados; FastAPI publica el informe y Next.js permite recorrerlo. SciPy sirve como referencia teórica para prominencia, pero el pipeline actual no lo invoca directamente.

**Conexión web:** vista general del caso y pestañas Pose 2D, Segmentación, Variables y Reglas.

## Diapositiva 4. Los resultados no aparecen por arte de magia

**Mensaje visible:** Los datos canónicos alimentan productos distintos sin alterar la evidencia original.

**Guion:** MediaPipe no genera directamente un video, una gráfica o un Excel. El pipeline guarda primero coordenadas, visibilidad, calidad, fases y métricas en CSV y JSON. Después, OpenCV dibuja puntos, líneas, textos y pixelado sobre cada fotograma; Matplotlib convierte series y métricas en gráficos PNG; openpyxl compone tablas, encabezados, formatos y leyendas en Excel; FFmpeg transforma el video intermedio en H.264 compatible con navegadores.

**Flujo visible:** `MediaPipe → CSV/JSON canónicos → OpenCV/Matplotlib/openpyxl → MP4/PNG/XLSX`.

**Aclaración:** Las tablas normalizadas son derivados de presentación. Los CSV y JSON canónicos permanecen disponibles para reproducir los cálculos.

## Diapositiva 5. Tres niveles que no deben confundirse

**Mensaje visible:** Fotograma decodificado ≠ pose válida ≠ repetición válida.

**Guion:** OpenCV informa si pudo leer un fotograma. MediaPipe entrega coordenadas y visibilidad. La regla del sistema exige coordenadas finitas y disponibilidad suficiente de referencias anatómicas. Una repetición solo puede clasificarse si su intervalo y su fotograma de máxima profundidad cumplen los criterios de calidad.

**Fórmulas:**

- `procesados (%) = 100 × fotogramas decodificados / fotogramas declarados`.
- `válidos (%) = 100 × fotogramas con pose válida / fotogramas decodificados`.
- `calidad global recomendada = válidos (%) ≥ 95 %`.

## Diapositiva 6. De 33 puntos a 13 referencias útiles

**Mensaje visible:** El modelo estima 33 puntos; el análisis conserva 13 y exige 8 referencias críticas.

**Guion:** Se utilizan nariz, hombros, caderas, rodillas, tobillos, talones y puntas de pie. Para aceptar un fotograma deben existir las ocho referencias centrales de hombros, caderas, rodillas y tobillos, además de una referencia distal por pie. Un punto es utilizable si sus coordenadas `x` e `y` son finitas y su visibilidad es al menos `0.50`.

**Aclaración:** La visibilidad crítica mínima es el menor valor efectivo entre los ocho puntos centrales; no es un promedio.

## Diapositiva 7. La cadera convierte el movimiento en una señal

**Mensaje visible:** `hip_midpoint_y = (y_cadera_izquierda + y_cadera_derecha) / 2`.

**Guion:** En las coordenadas de imagen, el origen está arriba a la izquierda y `y` aumenta hacia abajo. Por eso, cuando la persona desciende, la señal vertical del centro de caderas aumenta. Esta señal no representa fuerza ni ángulo articular: representa posición vertical normalizada en el tiempo.

**Evidencia:** fotograma de reposo, fotograma de máxima profundidad, su posición sobre la curva y el clip `senal_caderas_animada.mp4` construido con `frame_phases.csv`.

## Diapositiva 8. Una fórmula, dos interpolaciones distintas

**Mensaje visible:** Interpolar significa estimar un punto intermedio entre dos referencias conocidas.

**Fórmula general:** `q = q₁ + ((u - u₁)/(u₂ - u₁)) × (q₂ - q₁)`.

**Guion:** En la interpolación temporal, `u` es el tiempo o índice de fotograma y `q` es `hip_midpoint_y`; se usa para cubrir huecos breves de la señal. En la interpolación espacial, `u` es la coordenada vertical `y` y `q` es la coordenada horizontal `x`; se usa dentro del fotograma de máxima profundidad para estimar dónde el eje cadera–tobillo cruza la altura de la rodilla. La misma relación lineal responde a dos problemas diferentes.

**Aclaración:** La interpolación temporal no reemplaza las coordenadas anatómicas que se usan para calcular las variables biomecánicas.

## Diapositiva 9. Limpiar la señal sin inventar evidencia

**Mensaje visible:** Interpolar continuidad no convierte un fotograma deficiente en válido.

**Guion:** Un hueco aislado de `hip_midpoint_y` puede interpolarse temporalmente entre muestras conocidas. A `24.04 fps`, la ventana configurada de `0.20 s` equivale a cinco fotogramas. La mediana centrada reduce estimaciones atípicas, es decir, saltos aislados incompatibles con las muestras vecinas. Después, el promedio centrado reduce pequeñas variaciones restantes y facilita localizar máximos estables. Cada resultado se asigna al fotograma central de su ventana; por eso se obtiene una curva completa y no un único promedio global.

**Ejemplo real, fotograma 388:** valores `0.750289`, `0.750377`, `0.751089`, `0.751154` y `0.750506`; mediana `0.750506`; promedio de las medianas vecinas `0.750437`. El valor suavizado queda asociado al fotograma 388.

**Fórmula:** `y(t) = y_a + ((t - t_a)/(t_b - t_a)) × (y_b - y_a)`.

**Evidencia:** `01_limpieza_interpolacion_suavizado.png`.

## Diapositiva 10. Prominencia: un pico debe sobresalir

**Mensaje visible:** Un máximo local no basta para afirmar que existe una profundidad de sentadilla.

**Guion:** La prominencia compara el pico con la base lateral más alta. El umbral es adaptativo: `max(0.03, 0.18 × (P95 - P05))`. En el caso conductor, el rango robusto fue `0.17472`, el mínimo requerido `0.03145` y las tres profundidades aceptadas superaron ese valor.

**Fórmula:** `prominencia(p) = señal(p) - max(base_izquierda, base_derecha)`.

**Evidencia:** `02_prominencia_picos_reales.png` y clip HyperFrames de segmentación.

## Diapositiva 11. La recuperación evita duplicar una ejecución

**Mensaje visible:** Separación temporal no implica una nueva sentadilla; debe existir recuperación vertical.

**Guion:** En el caso límite, dos candidatos estaban separados `2.002 s`, pero el valle intermedio solo recuperó `0.000204`, por debajo de `0.03`. El algoritmo anterior contó una repetición adicional. La validación actual fusiona esos candidatos y conserva el pico más profundo.

**Regla:** `recuperación = min(pico_1, pico_2) - mínimo_entre_picos` en la orientación de la señal usada por el algoritmo; se acepta una separación solo cuando la recuperación alcanza el mínimo exigido.

**Evidencia:** `03_error_doble_pico_recuperacion.png`.

## Diapositiva 12. Del pico a las fases de la ejecución

**Mensaje visible:** Reposo → descenso → máxima profundidad → ascenso → cierre.

**Guion:** El pico aceptado fija la máxima profundidad. A ambos lados se buscan regiones de retorno hacia la posición alta para delimitar el inicio y el cierre. Para la repetición 3 del caso conductor, el sistema conserva el fotograma 474 como inicio, el 592 como máxima profundidad y el 621 como final.

**Conexión web:** seleccionar repetición 3 y recorrer los tres eventos sincronizados con el video.

## Diapositiva 13. `W0` normaliza las distancias

**Mensaje visible:** `W0 = mediana del ancho de hombros en los fotogramas iniciales válidos`.

**Guion:** Una distancia horizontal depende del tamaño aparente de la persona en la imagen. Dividirla entre una referencia corporal inicial permite expresarla como porcentaje. En el caso conductor, `W0 = 0.258264` del ancho normalizado de la imagen. No es el ancho instantáneo de hombros en máxima profundidad.

## Diapositiva 14. Orientación y traslación responden preguntas distintas

**Mensaje visible:** Tronco en grados; pelvis en porcentaje de `W0`.

**Guion:** La inclinación del tronco usa `atan2` porque mide orientación respecto de la vertical. El desplazamiento de pelvis compara el centro de caderas con el centro de tobillos y corrige el desplazamiento inicial porque mide traslación. El signo indica dirección anatómica; la magnitud absoluta se compara con el umbral.

**Resultados de ejemplo:** tronco `12.38°`; pelvis `9.55 % de W0`.

## Diapositiva 15. Alineación cadera–rodilla–tobillo

**Mensaje visible:** La interpolación espacial estima dónde debería cruzar la rodilla el eje cadera–tobillo a la misma altura vertical.

**Guion:** Para cada lado se toman cadera `H`, rodilla `K` y tobillo `A`. Primero se calcula `t = (Ky - Hy)/(Ay - Hy)`. Luego `Kx_esperado = Hx + t(Ax - Hx)`. La diferencia horizontal orientada hacia medial, dividida entre `W0`, produce la desviación porcentual. Esta interpolación ocurre dentro de un fotograma y no debe confundirse con la interpolación temporal de la señal.

**Ejemplo de la rodilla izquierda:** `t = 0.524693`, `Kx_esperado = 0.614828`, desviación medial `27.29 % de W0`.

**Evidencia:** clip `construccion_geometrica_variables.mp4`, que construye secuencialmente `W0`, tronco, pelvis, ambas alineaciones de rodilla y la diferencia bilateral con datos reales de la repetición 3.

## Diapositiva 16. Medir todavía no es clasificar

**Mensaje visible:** Valor + dirección + unidad + regla = estado interpretable.

**Guion:** Cada patrón se evalúa de manera independiente y una repetición puede presentar más de uno. Los umbrales son provisionales para construir y verificar el prototipo; no son puntos de corte clínicos. La salida conserva los estados ausente, no concluyente o presente con dirección cuando corresponde.

## Diapositiva 17. La web demuestra la trazabilidad

**Mensaje visible:** Video, tiempo, fotograma, coordenadas, fórmula y clasificación cuentan la misma historia.

**Guion de demostración:**

1. Seleccionar la repetición 3.
2. Confirmar calidad y disponibilidad en Pose 2D.
3. Ubicar el fotograma 592 en Segmentación.
4. Mostrar `W0` y la geometría de rodilla en Variables.
5. Comprobar la banda de decisión en Reglas.
6. Descargar los artefactos técnicos.

## Diapositiva 18. Qué demuestra y qué no demuestra

**Mensaje visible:** El sistema hace medible y auditable una observación; no reemplaza una evaluación clínica.

**Guion:** El prototipo demuestra detección de pose 2D, control de calidad, segmentación de ejecuciones, cálculo geométrico y reglas transparentes. No determina por sí solo la causa de una compensación, una patología ni un tratamiento. Su desempeño debe estimarse frente a evaluadores expertos mediante precisión, sensibilidad, especificidad, F1-score y concordancia.

## Correspondencia presentación–web–artefactos

| Tema | Diapositiva | Web | Artefacto |
|---|---:|---|---|
| Arquitectura | 3 | Resumen del caso | diagrama Fases 2–5 |
| Producción de artefactos | 4 | Descargas | CSV/JSON canónicos, MP4, PNG y XLSX |
| Calidad de pose | 5–6 | Pose 2D | `frame_quality.csv`, `landmarks.csv`, `pose_quality.png` |
| Señal de cadera | 7 | Segmentación | `frame_phases.csv`, `senal_caderas_animada.mp4` |
| Interpolación | 8 | Segmentación y Variables | fórmula lineal temporal y espacial |
| Limpieza | 9 | Segmentación | `01_limpieza_interpolacion_suavizado.png` |
| Prominencia | 10 | Segmentación | `02_prominencia_picos_reales.png`, clip HyperFrames |
| Recuperación | 11 | Segmentación | `03_error_doble_pico_recuperacion.png` |
| Fases | 12 | Segmentación | `repetitions.csv`, capturas de eventos |
| `W0` | 13 | Variables | `biomechanical_summary.json` |
| Tronco y pelvis | 14 | Variables | `biomechanical_frame_metrics.csv` |
| Rodillas | 15 | Variables | `peak_rep_3.png`, métricas por fotograma, `construccion_geometrica_variables.mp4` |
| Reglas | 16 | Reglas | `rule_evidence.csv`, `findings.json` |

## Preguntas previsibles

### ¿OpenCV decide si la pose es correcta?

No. OpenCV decodifica fotogramas. MediaPipe estima puntos y visibilidad. La decisión de calidad pertenece a la regla implementada por el sistema.

### ¿La visibilidad crítica mínima es un promedio?

No. Es el menor valor efectivo entre las ocho referencias centrales. Se utiliza como control conservador del fotograma.

### ¿Interpolar hace válido un fotograma?

No. Solo preserva continuidad en `hip_midpoint_y`; la bandera original de calidad y las coordenadas anatómicas usadas en las variables no se sustituyen.

### ¿Prominencia significa confianza del modelo?

No. Es una propiedad geométrica de una señal: cuánto sobresale un pico respecto de sus bases laterales.

### ¿Por qué hay grados y porcentajes?

Los grados describen orientación; los porcentajes describen distancias normalizadas. Son preguntas geométricas diferentes.

### ¿Los umbrales son clínicos?

No. Son criterios provisionales del prototipo sujetos a calibración y validación experta.

## Fuentes técnicas para las notas

- MediaPipe Pose Landmarker: coordenadas y visibilidad de pose.
- OpenCV `VideoCapture`: apertura, decodificación y metadatos del video.
- pandas `Series.interpolate`: interpolación temporal de huecos.
- SciPy `find_peaks` y `peak_prominences`: referencia conceptual para máximos locales, distancia y prominencia; no es una llamada directa del pipeline actual.
- Documentación y artefactos reproducibles del caso `dev_valgo_izq_002`.
