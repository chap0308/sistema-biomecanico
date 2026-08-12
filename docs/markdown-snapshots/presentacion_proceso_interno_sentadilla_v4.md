D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/peak_rep_3.png

**DEL VIDEO A UNA**

**DECISIÓN AUDITABLE**

Visión por computadora para analizar compensaciones observables durante la sentadilla bilateral

**POSE 2D**

**SEGMENTACIÓN**

**GEOMETRÍA**

Elias Chapoñan · Lima Sur, 2026

> Presente la tesis como una cadena de medición y no como un simple detector visual. La pregunta que guiará toda la exposición es: ¿cómo llegó el sistema a esa clasificación?  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/peak_rep_3.png

**PROBLEMA**

**Observar no equivale a medir**

La utilidad del sistema está en cuantificar, repetir y dejar evidencia de la decisión.

**VER**

**MEDIR**

**AUDITAR**

**“El tronco se inclinó”**

Reconocimiento visual

**12.38° hacia la izquierda**

Magnitud y dirección

**Fotograma + fórmula + regla**

Trazabilidad reproducible

**El reto no es notar un patrón evidente; es convertirlo en una medición consistente y defendible.**

> Reconocer un movimiento notorio puede ser simple. La contribución técnica aparece al definir referencias, controlar calidad, localizar la ejecución, calcular una magnitud comparable y conservar la evidencia.  Fuentes y evidencia: - Guion técnico del sistema; alcance aprobado de la tesis

**ARQUITECTURA**

**Cinco transformaciones, una misma evidencia**

Cada tecnología tiene una responsabilidad delimitada dentro del flujo.

**Video**

Entrada MP4 frontal

**OpenCV**

Decodifica fotogramas

**MediaPipe**

Pose + visibilidad

**Calidad**

Regla del sistema

**Señal y geometría**

pandas · NumPy · Python

**Informe**

FastAPI · Next.js

**La web no recalcula la biomecánica: presenta y sincroniza los artefactos producidos por el pipeline.**

**La arquitectura separa decodificación, estimación, decisión de calidad, medición e interpretación.**

> Explique de izquierda a derecha. No atribuya a OpenCV la validación de pose ni a la interfaz el cálculo biomecánico. SciPy es una referencia conceptual para prominencia, pero el pipeline actual no lo invoca directamente.  Fuentes y evidencia: - D:/sistema-biomecanico/docs/diagramas/presentacion/fases_2_5_sentadilla.drawio - D:/sistema-biomecanico/docs/diagramas/presentacion/fases_2_5_sentadilla.mmd

**PIPELINE DE EVIDENCIA**

**Los resultados no aparecen por arte de magia**

Los datos canónicos se transforman en productos visuales y tabulares sin alterar la evidencia original.

**MediaPipe**

coordenadas · visibilidad

**CSV / JSON**

evidencia canónica

**OpenCV + FFmpeg**

overlays · capturas · MP4

**Matplotlib**

gráficas PNG / PDF

**openpyxl**

tablas XLSX normalizadas

**FastAPI / Next.js**

publicación y exploración

**Los MP4, PNG y XLSX son derivados auditables; los CSV y JSON permiten reproducir el cálculo.**

> MediaPipe entrega datos numéricos, no un informe terminado. OpenCV crea el overlay y el pixelado; Matplotlib representa series; openpyxl compone los instrumentos y libros normalizados; FFmpeg garantiza compatibilidad web.  Fuentes y evidencia: - D:/sistema-biomecanico/docs/analisis_caso_dev_valgo_izq_002_fases_2_5.md - src/squat/pose_video.py - src/squat/evidence.py - src/squat/exports.py

**FASE 2 · CALIDAD**

**Tres niveles que no deben confundirse**

Fotograma decodificado, pose válida y repetición válida son decisiones diferentes.

**1**

**OpenCV**

**¿Pudo leer el fotograma?**

