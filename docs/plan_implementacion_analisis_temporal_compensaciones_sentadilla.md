# Plan de implementación del análisis temporal de compensaciones en sentadilla

## 1. Propósito

Este documento especifica la siguiente evolución del sistema de sentadilla bilateral:

1. conservar el resultado del fotograma de máxima profundidad;
2. analizar también el descenso y el ascenso completos;
3. representar apariciones sostenidas como intervalos temporales, no como una lista de fotogramas;
4. mantener una clasificación global simple y comparable con la evaluación experta;
5. mostrar diferente nivel de detalle al usuario, investigador y experto;
6. precisar la diferencia bilateral de rodillas sin confundir apertura lateral con valgo;
7. habilitar recomendaciones condicionadas por combinaciones observables, sin convertir la salida 2D en un diagnóstico.

La implementación debe mantener el alcance de la tesis: detectar **compensaciones y asimetrías cinemáticas observables en vista frontal 2D**. No debe afirmar rotaciones tridimensionales, patologías o causas anatómicas.

## 2. Decisiones cerradas

### 2.1. Unidad de análisis y validación

- La unidad continúa siendo `repetición × variable`.
- Cada repetición se clasifica de manera independiente.
- No se combinan varias repeticiones para producir una sola etiqueta del video.
- El experto emite una clasificación global por variable y repetición.
- El experto no debe anotar fases ni tiempos exactos.
- El sistema sí conserva fases, intervalos y máxima profundidad como evidencia descriptiva.

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
- cobertura mínima de datos válidos por fase.

Todos deben residir en el ruleset y nunca quedar ocultos en componentes web.

### 2.4. Resultado global del sistema

Por variable y repetición:

```text
presente
  si existe al menos un episodio sostenido presente en descenso o ascenso,
  o si el resultado puntual de máxima profundidad es presente;

ausente
  si descenso, máxima profundidad y ascenso son evaluables,
  no existe ningún episodio presente
  y no existe evidencia limítrofe relevante;

no_concluyente
  si no existe evidencia presente,
  pero hay una banda limítrofe, cobertura insuficiente o datos no finitos.
```

Un intervalo técnicamente no evaluable nunca se convierte en `ausente`.

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
4. unir interrupciones técnicas o limítrofes menores que `max_gap_seconds`;
5. cerrar el episodio si cambia de dirección de manera sostenida;
6. marcar los huecos de mala calidad como `no_evaluable`, no como ausencia.

Parámetros iniciales de ingeniería, pendientes de calibración:

```text
min_episode_duration_seconds: 0.12–0.16
max_merge_gap_seconds: 0.08
```

Se expresarán en segundos para no depender de una frecuencia fija. Los valores definitivos deben validarse y congelarse antes de la evaluación formal.

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
- `phase_missing`.

La interfaz no mostrará todos estos términos al usuario, pero el investigador y los exports sí.

## 7. Evaluación experta

### 7.1. El formulario no requiere fases

El experto observará la repetición completa en bucle y responderá una vez por variable. La instrucción debe decir:

> Clasifique la variable como presente si la observa en cualquier momento de la repetición, incluida la máxima profundidad. No es necesario indicar la fase ni el instante exacto.

Esto alinea el alcance del experto con el nuevo resultado global del sistema.

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
10. Actualizar documentos metodológicos de la tesis.

## 14. Pruebas mínimas

### Backend

- episodio presente solo en descenso;
- episodio presente solo en ascenso;
- episodio que atraviesa máxima profundidad;
- peak presente sin episodio sostenido;
- señal de un frame que no activa episodio;
- hueco breve que se une;
- hueco técnico largo que produce no evaluable;
- cambio de dirección que crea dos episodios;
- ambas rodillas mediales y simétricas;
- ambas laterales con izquierda más abierta;
- ambas laterales con derecha más abierta;
- izquierda medial y derecha lateral;
- diferencia bilateral presente con valgo ausente;
- valgo bilateral presente con diferencia bilateral ausente;
- coincidencia de ocurrencia con discrepancia de localización.

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

## 15. Criterios de aceptación

- La máxima profundidad permanece visible y auditable.
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

## 16. Documentación metodológica que deberá actualizarse

Después de implementar y validar:

- `docs/Plantilla_proyecto_de_tesis_completada.md` o su fuente vigente;
- `docs/matriz_operacionalizacion_variables_sentadilla.md`;
- `docs/evidencia_objetivo_3_variables_biomecanicas.md`;
- `docs/evidencia_objetivo_4_criterios_interpretables.md`;
- `docs/protocolo_aplicacion_instrumento3_expertos.md`;
- anexos e instrumentos derivados.

El cambio principal a declarar es que la serie completa deja de ser solamente evidencia gráfica y participa en la clasificación mediante episodios sostenidos, mientras máxima profundidad se conserva como ancla puntual.

## 17. Límite clínico

Los resultados describen movimiento proyectado. No confirman Left AIC, PEC, debilidad glútea, restricción capsular, lesión de ligamento, patología de rodilla ni causa de dolor. Las recomendaciones de Conor Harris y Squat University se utilizarán como rutas educativas condicionadas por pruebas adicionales, según el documento complementario.
