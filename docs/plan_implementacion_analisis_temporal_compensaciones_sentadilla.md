# Plan de implementación del análisis temporal de compensaciones en sentadilla

## 1. Propósito

Este documento especifica la siguiente evolución del sistema de sentadilla bilateral:

1. conservar el resultado del fotograma de máxima profundidad;
2. analizar también el descenso y el ascenso completos;
3. representar apariciones sostenidas como intervalos temporales, no como una lista de fotogramas;
4. mantener una clasificación global simple y comparable con la evaluación experta;
5. mostrar diferente nivel de detalle al usuario, investigador y experto;
6. precisar la diferencia bilateral de rodillas sin confundir apertura lateral con valgo;
7. habilitar recomendaciones condicionadas por combinaciones observables, sin convertir la salida 2D en un diagnóstico;
8. generar, cuando el video contenga varias repeticiones, una síntesis comparativa opcional que preserve el resultado independiente de cada repetición.

La implementación debe mantener el alcance de la tesis: detectar **compensaciones y asimetrías cinemáticas observables en vista frontal 2D**. No debe afirmar rotaciones tridimensionales, patologías o causas anatómicas.

## 2. Decisiones cerradas

### 2.1. Unidad de análisis y validación

- La unidad continúa siendo `repetición × variable`.
- Cada repetición se clasifica de manera independiente.
- No se combinan varias repeticiones para producir una sola etiqueta validable del video.
- El experto emite una clasificación global por variable y repetición.
- El experto no debe anotar fases ni tiempos exactos.
- El sistema sí conserva fases, intervalos y máxima profundidad como evidencia descriptiva.
- Si el video tiene dos o más repeticiones, puede añadirse una **síntesis comparativa para el usuario y el investigador**. Esta capa no reemplaza, modifica ni participa en las etiquetas usadas para validar la tesis.
- Si el video tiene una sola repetición, la síntesis comparativa simplemente no se genera; el análisis temporal de esa repetición sigue siendo válido.

### 2.2. Alcance temporal

Por repetición se analizarán:

- descenso completo;
- máxima profundidad como instante explícito;
- ascenso completo.

El primer 30 % del ascenso puede conservarse como resumen exploratorio, pero no sustituye el análisis del ascenso completo ni debe ser el único intervalo usado por el clasificador.

### 2.3. Umbrales

En la primera versión se utilizará el mismo par de umbrales de magnitud por variable en descenso, máxima profundidad y ascenso:

- `absent_max`;
- `present_min`.

No se crearán umbrales distintos por fase hasta que la validación experta demuestre errores sistemáticos por fase. Sí se agregarán parámetros temporales versionados:

- duración mínima para considerar una aparición sostenida;
- separación máxima que puede unirse dentro del mismo episodio;
- cobertura mínima de datos válidos por fase;
- duración máxima de un hueco no observado compatible con clasificar ausencia.

Todos deben residir en el ruleset y nunca quedar ocultos en componentes web.

Configuración provisional inicial:

```text
min_episode_duration_seconds: 0.16
max_merge_gap_seconds: 0.08
min_phase_valid_coverage_pct: 80
min_episode_valid_samples: ceil(min_episode_duration_seconds * effective_fps)
max_unobserved_gap_seconds_for_absence: min_episode_duration_seconds - frame_period_seconds
```

Estos valores son hipótesis de ingeniería, no umbrales clínicos de Conor Harris ni Squat University. Deben someterse a análisis de sensibilidad y validación experta antes de congelarse.

#### 2.3.1. Qué significa cada parámetro

| Parámetro | Definición operacional | Función |
| --- | --- | --- |
| `effective_fps` | Frecuencia efectiva estimada con los timestamps válidos del video. | Convertir entre muestras y segundos sin asumir que todos los videos son exactamente de 25 fps. |
| `frame_period_seconds` | `1 / effective_fps`. | Aproximar cuánto tiempo representa cada muestra. |
| `min_episode_duration_seconds` | Duración activa continua mínima sobre el criterio temporal para crear un episodio. | Evitar que uno o pocos fotogramas aislados activen `presente`. |
| `min_episode_valid_samples` | `ceil(min_episode_duration_seconds × effective_fps)`. | Exigir además una cantidad mínima de observaciones y evitar que timestamps anómalos conviertan muy pocas muestras en episodio. |
| `max_merge_gap_seconds` | Interrupción máxima de **muestras válidas en la banda de histéresis** que puede mantener unido un episodio. | Evitar fragmentación por oscilación breve alrededor del umbral. No interpola pose ni convierte el hueco en duración activa. |
| `min_phase_valid_coverage_pct` | Porcentaje mínimo de muestras de la fase con métricas técnicamente válidas. | Impedir decisiones sobre fases dominadas por pérdida de pose. No indica cuánto tiempo estuvo presente la compensación. |
| `max_unobserved_gap_seconds_for_absence` | Mayor hueco consecutivo de muestras inválidas permitido para sostener `ausente`; debe ser menor que la duración mínima de episodio. | Evitar declarar ausencia cuando un intervalo sin datos podría ocultar por sí solo un episodio completo. |

`25 fps` no es un parámetro de clasificación. Es una referencia aproximada derivada de los videos actuales: un fotograma representa cerca de `1/25 = 0.04 s`. Por ello, cuatro fotogramas ocupan aproximadamente `4/25 = 0.16 s`. El sistema debe usar el FPS efectivo de cada repetición: a `24.04 fps`, cuatro muestras representan aproximadamente `0.166 s`; a `30 fps`, `ceil(0.16 × 30) = 5` muestras.

#### 2.3.2. Fundamento disponible y límites