procesados = decodificados / declarados

**2**

**MediaPipe + regla**

**¿Hay referencias anatómicas utilizables?**

válidos = pose válida / decodificados

**3**

**Segmentación**

**¿El intervalo y el pico son analizables?**

repetición válida = válidos del intervalo / total

**Calidad global recomendada: al menos 95 % de los fotogramas decodificados deben tener pose válida.**

> Esta lámina resuelve la ambigüedad entre fotogramas y puntos anatómicos. OpenCV solo confirma lectura; la regla de calidad trabaja sobre las salidas de MediaPipe.  Fuentes y evidencia: - D:/sistema-biomecanico/docs/explicacion_ajuste_indicador_puntos_anatomicos.md - D:/sistema-biomecanico/docs/analisis_caso_dev_valgo_izq_002_fases_2_5.md

**FASE 2 · POSE 2D**

**De 33 puntos a 13 referencias útiles**

La selección reduce el modelo a las referencias necesarias para el análisis frontal.

D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/peak_rep_3.png

**33**

**estimados por MediaPipe**

**13**

**conservados por el sistema**

**8**

**referencias centrales críticas**

**Un punto es utilizable si**

**x e y son finitas**

y

**visibilidad ≥ 0.50**

**La visibilidad crítica mínima es el menor valor entre los 8 puntos centrales; no es un promedio.**

> Mencione que nariz, talones y puntas del pie aportan información, pero la validez central exige hombros, caderas, rodillas y tobillos. También se exige una referencia distal por pie.  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/peak_rep_3.png - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/frame_quality.csv - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/landmarks.csv

**FASE 2 · DATOS PRIMARIOS**

**MediaPipe entrega una fila por punto y fotograma**

landmarks.csv conserva coordenadas normalizadas, profundidad relativa y visibilidad antes de cualquier resumen.

| Frame | Tiempo | Punto | x | y | z | Visibilidad |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.000 s | Hombro izq. | 0.6449 | 0.3517 | 0.0349 | 0.999998 |
| 0 | 0.000 s | Cadera der. | 0.4414 | 0.5761 | 0.0015 | 0.999964 |
| 228 | 9.485 s | Rodilla izq. | 0.6308 | 0.7432 | -0.0262 | 0.994689 |
| 228 | 9.485 s | Tobillo der. | 0.4097 | 0.8541 | 0.2557 | 0.989488 |
| 592 | 24.628 s | Hombro izq. | 0.6948 | 0.6358 | -0.8655 | 0.999985 |
| 592 | 24.628 s | Rodilla izq. | 0.5444 | 0.8130 | -0.8161 | 0.989900 |

**SISTEMA DE COORDENADAS**

**x**

0 = borde izquierdo

1 = borde derecho

**y**

0 = borde superior

1 = borde inferior

**z**

profundidad relativa;

no entra en las fórmulas 2D

**En este caso: 662 fotogramas con pose × 13 puntos seleccionados = 8 606 filas.**

> Muestre que cada fila es una observación primaria de MediaPipe. El total general es fotogramas con pose multiplicado por 13; si un fotograma no contiene pose, no se escriben sus 13 filas. x e y están normalizadas respecto del ancho y alto de la imagen.  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/landmarks.csv - src/squat/pose_video.py

**FASE 2 · DECISIÓN POR FOTOGRAMA**

**frame\_quality.csv resume si la pose puede analizarse**

Cada fila condensa los 13 puntos seleccionados en una decisión reproducible para un fotograma.

| Frame | Tiempo | Pose | Válido | Puntos | Visibilidad crítica |
| --- | --- | --- | --- | --- | --- |
| 0 | 0.000 s | Sí | 1 | 13 | 0.997180 |
| 228 | 9.485 s | Sí | 1 | 13 | 0.989488 |
| 592 | 24.628 s | Sí | 1 | 13 | 0.924413 |
| 661 | 27.498 s | Sí | 1 | 13 | 0.994451 |

