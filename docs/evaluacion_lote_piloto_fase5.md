# Evaluación del lote piloto para la Fase 5

## 1. Propósito

Este documento evalúa si los videos controlados incorporados en
`data/sentadilla_bilateral/raw/` permiten iniciar la Fase 5, orientada a
definir reglas biomecánicas interpretables. La evaluación no reemplaza la
clasificación consolidada de los expertos ni constituye una validación del
desempeño del sistema.

El nombre de cada archivo representa el **patrón intentado durante la
grabación**, no una etiqueta de referencia confirmada. Esta distinción evita
ajustar las reglas para que coincidan artificialmente con la intención del
participante.

## 2. Procesamiento realizado

Los siete videos nuevos se procesaron con las etapas disponibles:

1. extracción de pose 2D;
2. segmentación de una o más repeticiones;
3. control de calidad analítica;
4. cálculo de variables biomecánicas por fotograma y repetición;
5. revisión visual del overlay en máxima profundidad.

Todos los videos obtuvieron el estado `apto_para_analisis`, presentaron tres
repeticiones y alcanzaron 100 % de fotogramas válidos. Esto confirma su
factibilidad técnica, pero no confirma por sí solo la etiqueta biomecánica.

## 3. Respuesta de las variables

Los valores siguientes correspondían a la mediana exploratoria de las variables
en máxima profundidad del lote inicial. La implementación vigente conserva el
valor y la clasificación de cada repetición de forma independiente, por lo que
no utiliza esa mediana como salida del sistema. El signo positivo del tronco y la pelvis representa el
lado anatómico izquierdo; en las rodillas, el signo positivo representa
desviación medial.

| Caso | Tronco (°) | Pelvis (%) | Rodilla izq. (%) | Rodilla der. (%) | Diferencia bilateral (%) |
|---|---:|---:|---:|---:|---:|
| `dev_negativo_001` | 1,74 | -3,39 | -23,09 | -28,21 | 5,45 |
| `dev_pelvis_der_001` | 2,71 | -9,33 | -35,16 | -36,66 | 5,01 |
| `dev_pelvis_izq_001` | -14,59 | 23,39 | -6,41 | -33,05 | 25,01 |
| `dev_tronco_der_001` | -27,32 | 2,61 | -15,21 | -38,89 | 19,17 |
| `dev_tronco_izq_001` | 27,89 | 2,37 | -13,28 | -26,72 | 13,44 |
| `dev_valgo_der_001` | 3,25 | -4,44 | -13,31 | -6,17 | 4,57 |
| `dev_valgo_izq_001` | 6,48 | -2,14 | 6,71 | -27,62 | 33,98 |

Estos valores son exploratorios. No deben presentarse todavía como puntos de
corte ni como rangos normales o patológicos.

## 4. Aptitud de cada caso

| Caso | Evaluación analítica | Uso recomendado |
|---|---|---|
| `dev_negativo_001` | No presenta una inclinación marcada del tronco ni una medialización positiva de las rodillas. La base y profundidad son amplias, por lo que no representa por sí solo toda la variabilidad negativa. | Caso negativo piloto; no usar como estándar negativo único. |
| `dev_pelvis_der_001` | El desplazamiento pélvico responde en la dirección esperada y la inclinación del tronco permanece baja. | Caso aislado útil para verificar signo y sensibilidad inicial. |
| `dev_pelvis_izq_001` | El desplazamiento pélvico responde claramente, pero coexiste con inclinación marcada del tronco hacia la derecha y diferencia bilateral elevada. | Caso combinado útil; repetir si se necesita una referencia aislada de pelvis izquierda. |
| `dev_tronco_der_001` | La inclinación del tronco responde claramente en la dirección esperada. | Caso positivo útil para la regla de tronco derecho. |
| `dev_tronco_izq_001` | La inclinación del tronco responde claramente en la dirección esperada. | Caso positivo útil para la regla de tronco izquierdo. |
| `dev_valgo_der_001` | La rodilla derecha no presenta desviación medial positiva en máxima profundidad ni un cambio medial claro respecto al reposo. | No usar como positivo confirmado; repetir la ejecución y revisar visualmente antes de aceptarla. |
| `dev_valgo_izq_001` | La rodilla izquierda presenta desviación medial positiva y una diferencia bilateral marcada. | Caso positivo útil para valgo visible izquierdo y para probar salida multietiqueta. |

## 5. Decisión sobre el avance

El lote permite avanzar con la **estructura técnica** de la Fase 5:

- contrato de reglas independiente del cálculo geométrico;
- estados `presente`, `ausente` y `no_concluyente`;
- evaluación independiente de cada patrón;
- soporte de múltiples etiquetas;
- trazabilidad de variable, valor, umbral y evidencia temporal;
- configuración externa y versionada de umbrales.

El lote también permite realizar pruebas de signo, dirección y coherencia sobre
tronco, pelvis derecha y valgo izquierdo. Sin embargo, todavía no permite
cerrar umbrales definitivos ni estimar desempeño.

## 6. Datos adicionales prioritarios

Antes de congelar los umbrales se requiere, como mínimo:

1. repetir `dev_valgo_der_001` con medialización derecha visible respecto a la
   línea cadera-tobillo;
2. grabar `dev_valgo_bilateral_001`;
3. repetir un desplazamiento pélvico izquierdo procurando mantener el tronco
   centrado;
4. disponer de más de un caso negativo con base y profundidad comparables;
5. incorporar repeticiones de los patrones y, posteriormente, participantes
   diferentes;
6. obtener la clasificación independiente de los expertos para la fase de
   validación.

Los casos combinados no deben descartarse. Se conservarán para probar que el
motor multietiqueta detecte señales coexistentes, pero no deben sustituir los
casos aislados usados para verificar cada regla.

## 7. Estrategia para los umbrales

Los umbrales iniciales se establecerán mediante una estrategia híbrida:

1. definición geométrica y dirección esperada respaldadas por bibliografía;
2. exploración del lote piloto para conocer ruido, magnitud y estabilidad;
3. propuesta de puntos de corte iniciales sin usar todavía la muestra final;
4. congelamiento de reglas y umbrales antes de la evaluación formal;
5. comparación posterior con la referencia consolidada de expertos mediante
   F1-score, sensibilidad, precisión y concordancia Kappa.

No se usarán los nombres de los archivos como verdad de referencia ni se
modificarán los umbrales después de observar los resultados de la muestra
formal, salvo que se declare una nueva versión y una evaluación independiente.