| Decisión | Respaldo disponible | Qué no demuestra |
| --- | --- | --- |
| Analizar episodios en la curva completa | Yoma et al. compararon análisis de curva completa y puntos discretos en sentadilla monopodal con captura markerless; ambos aportan información y presentan error de medición específico por tarea y articulación ([Yoma et al., 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12317789/)). | No prescribe 0.16 s ni cuatro frames. |
| No depender de un solo pico | La literatura markerless en sentadilla muestra error de medición y fiabilidad dependientes de tarea, articulación y sistema; por ejemplo, OpenCap presentó RMSE medio de 7° en sus ángulos de squat, con rango de 2.9° a 13.6° ([Lima et al., 2024](https://pubmed.ncbi.nlm.nih.gov/39444219/)). | No permite trasladar ese error directamente a MediaPipe ni definir un umbral temporal. |
| Expresar persistencia en segundos y muestras | La frecuencia de cámara modifica el error temporal y la capacidad de capturar picos. Un estudio de movimientos rápidos encontró diferencias entre 30 y 120 fps en FPPA e inclinación lateral del tronco, y señaló que no existen guías estandarizadas de FPS para todo análisis 2D ([Alenzi et al., 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11901006/)). Un estudio a 25 Hz encontró utilidad para desplazamientos macroscópicos, pero menor rendimiento en variables derivadas rápidas ([Li et al., 2026](https://pubmed.ncbi.nlm.nih.gov/41829650/)). | No prueba que 25 fps sea óptimo para sentadilla ni que cuatro muestras sean clínicamente suficientes. |
| Limitar y documentar huecos | Métodos de postprocesamiento de pose recomiendan fijar un máximo de hueco, reportarlo en frames y segundos y validarlo para la tarea; `refineDLC` ejemplifica este enfoque, aunque en otro dominio ([Klecel et al., 2025](https://academic.oup.com/biomethods/article/10/1/bpaf084/8368337)). | No respalda específicamente `0.08 s` para sentadilla ni autoriza interpolar una compensación. |
| Cobertura válida de 80 % | Continúa la política de calidad provisional ya usada por repetición en [`analisis_caso_dev_valgo_izq_002_fases_2_5.md`](./analisis_caso_dev_valgo_izq_002_fases_2_5.md). | No existe un estándar publicado localizado que valide 80 % como límite universal o específico de sentadilla. |

Conclusión metodológica:

- `0.16 s` se elige provisionalmente como la primera opción que exige cuatro muestras a ~25 fps y excluye el caso observado de tres fotogramas (~0.12 s); no es un límite clínico publicado;
- `0.08 s` equivale aproximadamente a dos periodos de frame a 25 fps y se usa solo para tolerar oscilaciones válidas en la banda intermedia; no es un estándar publicado;
- `80 %` limita la cantidad total de datos inválidos a 20 %, pero no basta por sí solo: debe combinarse con el control del mayor hueco consecutivo;
- los valores finales se seleccionarán mediante análisis de sensibilidad y concordancia con expertos, no por atribución a Conor Harris o Squat University.

Matriz mínima de sensibilidad propuesta:

```text
min_episode_duration_seconds: 0.12 | 0.16 | 0.20
max_merge_gap_seconds: 0.04 | 0.08 | 0.12
min_phase_valid_coverage_pct: 80 | 90 | 95
```

La selección debe realizarse con casos de calibración y congelarse antes de la evaluación final, para no escoger retrospectivamente la combinación que mejor coincida con los mismos expertos usados como resultado definitivo. Además de concordancia, se reportará cuántos resultados cambian entre `ausente`, `no_concluyente` y `presente` con cada configuración.

### 2.4. Resultado global del sistema

Por variable y repetición:

```text
presente
  si existe al menos un episodio continuo que cumple magnitud,
  duración mínima y cantidad mínima de muestras,
  independientemente de si ocurre en descenso, alrededor de máxima profundidad,
  en ascenso o atravesando sus límites;

ausente
  si descenso, máxima profundidad y ascenso son evaluables,
  no existe ningún episodio presente
  y no existe evidencia limítrofe relevante;

no_concluyente
  si no existe evidencia presente,
  pero hay una banda limítrofe, una detección demasiado breve,
  un cruce aislado en máxima profundidad, cobertura insuficiente
  o datos no finitos.
```

Un intervalo técnicamente no evaluable nunca se convierte en `ausente`.

La salida debe separar:

```text
detección:
  hubo o no muestras consecutivas que cruzaron present_min;

episodio:
  la detección cumplió persistencia y calidad;

clasificación:
  resultado final de la repetición × variable.
```

Así, una detección de tres fotogramas puede conservarse como `detectada_muy_breve` y producir `no_concluyente` sin convertirse en un episodio presente.

La máxima profundidad no constituye una excepción al requisito temporal. Es un endpoint destacado para descripción, auditoría y comparación con el sistema anterior, pero un solo fotograma no valida presencia global.

### 2.5. Reglas de recomendación deshabilitadas

- **R11** queda deshabilitada en la vista frontal: requiere medición sagital validada de flexión de cadera y no puede activarse con profundidad vertical como proxy.
- **R12** queda deshabilitada en esta etapa: requiere comparación protocolizada entre dos videos o condiciones diferentes. Comparar repeticiones dentro del mismo video no activa R12.

## 3. Estado actual que debe preservarse

El sistema ya dispone de:

- series por fotograma en `biomechanical_frame_metrics.csv`;
- fase y repetición por fotograma;
- valor de las variables en máxima profundidad;
- máximos instantáneos descriptivos;
- reglas versionadas con `ausente`, `no_concluyente` y `presente`;
- evaluación experta ciega por repetición y variable;
- vistas diferenciadas para usuario, investigador y experto;
- comparación sistema–expertos.

La nueva implementación debe ser aditiva. No se eliminarán los campos `*_at_peak_*` ni los artefactos de máxima profundidad.

## 4. Semántica correcta de las rodillas

### 4.1. Métricas de origen

Sean:

```text
L(t) = desviación proyectada de la rodilla izquierda
R(t) = desviación proyectada de la rodilla derecha
```

La convención vigente es:

```text
valor positivo = dirección medial
valor negativo = dirección lateral o apertura
```

La diferencia bilateral vigente es:

```text
D_abs(t) = |L(t) - R(t)|
```

Debe agregarse y conservarse también la diferencia con signo:

```text
D_signed(t) = L(t) - R(t)
```

`D_abs` determina la magnitud de la diferencia. `D_signed`, junto con los valores originales, permite explicar cómo difieren las dos rodillas.

### 4.2. Diferencia de alineación no equivale a valgo

La diferencia bilateral es una variable derivada de `L` y `R`. No constituye una cuarta compensación independiente y no debe contarse dos veces para aumentar artificialmente la certeza.

Son posibles estos casos:

| Izquierda | Derecha | Lectura de valgo | Lectura bilateral |
| --- | --- | --- | --- |
| medial presente | ausente | valgo izquierdo | diferencia posiblemente presente |
| medial presente | medial presente y similar | valgo bilateral | diferencia posiblemente ausente |
| medial presente | medial presente, magnitudes distintas | valgo bilateral | diferencia posiblemente presente |
| ambas laterales, una se abre más | valgo ausente | diferencia posiblemente presente |
| una medial y otra lateral | depende del umbral medial | diferencia posiblemente presente y direcciones opuestas |

### 4.3. Resultado del caso `seg_dos_rapidas`

En máxima profundidad de la primera repetición:

```text
L = -25.01 % de W0
R = -15.80 % de W0
D_abs = 9.21 puntos porcentuales de W0
```

La interpretación para el usuario es:

> Ambas rodillas se observaron abiertas hacia fuera, pero la izquierda quedó 9.21 puntos porcentuales más lateral que la derecha.

No debe decirse:

> Hubo mayor desviación medial derecha.

Aunque `R` sea numéricamente mayor que `L`, esa frase invierte el fenómeno visual que interesa comunicar.

### 4.4. Estado absoluto frente a movimiento desde el inicio

Debe distinguirse:

```text
alineación absoluta proyectada:
  L(t), R(t)

cambio dinámico desde el baseline:
  delta_L(t) = L(t) - baseline_L
  delta_R(t) = R(t) - baseline_R

diferencia dinámica bilateral:
  D_delta(t) = |delta_L(t) - delta_R(t)|
```

Regla de lenguaje:

- usar **“quedó/se observó más abierta”** cuando la frase se basa en el estado absoluto;
- usar **“se abrió más durante el movimiento”** solamente cuando el delta respecto al baseline confirma ese cambio;
- usar **“entró más hacia medial”** cuando el delta o el valor positivo lo sustentan;
- mostrar siempre `L`, `R` y la diferencia al investigador.

No se debe reemplazar silenciosamente `D_abs` por `D_delta` en la regla ya validada. Ambas métricas se almacenan; cualquier cambio de la métrica clasificadora requiere nueva calibración y nueva versión del ruleset.

### 4.5. Generador de lenguaje bilateral

Para el valor representativo de un episodio o el valor puntual en máxima profundidad:

| Condición | Texto base para usuario |
| --- | --- |
| `L < 0` y `R < 0`, `|L| > |R|` | “Ambas rodillas se abrieron; la izquierda quedó más abierta que la derecha.” |
| `L < 0` y `R < 0`, `|R| > |L|` | “Ambas rodillas se abrieron; la derecha quedó más abierta que la izquierda.” |
| `L > 0` y `R > 0`, `L > R` | “Ambas rodillas se desplazaron hacia medial; el movimiento fue mayor en la izquierda.” |
| `L > 0` y `R > 0`, `R > L` | “Ambas rodillas se desplazaron hacia medial; el movimiento fue mayor en la derecha.” |
| `L > 0` y `R < 0` | “La izquierda se desplazó hacia medial mientras la derecha se abrió hacia lateral.” |
| `L < 0` y `R > 0` | “La izquierda se abrió hacia lateral mientras la derecha se desplazó hacia medial.” |
| diferencia cambia de lado entre episodios | “La diferencia fue variable: predominó un lado en el descenso y el otro en el ascenso.” |

Si uno de los valores está próximo a cero o es limítrofe, el texto debe describir los valores sin asignar una dirección categórica rígida.

La implementación no debe seguir derivando el predominio únicamente con `L > R`. Debe producir dos campos distintos:

```text
relation_kind:
  medial_predominance
  lateral_predominance
  opposite_directions
  neutral_or_unclear

predominant_side:
  izquierda
  derecha
  sin_predominio
  variable
```

Reglas mínimas:

- si ambos valores son positivos, tiene predominio medial el lado con mayor magnitud positiva;
- si ambos son negativos, tiene predominio lateral el lado con mayor magnitud absoluta negativa;
- si tienen signos opuestos, usar `opposite_directions` y describir cada rodilla; no reducirlo a predominio medial;
- si la relación cambia entre episodios, usar `variable` en el resumen global y conservar el detalle por episodio.

Para `L=-25.01` y `R=-15.80`:

```text
relation_kind = lateral_predominance
predominant_side = izquierda
```

La localización secundaria del sistema debe ser izquierda, aunque el valor derecho sea numéricamente mayor por estar menos alejado de cero.

### 4.6. Etiqueta experta de diferencia bilateral

Las opciones actuales ya combinan ocurrencia y localización. Deben conservar el contrato:

```text
ausente
presente_izquierda
presente_derecha
presente_sin_direccion
no_concluyente
```

Sin embargo, el texto visible debe ser neutral:

- `Presente, predominio izquierdo`;
- `Presente, predominio derecho`;
- `Presente, sin predominio claro`.

No debe decir “mayor desviación medial” porque la diferencia también puede deberse a una mayor apertura lateral.

El sistema aportará después el detalle `medial`, `lateral`, `direcciones_opuestas` o `variable`. No se exige al experto anotarlo.

## 5. Episodios temporales

### 5.1. Definición

Un episodio es un intervalo continuo en el que la señal satisface de manera sostenida el criterio de presencia.

Campos mínimos:

```json
{
  "phase": "descenso",
  "start_frame": 45,
  "end_frame": 59,
  "start_seconds_relative": 0.8,
  "end_seconds_relative": 1.4,
  "start_seconds_video": 5.3,
  "end_seconds_video": 5.9,
  "duration_seconds": 0.6,
  "status": "presente",
  "direction": "izquierda",
  "sustained_value": 13.2,
  "valid_coverage_pct": 100.0
}
```

Los tiempos relativos parten del inicio de la repetición. Los tiempos absolutos del video se conservan para seek y auditoría.

### 5.2. Histéresis y persistencia

La extracción no debe abrir y cerrar episodios por cada cruce de un frame:

1. entrar en estado presente al alcanzar `present_min` durante la persistencia configurada;
2. mantener el episodio dentro de la banda intermedia;
3. cerrarlo al caer hasta `absent_max` durante la persistencia configurada;
4. unir únicamente interrupciones limítrofes con muestras válidas menores que `max_merge_gap_seconds`;
5. cerrar el episodio si cambia de dirección de manera sostenida;
6. marcar los huecos de mala calidad como `no_evaluable`, no como ausencia.

Parámetros iniciales de ingeniería, pendientes de calibración:

```text
min_episode_duration_seconds: 0.16
max_merge_gap_seconds: 0.08
min_phase_valid_coverage_pct: 80
min_episode_valid_samples: ceil(min_episode_duration_seconds * effective_fps)
max_unobserved_gap_seconds_for_absence: min_episode_duration_seconds - frame_period_seconds
```

Se expresarán en segundos para no depender de una frecuencia fija. `effective_fps` se estimará con la mediana de los intervalos de timestamp válidos de la repetición. Un episodio debe cumplir tanto `0.16 s` como `ceil(0.16 * effective_fps)` muestras válidas consecutivas; a aproximadamente 25 fps esto equivale a cuatro fotogramas. La implementación calculará la duración considerando el periodo representado por las muestras, no solo `timestamp_final - timestamp_inicial`.

`min_phase_valid_coverage_pct` significa que al menos el 80 % de las muestras esperadas de la fase tienen métricas válidas. No significa que la compensación deba ocupar el 80 % de la fase. Deben almacenarse por separado:

```text
valid_coverage_pct:
  proporción de la fase con datos técnicamente evaluables;

active_duration_seconds:
  tiempo realmente por encima del criterio de presencia;

episode_span_seconds:
  tiempo entre inicio y fin después de unir huecos permitidos;

active_ratio_pct:
  active_duration_seconds / episode_span_seconds.
```

Un hueco de hasta `0.08 s` solo puede unirse si contiene muestras técnicamente válidas dentro de la banda de histéresis, los segmentos de ambos lados pertenecen a la misma variable y dirección y el hueco no se debe a un cambio sostenido hacia ausencia. Puede atravesar un límite de fase si la señal es continua. El hueco no suma duración activa. Esto evita que la unión artificial transforme varios picos mínimos en un episodio sostenido.

Los huecos de pose inválida no se unen mediante `max_merge_gap_seconds` y rompen la evidencia de continuidad. Para clasificar una fase como `ausente`, además del 80 % de cobertura, su mayor hueco consecutivo no observado debe ser menor que `min_episode_duration_seconds`; de lo contrario, la fase será `no_evaluable` porque el hueco podría contener un episodio completo. Las métricas interpoladas pueden emplearse para segmentación si el pipeline lo documenta, pero no para inventar presencia o ausencia de una compensación.

Los valores definitivos deben validarse y congelarse antes de la evaluación formal. Como análisis de sensibilidad se compararán, como mínimo, reglas de `0.12 s`, `0.16 s` y `0.20 s`, documentando cuánto cambia la concordancia frente a expertos.

Clasificación técnica de persistencia:

```text
very_brief:
  existe una detección continua, pero dura menos de 0.16 s;

sustained:
  existe al menos un episodio continuo que cumple 0.16 s y el mínimo de muestras;

intermittent:
  existen dos o más detecciones o episodios separados por huecos mayores de 0.08 s;

peak_only:
  solo el endpoint de máxima profundidad cruza present_min;

not_evaluable:
  la calidad o cantidad de muestras no permite valorar persistencia.
```

Estas categorías son descriptivas y técnicas. No equivalen por sí solas a gravedad clínica.

### 5.3. Máxima profundidad

La máxima profundidad sigue siendo un instante separado:

```json
{
  "frame": 87,
  "seconds_relative": 1.9,
  "seconds_video": 6.4,
  "value": 9.21,
  "status": "no_concluyente",
  "direction": "predominio_izquierdo"
}
```

Un episodio puede atravesar ese instante sin partirse. La interfaz lo narrará por partes:

> Comenzó al final del descenso, estuvo presente en máxima profundidad y continuó durante el inicio del ascenso.

Si el episodio rodea el fondo pero el frame puntual queda limítrofe:

> La diferencia rodeó la máxima profundidad, pero el instante exacto fue no concluyente.

El resultado puntual de máxima profundidad se conserva por compatibilidad y trazabilidad con el diseño anterior de la tesis, pero deja de activar presencia global por sí solo. Si únicamente ese fotograma cruza `present_min`:

```text
peak.instant_status: present
global_status: no_concluyente
reason_code: peak_only_without_temporal_support
temporal_persistence: very_brief
recommendation_confidence: baja
```

La interfaz debe diferenciar “cruzó el umbral en máxima profundidad” de “compensación presente de forma sostenida”.

### 5.4. Casos límite de persistencia

| Caso | Resultado temporal | Clasificación de repetición si no hay otra evidencia |
| --- | --- | --- |
| Cruce de 1–3 fotogramas y menos de `0.16 s` | `detectada_muy_breve`; no crea episodio | `no_concluyente` |
| Segmento continuo de al menos `0.16 s` | episodio sostenido | `presente` |
| Dos segmentos separados, cada uno menor de `0.16 s` | conservar dos detecciones breves; no sumar duraciones | `no_concluyente` |
| Detección breve en descenso y otra breve en ascenso | conservar por fase; no sumarlas | `no_concluyente` |
| Señal continua desde el final del descenso, a través del fondo y hacia el ascenso | un episodio trans-fase; puede sumar duración continua | `presente` si alcanza `0.16 s` |
| Descenso o ascenso total menor de 1 segundo | aplicar los mismos segundos y reportar también proporción de fase | depende de duración y cobertura |
| Fase con menos muestras totales que `min_episode_valid_samples` | `temporally_insufficient` | `no_concluyente` salvo episodio válido en otra parte de la repetición |
| Fase con menos de 80 % de datos válidos | fase `no_evaluable` | `no_concluyente` salvo episodio válido en otra parte de la repetición |
| Peak presente sin episodio adyacente | `peak_only_without_temporal_support` | `no_concluyente` |

Que una fase dure menos de un segundo no cambia automáticamente los umbrales de magnitud ni la clasificación. Sí vuelve especialmente importante mostrar duración absoluta y porcentaje de la fase. Por ejemplo, `0.16 s` representa 16 % de una fase de `1.00 s`, pero 32 % de una fase de `0.50 s`.

No se agregan apariciones de fases diferentes para superar artificialmente `0.16 s`. La persistencia pertenece a un intervalo continuo, no a la suma total de tiempo detectado en toda la repetición.

Los límites entre descenso, máxima profundidad y ascenso son etiquetas biomecánicas, no cortes obligatorios del episodio. Si la señal es continua, puede contabilizarse a través de esos límites. A aproximadamente 25 fps:

| Distribución de muestras consecutivas sobre `present_min` | Total | Resultado global si no hay otra evidencia |
| --- | ---: | --- |
| solo máxima profundidad | 1 frame | `no_concluyente` |
| descenso + máxima profundidad | 3 frames / ~0.12 s | `no_concluyente` |
| máxima profundidad + ascenso | 3 frames / ~0.12 s | `no_concluyente` |
| descenso + máxima profundidad + ascenso | 3 frames / ~0.12 s | `no_concluyente` |
| cualquier distribución continua que atraviesa el fondo | 4 frames / ~0.16 s | `presente` |
| cuatro frames repartidos en segmentos no continuos | 4 frames acumulados | no se suman; `no_concluyente` si ninguno forma episodio |

La misma regla se aplica a más fotogramas: se evalúa cada intervalo continuo, no la fase donde cayó cada muestra ni la suma total dispersa.

### 5.5. Profundidad como contexto, no como compensación

La vista frontal actual puede calcular, sin llamarlos grados de flexión de cadera:

```text
peak_hip_vertical_drop_normalized
hip_to_knee_vertical_relation_at_peak
descent_depth_progress_pct
onset_depth_progress_pct por episodio
descent_duration_seconds
ascent_duration_seconds
```

Usos permitidos:

- describir si una señal apareció temprano, a mitad o al final del descenso de una repetición;
- comparar exposición entre repeticiones del mismo video;
- advertir que una ausencia ocurrió en una repetición menos profunda;
- contextualizar consistencia y confianza de una recomendación.

Usos no permitidos:

- presentar estas métricas como grados anatómicos de flexión de cadera;
- inferir automáticamente IR/ER, dorsiflexión o una causa estructural;
- convertir una repetición menos profunda en `presente` o `ausente` por contrafactual;
- activar la regla R11 mientras no exista una medición sagital validada.

## 6. Contratos de datos propuestos

### 6.1. Resumen por fase

```json
{
  "phase": "descenso",
  "status": "presente",
  "direction": "izquierda",
  "max_sustained_value": 13.2,
  "max_instant_value": 15.7,
  "valid_coverage_pct": 98.4,
  "episodes": []
}
```

`max_instant_value` es descriptivo; no activa por sí solo la regla.

### 6.2. Resumen temporal por hallazgo

```json
{
  "repetition_index": 1,
  "finding": "asimetria_bilateral_observable",
  "global_status": "presente",
  "global_direction": "variable",
  "relation_kind": "lateral_predominance",
  "predominant_side": "izquierda",
  "peak": {},
  "phases": {
    "descenso": {},
    "ascenso": {}
  },
  "baseline": {
    "absolute_value": 3.09,
    "left_value": -3.25,
    "right_value": -0.03
  },
  "reason_codes": []
}
```

### 6.3. Códigos de razón

`no_concluyente` debe explicar su causa:

- `threshold_band`;
- `insufficient_valid_coverage`;
- `non_finite_metric`;
- `unstable_direction`;
- `episode_too_short`;
- `peak_frame_invalid`;
- `phase_missing`;
- `temporally_insufficient`;
- `long_unobserved_gap`;
- `brief_detection_only`;
- `peak_only_without_temporal_support`;
- `repetitions_not_comparable_depth`;
- `repetitions_conflicting_direction`;
- `repetitions_different_results`.

La interfaz no mostrará todos estos términos al usuario, pero el investigador y los exports sí.

### 6.4. Síntesis opcional para videos con varias repeticiones

La síntesis de video es una capa derivada y no una nueva verdad de terreno:

```json
{
  "finding": "lateral_trunk_inclination",
  "repetition_count": 2,
  "present_count": 1,
  "absent_count": 0,
  "inconclusive_count": 1,
  "result_comparison": "different",
  "direction_comparison": "same_side",
  "depth_comparison": "different",
  "depth_detail": "repetition_2_shallower",
  "tempo_comparison": "similar",
  "repetitions": [1, 2],
  "reason_codes": ["repetitions_not_comparable_depth"]
}
```

Campos comparativos simples:

```text
result_comparison: same | different
direction_comparison: same | different | not_applicable
depth_comparison: similar | different | unavailable
tempo_comparison: similar | different | unavailable
```

No se construye un estado compuesto que intente resolver todas las combinaciones.

Reglas de decisión:

1. Nunca sobrescribir los resultados independientes.
2. No usar mayoría simple ni construir una etiqueta global de compensación; mostrar `n de N` y las diferencias.
3. Comparar de forma descriptiva resultado, dirección, fase, duración y profundidad alcanzada.
4. Si aparecen variables o direcciones diferentes, no intentar combinarlas en una hipótesis o recomendación única.
5. Mantener las recomendaciones individuales de cada repetición junto a su propio resultado.
6. Si las profundidades difieren, indicarlo como una condición que puede contribuir a la diferencia, sin afirmar causalidad ni calcular qué habría ocurrido con igual profundidad.
7. Si cambian stance, toe-out, talones, carga, velocidad o instrucciones, mostrar esas diferencias cuando estén registradas; no inferir la intención únicamente desde la pose.
8. El resumen comparativo puede sugerir repetir el protocolo con profundidad y técnica semejantes, pero no prioriza ni fusiona correctivos.

Para videos de una sola repetición:

```text
cross_repetition_comparison = null
```

Este estado no reduce la validez del resultado de la repetición ni debe mostrarse como error al usuario.

## 7. Evaluación experta

### 7.1. El formulario no requiere fases

El experto observará la repetición completa en bucle y responderá una vez por variable. La instrucción debe decir:

> Clasifique la variable como presente si observa una desviación mantenida durante un intervalo de la repetición. No la marque como presente basándose únicamente en un fotograma pausado de máxima profundidad. No es necesario contar fotogramas ni indicar la fase: el sistema aplica el criterio temporal cuantitativo.

Esto alinea el alcance del experto con el nuevo resultado global del sistema.

El experto no necesita estimar `0.16 s`; ese es el criterio operacional del sistema. Sí debe observar la repetición completa, con reproducción y avance cuadro a cuadro disponibles cuando necesite resolver una aparición limítrofe.

### 7.2. Las opciones actuales ya combinan dos niveles

Ejemplo de valgo:

- `Presente en rodilla izquierda` = ocurrencia presente + localización izquierda;
- `Presente en rodilla derecha` = ocurrencia presente + localización derecha;
- `Presente bilateral` = ocurrencia presente + localización bilateral.

Ejemplo de diferencia bilateral:

- `Presente, predominio izquierdo` = ocurrencia presente + localización izquierda;
- `Presente, predominio derecho` = ocurrencia presente + localización derecha.

No se necesitan checkboxes adicionales. Las clasificaciones son mutuamente excluyentes.

### 7.3. Control de interfaz

El `select` actual es válido y representa el menor cambio. Si se mejora la ergonomía, shadcn recomienda `ToggleGroup` de selección única para conjuntos de 2–7 opciones. No debe usarse `Checkbox`.

Una composición opcional sería:

```text
Estado:      [Ausente] [Presente] [No concluyente]
Localización, si presente: [Izquierda] [Derecha] [Bilateral]
```

No es requisito para la implementación temporal. Si se adopta, debe conservar exactamente el payload vigente de `classification` y `observed_side`.

## 8. Comparación sistema–expertos

### 8.1. Dos resultados explícitos

La comparación debe exponer:

1. **Coincidencia de ocurrencia**, principal:
   - compara `presente`, `ausente` o `no_concluyente`;
2. **Coincidencia de localización**, secundaria:
   - compara izquierda, derecha o bilateral cuando ambas clasificaciones son presentes.

Campos sugeridos:

```json
{
  "occurrence_match": true,
  "localization_match": false,
  "exact_match": false
}
```

`exact_match` puede mantenerse por compatibilidad como la coincidencia conjunta.

### 8.2. Diferencia bilateral

Para `bilateral_asymmetry`:

- la coincidencia principal se basa solo en ocurrencia;
- el predominio se conserva como análisis secundario;
- la semántica medial/lateral es evidencia generada por el sistema y no forma parte obligatoria del juicio experto.

La implementación actual ya normaliza cualquier dirección presente de esta variable a `presente`. Debe conservarse esa lógica para la métrica principal y hacerse visible en la documentación.

### 8.3. Evidencia temporal en la comparación

Después del cierre del caso, la tarjeta puede mostrar:

```text
Experto: Presente, izquierda
Sistema: Presente, izquierda
Coincidencia de ocurrencia: Sí
Coincidencia de localización: Sí

Evidencia temporal del sistema
Descenso: presente, 0.8–1.4 s
Máxima profundidad: ausente
Ascenso: presente, 2.3–2.7 s
```

La evidencia temporal no se mostrará antes de que el experto envíe su evaluación.

## 9. Presentación por rol

### 9.1. Usuario

El usuario necesita lenguaje, orden y rangos, no frames:

```text
Diferencia bilateral de rodillas

Durante el descenso, entre 0.8 y 1.4 s, ambas rodillas se abrieron,
pero la izquierda se abrió más que la derecha.

En máxima profundidad la diferencia fue no concluyente.
Durante el ascenso no volvió a detectarse.
```

Elementos:

- `Badge` de resultado global;
- resumen en lenguaje natural;
- línea temporal por repetición;
- marcador explícito de máxima profundidad;
- intervalos pulsables para reproducir el video;
- recomendación condicionada y pruebas sugeridas;
- advertencia de alcance observacional.

La ruta `my-analyses/[analysisId]` reutiliza `CaseDetailView` con audiencia `self-service`; la mejora debe implementarse en el componente compartido o en un subcomponente por audiencia, no duplicarse en la ruta.

Si hay varias repeticiones, mostrar primero las tarjetas independientes y luego un resumen comparativo:

```text
Inclinación lateral del tronco

Repetición 1: presente de forma sostenida durante el descenso.
Repetición 2: aparición demasiado breve; resultado no concluyente.

Comparación: el comportamiento no fue consistente entre repeticiones. La segunda
repetición alcanzó menor profundidad, por lo que no ofrece la misma exposición.
No se puede atribuir la diferencia únicamente a la profundidad.
```

Casos de lenguaje:

| Síntesis | Texto para usuario |
| --- | --- |
| consistente | “Se observó de forma consistente en {n} de {N} repeticiones.” |
| aparición parcial | “Se observó en {n} de {N} repeticiones; el comportamiento fue variable.” |
| dirección variable | “La dirección cambió entre repeticiones, por lo que no se puede señalar un predominio estable.” |
| hallazgos diferentes | “Las repeticiones mostraron compensaciones diferentes; conviene repetir el test con la misma técnica y profundidad objetivo.” |
| profundidad no comparable | “Las repeticiones alcanzaron profundidades diferentes; la ausencia en la más superficial solo describe el rango realizado.” |
| una repetición | No mostrar tarjeta comparativa. |

Una aparición menor de `0.16 s` se narrará así:

> Se detectó una desviación muy breve durante {fase}, entre {inicio} y {fin} s. No duró lo suficiente para considerarla un episodio sostenido, por lo que el resultado es no concluyente.

Las recomendaciones se muestran dentro del detalle de cada repetición. La tarjeta comparativa no genera, fusiona ni ordena recomendaciones de varias repeticiones.

### 9.2. Investigador

Además de la vista anterior:

- valores absolutos y delta desde baseline;
- series original y suavizada;
- umbrales y ruleset;
- onset, offset y duración;
- máximo instantáneo y máximo sostenido;
- cobertura válida;
- códigos de razón;
- frames y timestamps absolutos;
- `L`, `R`, `D_abs`, `D_signed` y `D_delta` para rodillas.
- profundidad vertical normalizada, progreso de profundidad al inicio de cada episodio y duración de fases;
- matriz repetición × variable y síntesis de consistencia entre repeticiones;
- comparabilidad de profundidad y tempo, sin etiquetarlos como flexión anatómica de cadera.

### 9.3. Experto

- video anonimizado completo y por repetición;
- clasificación global por variable;
- confianza y observación;
- sin métricas, umbrales, intervalos ni recomendaciones antes del cierre.

## 10. Composición de interfaz con shadcn

No existe un componente estándar de shadcn que represente por sí solo varios intervalos dentro de una repetición. Se propone un componente de dominio `FindingTimeline` compuesto con:

- `Card` para la variable;
- `Badge` para estados;
- `Tabs` para cambiar de repetición;
- `Tooltip` para fase, rango y valor;
- `Button` para episodios que realizan seek;
- `Chart` solamente en la vista del investigador;
- `Alert` para incertidumbre o calidad insuficiente;
- `Skeleton` durante carga.

No usar `Progress`: comunica avance continuo, no episodios separados. No usar colores Tailwind crudos; usar tokens semánticos y variantes de componentes.

## 11. Reglas de lenguaje del usuario

### 11.1. Plantillas temporales

| Caso | Plantilla |
| --- | --- |
| ausente completo | “No se detectó durante el descenso, la máxima profundidad ni el ascenso.” |
| una fase | “Se detectó durante el descenso, entre {inicio} y {fin} s. No apareció en máxima profundidad ni en el ascenso.” |
| atraviesa el fondo | “Comenzó al final del descenso, estuvo presente en máxima profundidad y continuó durante el inicio del ascenso.” |
| episodios separados | “Apareció durante el descenso, no estuvo presente en máxima profundidad y reapareció durante el ascenso.” |
| limítrofe | “Se observó una desviación leve, pero no alcanzó el criterio definido para considerarla presente.” |
| no evaluable | “No fue posible evaluar este intervalo con suficiente calidad.” |
| intermitente | “Se observó un comportamiento intermitente durante esta fase.” |
| demasiado breve | “Se detectó una desviación muy breve, pero no duró lo suficiente para considerarla sostenida.” |
| repeticiones variables | “El resultado cambió entre repeticiones; revise el detalle de cada una.” |
| exposición diferente | “Las repeticiones alcanzaron profundidades diferentes y no ofrecen la misma exposición al movimiento.” |

### 11.2. Precisión terminológica

- `valgo proyectado` o `desviación medial proyectada`, no valgo anatómico confirmado;
- `diferencia bilateral de alineación`, no asimetría corporal general;
- `más abierta/lateral` para valores negativos;
- `más medial/entró más` para valores positivos;
- `compatible con` y `conviene contrastar`, no `causado por`;
- `prueba sugerida`, no diagnóstico automático.

## 12. Archivos de implementación probables

### Backend

- `src/squat/biomechanics.py`
  - baseline por rodilla;
  - deltas dinámicos;
  - diferencia bilateral con signo;
  - resúmenes por fase.
- `src/squat/models.py`
  - contratos de episodio, fase, peak y resumen temporal.
- `src/squat/rules.py`
  - histéresis, persistencia, episodios y agregación global.
- `src/squat/comparison.py`
  - ocurrencia frente a localización.
- `src/squat/exports.py`
  - nuevas columnas y textos.
- `config/squat/ruleset_*.json`
  - parámetros temporales versionados.
- esquemas y endpoints de API que serializan el reporte y la comparación.

### Frontend

- `apps/web/src/types/squat-case-report.ts`;
- `apps/web/src/types/squat-comparison.ts`;
- `apps/web/src/lib/squat-classification.ts`;
- `apps/web/src/app/(protected)/cases/[caseId]/page.tsx`;
- `apps/web/src/app/(protected)/cases/[caseId]/comparison/`;
- `apps/web/src/app/(protected)/expert/assignments/[assignmentId]/evaluation-form.tsx`;
- nuevo componente de dominio para timeline y resumen temporal.

La ruta `my-analyses/[analysisId]` no necesita duplicar lógica porque delega en `CaseDetailView`.

## 13. Orden de implementación recomendado

1. Agregar métricas derivadas y contratos sin cambiar clasificaciones.
2. Implementar resúmenes por fase y episodios detrás de pruebas unitarias.
3. Agregar agregación global y conservar peak como campo separado.
4. Separar coincidencia de ocurrencia y localización.
5. Actualizar exports y API.
6. Implementar timeline del investigador.
7. Implementar resumen narrativo del usuario.
8. Ajustar únicamente el lenguaje bilateral del formulario experto.
9. Incorporar recomendaciones mediante la matriz complementaria.
10. Agregar la síntesis opcional entre repeticiones sin alterar la validación por repetición.
11. Actualizar documentos metodológicos de la tesis.

## 14. Pruebas mínimas

### Backend

- episodio presente solo en descenso;
- episodio presente solo en ascenso;
- episodio que atraviesa máxima profundidad;
- peak por encima del umbral sin episodio sostenido que produce `no_concluyente`;
- peak presente como único frame que produce `no_concluyente`;
- tres frames continuos distribuidos entre descenso, peak y ascenso que producen `no_concluyente`;
- cuatro frames continuos que atraviesan peak y producen `presente`;
- cuatro frames no continuos que no se suman;
- señal de un frame que no activa episodio;
- señal de tres frames y menos de 0.16 s que queda como detección muy breve;
- episodio de 0.16 s en una fase menor de un segundo;
- dos detecciones breves separadas que no suman un episodio;
- episodio continuo que cruza descenso, peak y ascenso;
- hueco breve que se une;
- hueco unido que no se contabiliza como tiempo activo;
- hueco limítrofe válido que puede unirse frente a hueco de pose inválida que rompe el episodio;
- fase con cobertura global ≥80 % pero hueco inválido continuo capaz de ocultar 0.16 s, que queda `no_evaluable`;
- conversión de 0.16 s a cuatro muestras a ~25 fps y cinco muestras a 30 fps;
- hueco técnico largo que produce no evaluable;
- cambio de dirección que crea dos episodios;
- ambas rodillas mediales y simétricas;
- ambas laterales con izquierda más abierta;
- ambas laterales con derecha más abierta;
- izquierda medial y derecha lateral;
- diferencia bilateral presente con valgo ausente;
- valgo bilateral presente con diferencia bilateral ausente;
- coincidencia de ocurrencia con discrepancia de localización;
- una sola repetición sin síntesis comparativa visible;
- varias repeticiones consistentes;
- presente en una repetición y ausente/no concluyente en otra;
- direcciones opuestas entre repeticiones;
- compensaciones diferentes por repetición;
- repetición superficial cuyo rango no alcanza la profundidad de inicio del episodio de otra;
- repetición más profunda donde no reaparece una señal de la superficial.

### Frontend

- narración de cada caso temporal;
- timeline con intervalos separados;
- marcador de máxima profundidad;
- seek al pulsar un episodio;
- vista móvil y teclado;
- usuario sin frames técnicos;
- investigador con detalle completo;
- experto sin evidencia del sistema antes del cierre;
- etiqueta “más abierta” para el caso `seg_dos_rapidas`.
- narración de detección muy breve sin llamarla episodio;
- resumen `n de N` sin reemplazar tarjetas por repetición;
- advertencia de profundidades no comparables;
- ausencia de síntesis comparativa en videos de una repetición.

## 15. Criterios de aceptación

- La máxima profundidad permanece visible y auditable.
- La máxima profundidad no activa `presente` sin cumplir persistencia temporal.
- Cada variable puede reportar cero, uno o varios episodios.
- Los tiempos del usuario son relativos a la repetición y se muestran con una decimal.
- Los timestamps absolutos y frames permanecen disponibles al investigador.
- La diferencia bilateral muestra los valores de ambas rodillas.
- El caso `L=-25.01`, `R=-15.80` se expresa como “izquierda más abierta”.
- El formulario experto no exige fases.
- La comparación principal usa ocurrencia y la secundaria localización.
- No se muestra una recomendación de valgo cuando ambas rodillas son laterales y el valgo es ausente.
- Toda recomendación incluye prueba confirmatoria, retest, fuente y límite de interpretación.
- Los umbrales y parámetros temporales están versionados.
- Una detección menor de `0.16 s` se conserva, pero no crea un episodio sostenido.
- El 80 % de cobertura representa datos válidos, no tiempo con compensación.
- Una fase no puede clasificarse como ausente si contiene un hueco no observado capaz de ocultar un episodio completo, aunque alcance 80 % de cobertura total.
- `max_merge_gap_seconds` solo une muestras válidas dentro de la banda de histéresis; nunca rellena pose inválida.
- Dos apariciones breves separadas no se suman para alcanzar persistencia.
- La síntesis entre repeticiones nunca reemplaza la clasificación por repetición.
- La síntesis entre repeticiones no genera una recomendación combinada.
- Las métricas frontales de profundidad no se expresan como grados de flexión de cadera.

## 16. Documentación metodológica que deberá actualizarse

Después de implementar y validar:

- `docs/Plantilla_proyecto_de_tesis_completada.md` o su fuente vigente;
- `docs/matriz_operacionalizacion_variables_sentadilla.md`;
- `docs/evidencia_objetivo_3_variables_biomecanicas.md`;
- `docs/evidencia_objetivo_4_criterios_interpretables.md`;
- `docs/protocolo_aplicacion_instrumento3_expertos.md`;
- anexos e instrumentos derivados.

El cambio principal a declarar es que la serie completa deja de ser solamente evidencia gráfica y participa en la clasificación mediante episodios sostenidos, mientras máxima profundidad se conserva como ancla puntual descriptiva. Debe actualizarse expresamente la definición operacional: **un valor presente en un único fotograma de máxima profundidad ya no basta para clasificar la repetición como presente**; la señal debe satisfacer `present_min`, `0.16 s` y el mínimo de muestras correspondiente al FPS efectivo.

## 17. Límite clínico

Los resultados describen movimiento proyectado. No confirman Left AIC, PEC, debilidad glútea, restricción capsular, lesión de ligamento, patología de rodilla ni causa de dolor. Las recomendaciones de Conor Harris y Squat University se utilizarán como rutas educativas condicionadas por pruebas adicionales, según el documento complementario.