**valid\_for\_analysis(f)**

**1 si:**

• los 8 puntos centrales tienen visibilidad ≥ 0.50

• existe al menos una referencia distal por cada pie con visibilidad ≥ 0.50

**0 en caso contrario**

minimum_critical_visibility = min(visibilidad de hombros, caderas, rodillas y tobillos)

**El CSV almacena True/False; en las fórmulas se interpreta como indicador binario 1/0.**

> No atribuya esta decisión a OpenCV. OpenCV aporta el fotograma decodificado; MediaPipe entrega pose y visibilidad; la regla del sistema construye valid_for_analysis. La visibilidad crítica mínima es un mínimo, no una media.  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/frame_quality.csv - src/squat/pose_video.py

**FASE 2 · INDICADORES**

**Los porcentajes agregan decisiones de distinto nivel**

OpenCV mide lectura técnica; las reglas sobre MediaPipe miden disponibilidad anatómica.

**Fotogramas procesados correctamente**

100 × fotogramas decodificados por OpenCV / fotogramas declarados

**100.00 %**

**Fotogramas válidos**

100 × Σ valid_for_analysis(f) / fotogramas decodificados

**100.00 %**

**Promedio de puntos detectados**

Σ detected_keypoints(f) / fotogramas decodificados

**13.00 de 13**

**Uso del promedio: describe estabilidad y disponibilidad de los 13 puntos; no reemplaza la regla binaria de validez.**

> processed_frames se incrementa únicamente cuando VideoCapture.read devuelve un fotograma decodificado. valid_frames suma la decisión binaria por fotograma. mean_detected_keypoints resume cuántos de los 13 puntos superan el umbral de visibilidad, pero un promedio alto no garantiza por sí solo que estén disponibles todas las referencias obligatorias.  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/pose_summary.json - src/squat/pose_video.py - src/squat/quality_gate.py

**FASE 2 · TRAZABILIDAD VISUAL**

**Dos CSV responden preguntas diferentes**

La interfaz representa los datos canónicos; no recalcula la decisión de calidad.

D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/pose_quality.png

**Visibilidad por punto · repetición 3**

|  | Visibilidad media |
| --- | --- |
| Hombro I | 1 |
| Hombro D | 0.9999 |
| Cadera I | 0.9999 |
| Cadera D | 0.9998 |
| Rodilla I | 0.9939 |
| Rodilla D | 0.9923 |
| Tobillo I | 0.9885 |
| Tobillo D | 0.9764 |
| Talón I | 0.9134 |
| Talón D | 0.9069 |
| Punta I | 0.982 |
| Punta D | 0.9593 |
| Nariz | 1 |

**frame\_quality.csv → disponibilidad por fotograma**

**landmarks.csv → visibilidad y cobertura por punto**

> En la web, Disponibilidad de pose por fotograma se alimenta de frame_quality.csv. Visibilidad por punto anatómico se deriva de landmarks.csv dentro del intervalo de la repetición seleccionada. La gráfica derecha resume la visibilidad media de la repetición 3; la cobertura fue 100 % para los 13 puntos en este caso.  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/pose_quality.png - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/frame_quality.csv - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/landmarks.csv

**FASE 3 · SEÑAL**

**La cadera convierte el movimiento en una curva**

En coordenadas de imagen, y aumenta hacia abajo: descender hace crecer hip_midpoint_y.

D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_inicio_descenso.png

D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_maxima_profundidad.png

D:/sistema-biomecanico/docs/assets/presentacion_sentadilla/hyperframes_senal_caderas/cover_senal_caderas.png

**INICIO · F474**

**PICO · F592**

[**▶ hip\_midpoint\_y = (y\_cadera\_izq + y\_cadera\_der) / 2**](file:///D:/sistema-biomecanico/docs/assets/presentacion_sentadilla/hyperframes_senal_caderas/senal_caderas_animada.mp4)

> La señal es una posición vertical normalizada, no fuerza ni ángulo. La portada abre un clip de 14 segundos construido con los datos reales de frame_phases.csv.  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_inicio_descenso.png - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_maxima_profundidad.png - D:/sistema-biomecanico/docs/assets/presentacion_sentadilla/hyperframes_senal_caderas/senal_caderas_animada.mp4

**CONCEPTO TRANSVERSAL**

**Una fórmula, dos interpolaciones distintas**

Estimar un punto intermedio sirve tanto en el tiempo como dentro de un fotograma.

**q = q₁ + ((u − u₁)/(u₂ − u₁)) × (q₂ − q₁)**

**INTERPOLACIÓN TEMPORAL**

**u = tiempo o fotograma**

**q = hip\_midpoint\_y**

Cubre un hueco breve entre dos muestras conocidas.

**INTERPOLACIÓN ESPACIAL**

**u = coordenada y**

**q = coordenada x**

Cruza el eje cadera–tobillo a la altura de la rodilla.

**La relación lineal es la misma; cambian el dominio, las variables y el propósito.**

> Primero explique el concepto general. Después contraste: la interpolación temporal preserva continuidad de hip_midpoint_y; la espacial construye una referencia geométrica en máxima profundidad. La temporal no valida el fotograma ni sustituye los landmarks biomecánicos.  Fuentes y evidencia: - D:/sistema-biomecanico/docs/analisis_caso_dev_valgo_izq_002_fases_2_5.md - pandas Series.interpolate - src/squat/biomechanics.py

**FASE 3 · LIMPIEZA**

**Limpiar la señal sin inventar evidencia**

Tres operaciones reducen huecos y ruido; la decisión de calidad original permanece intacta.

D:/sistema-biomecanico/docs/assets/segmentacion_sentadilla/01_limpieza_interpolacion_suavizado.png

**VENTANA CENTRADA**

**5 fotogramas**

**≈ 0.208 s**

**Fotograma 388**

cruda       0.751089

mediana     0.750506

promedio    0.750437

**El resultado permanece en F388**

> La mediana reduce estimaciones atípicas y el promedio reduce pequeñas variaciones restantes. center=True asigna el resultado al fotograma central. Cada fotograma repite el procedimiento y la sucesión forma la curva suavizada.  Fuentes y evidencia: - D:/sistema-biomecanico/docs/assets/segmentacion_sentadilla/01_limpieza_interpolacion_suavizado.png - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/frame_phases.csv - pandas rolling median y rolling mean

**FASE 3 · PROMINENCIA**

**Un máximo local debe sobresalir**

La prominencia descarta oscilaciones pequeñas que también producen máximos locales.

D:/sistema-biomecanico/docs/assets/segmentacion_sentadilla/02_prominencia_picos_reales.png

**prominencia(p)**

**señal(p) − max(BI, BD)**

mínimo = max(0.03, 0.18 × (P95 − P05))

D:/sistema-biomecanico/docs/assets/presentacion_sentadilla/hyperframes_segmentacion/cover_prominencia.png

[**▶**](file:///D:/sistema-biomecanico/docs/assets/presentacion_sentadilla/hyperframes_segmentacion/segmentacion_prominencia_recuperacion.mp4)

**CLIP EXPLICATIVO · 18 s**

> Use la figura para los datos reales y el clip para el concepto. En el caso conductor: rango robusto 0.17472; mínimo 0.03145; prominencias aceptadas 0.06266, 0.06623 y 0.08787.  Fuentes y evidencia: - D:/sistema-biomecanico/docs/assets/segmentacion_sentadilla/02_prominencia_picos_reales.png - D:/sistema-biomecanico/docs/assets/presentacion_sentadilla/hyperframes_segmentacion/segmentacion_prominencia_recuperacion.mp4 - SciPy find_peaks y peak_prominences

**FASE 3 · CASO LÍMITE**

**La recuperación evita duplicar una ejecución**

Dos candidatos separados en el tiempo pueden pertenecer a la misma sentadilla.

D:/sistema-biomecanico/docs/assets/segmentacion_sentadilla/03_error_doble_pico_recuperacion.png

**2.002 s**

separación temporal

**0.000204**

recuperación observada

**< 0.03 → fusionar**

**El algoritmo conserva el pico más profundo porque no hubo una recuperación biomecánica suficiente.**

> Este es el ejemplo más útil para demostrar que la segmentación no depende solo del tiempo. Explique el error anterior de cuatro repeticiones y la corrección actual.  Fuentes y evidencia: - D:/sistema-biomecanico/docs/assets/segmentacion_sentadilla/03_error_doble_pico_recuperacion.png - D:/sistema-biomecanico/docs/validacion_casos_limite_segmentacion_temporal.md

**FASE 3 · EVENTOS**

**Del pico a las fases de una ejecución**

La repetición conserva tres fotogramas clave y dos intervalos de movimiento.

D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_inicio_descenso.png

**INICIO**

F474 · 19.75 s

D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_maxima_profundidad.png

**MÁXIMA PROFUNDIDAD**

F592 · 24.63 s

D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_final_ascenso.png

**CIERRE**

F621 · 25.84 s

**Descenso y ascenso se calculan alrededor de una profundidad aceptada; el pico no se analiza de forma aislada.**

> Muestre la conexión con la web: al seleccionar cada evento, el video se posiciona en el mismo fotograma. La repetición 3 va del fotograma 474 al 621.  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_inicio_descenso.png - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_maxima_profundidad.png - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_final_ascenso.png - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/repetitions.csv

**FASE 4 · NORMALIZACIÓN**

**W0 convierte píxeles aparentes en proporciones corporales**

La referencia se estima en reposo inicial; no en el fotograma de máxima profundidad.

D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_inicio_descenso.png

**W0**

**W0 = mediana(|x\_hombro\_der − x\_hombro\_izq|)**

fotogramas iniciales válidos

**0.258264**

ancho normalizado

**≈ 123.45 px**

en 478 px de ancho

**% de W0**

unidad de distancias

**W0 reduce el efecto del tamaño aparente; no corrige perspectiva ni reemplaza una calibración 3D.**

> Explique por qué se usa una mediana: reduce el efecto de un fotograma inicial atípico. W0 se aplica a pelvis y rodillas, no al ángulo del tronco.  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rep_03_inicio_descenso.png - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/biomechanical_summary.json

**FASE 4 · GEOMETRÍA**

**Orientación y traslación son preguntas distintas**

Por eso el tronco se expresa en grados y la pelvis como porcentaje de W0.

**INCLINACIÓN DEL TRONCO**

**θ = atan2(Δx, Δy)**

Pregunta: ¿cuánto se orienta el eje respecto de la vertical?

**Resultado R3: 12.38°**

**DESPLAZAMIENTO DE PELVIS**

**100 × Δx / W0**

Pregunta: ¿cuánto se trasladó lateralmente la pelvis respecto de la base?

**Resultado R3: 9.55 % de W0**

**El signo indica izquierda o derecha; la magnitud absoluta se compara con el umbral.**

> La diferencia de unidades no es inconsistencia: responde a dos objetos geométricos distintos. El tronco mide orientación; la pelvis, traslación.  Fuentes y evidencia: - D:/sistema-biomecanico/docs/analisis_caso_dev_valgo_izq_002_fases_2_5.md - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/biomechanical_repetition_metrics.csv

**FASE 4 · RODILLA**

**Alineación cadera–rodilla–tobillo**

La interpolación espacial construye una referencia esperada a la altura vertical de la rodilla.

D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/peak_rep_3.png

**▶ CLIP · 26 s**

**1**

**t = (Ky − Hy) / (Ay − Hy)**

**2**

**Kx esperado = Hx + t(Ax − Hx)**

**3**

**100 × desplazamiento medial / W0**

Interpolación espacial: un solo fotograma

**Ejemplo · rodilla izquierda**

**H**

(0.607777, 0.750241)

**K**

(0.544360, 0.812981)

**A**

(0.621215, 0.869815)

**t**

0.524693

**Kx esperado**

0.614828

**Desviación**

27.29 % de W0

**La diferencia bilateral usa las dos alineaciones ya calculadas; no equivale por sí sola a una asimetría corporal general.**

> Destaque que esta interpolación es espacial. La imagen enlaza un clip de 26 segundos que construye W0, tronco, pelvis, ambas rodillas y diferencia bilateral con datos reales.  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/peak_rep_3.png - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/biomechanical_frame_metrics.csv - D:/sistema-biomecanico/docs/assets/presentacion_sentadilla/hyperframes_geometria_variables/construccion_geometrica_variables.mp4 - D:/sistema-biomecanico/docs/analisis_caso_dev_valgo_izq_002_fases_2_5.md

**FASE 5 · INTERPRETACIÓN**

**Medir todavía no es clasificar**

La regla conserva magnitud, dirección, unidad y estado para cada patrón.

**VALOR**

**12.38**

**DIRECCIÓN**

**izquierda**

**UNIDAD**

**grados**

**REGLA**

**≥ 12**

**ESTADO**

**presente**

**Los cuatro patrones se evalúan de forma independiente; una repetición puede contener ninguna, una o varias compensaciones observables.**

**Los umbrales son provisionales del prototipo; deben calibrarse y validarse frente a la referencia experta.**

> Evite presentar los umbrales como clínicos. Esta fase traduce una medición a un estado interpretable y conserva la evidencia que permite revisar la decisión.  Fuentes y evidencia: - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/rule_evidence.csv - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/findings.json - D:/sistema-biomecanico/data/sentadilla_bilateral/outputs/dev_valgo_izq_002/quality_gate_summary.json

**DEMOSTRACIÓN**

**La web hace visible la trazabilidad**

La presentación explica la lógica; la interfaz permite recorrer el caso y descargar la evidencia.

D:/sistema-biomecanico/docs/assets/presentacion_sentadilla/web_trazabilidad_caso.png

**1**

**Pose 2D**

calidad y puntos

**2**

**Segmentación**

fotograma 592

**3**

**Variables**

W0 y geometría

**4**

**Reglas**

banda de decisión

**5**

**Descargas**

artefactos técnicos

**Video, tiempo, fotograma, coordenadas, fórmula y clasificación deben contar la misma historia.**

> La demostración debe durar entre dos y tres minutos. No recorra toda la página: siga los cinco pasos y use siempre la repetición 3 para mantener continuidad narrativa.  Fuentes y evidencia: - D:/sistema-biomecanico/docs/assets/presentacion_sentadilla/web_resumen_caso.png - D:/sistema-biomecanico/docs/assets/presentacion_sentadilla/web_trazabilidad_caso.png - Aplicación web /cases/\[caseId]

**LO QUE DEMUESTRA**

**Una observación**

**se vuelve medible**

**y auditable.**

**✓**

**Pose 2D con control de calidad**

**✓**

**Segmentación de ejecuciones**

**✓**

**Geometría observable**

**✓**

**Reglas transparentes**

**✓**

**Comparación con expertos**

**No determina por sí solo una causa anatómica, patología o tratamiento.**

Siguiente paso: estimar desempeño frente a evaluadores expertos mediante F1-score y concordancia.

**Preguntas**

> Cierre la exposición delimitando el alcance. El sistema no sustituye una evaluación clínica; aporta medición observable, trazabilidad y una base reproducible para contrastar con expertos.  Fuentes y evidencia: - Plantilla del proyecto de tesis; matriz de operacionalización; protocolo de evaluación experta
