# Plan de mejora de explicabilidad para la web de sentadilla

## 1. Objetivo

La vista actual presenta el video overlay, eventos temporales y resultados por repetición. La mejora propuesta debe convertir esa información en una demostración comprensible del funcionamiento interno del sistema.

La interfaz debe responder, en orden:

1. ¿El video fue técnicamente utilizable?
2. ¿Dónde detectó el sistema los puntos anatómicos?
3. ¿Cómo separó las repeticiones?
4. ¿Qué geometría utilizó para calcular cada variable?
5. ¿Qué valor obtuvo en cada repetición y lado?
6. ¿Qué umbral aplicó?
7. ¿Por qué produjo la clasificación final?

La fuente de referencia para el ejemplo es `analisis_caso_dev_valgo_izq_002_fases_2_5.md`.

## 2. Principio de diseño

No conviene mostrar todos los datos al mismo tiempo. La vista debe tener dos niveles:

- **Resumen:** compensaciones detectadas, repetición y estado de calidad.
- **Cómo se calculó:** explicación progresiva de las fases 2, 3, 4 y 5.

El usuario debe poder entender el resultado sin abrir CSV, pero también debe poder llegar hasta la evidencia técnica original.

## 3. Estructura propuesta dentro de `/cases/[id]`

### 3.1. Resultado principal

Mantener:

- reproductor;
- selector de repetición;
- cuatro patrones por repetición;
- estado `presente`, `ausente` o `no concluyente`;
- valor y umbral.

Corregir:

- valgo debe mostrar valor izquierdo y derecho;
- asimetría debe mostrar ambos valores de rodilla y su diferencia;
- los porcentajes deben etiquetarse como “% del ancho inicial de hombros”, no como confianza;
- incluir la versión del conjunto de reglas.

### 3.2. Nueva sección: “Cómo se obtuvo este resultado”

Utilizar un selector de cuatro pasos:

```text
1. Pose 2D -> 2. Segmentación -> 3. Variables -> 4. Reglas
```

Cada paso debe tener:

- explicación breve;
- evidencia visual;
- valores del caso;
- enlace a “Ver detalle técnico”.

## 4. Paso web de Fase 2: pose y calidad

### 4.1. Reproductor de pose

Mostrar `overlay.mp4` con:

- puntos y segmentos;
- estado del fotograma;
- pixelado facial;
- fotograma actual;
- cantidad de puntos detectados;
- visibilidad mínima.

### 4.2. Tarjetas didácticas

| Tarjeta | Ejemplo |
|---|---|
| Fotogramas procesados | 662 de 662 |
| Fotogramas válidos | 100 % |
| Puntos seleccionados | 13 |
| Promedio detectado | 13 de 13 |
| Umbral de visibilidad | 0.50 |
| Mínimo observado | 0.9217 |

### 4.3. Mejora del overlay de calidad

El overlay actual cambia el color del esqueleto completo:

- verde: válido;
- naranja: revisión.

Mejora recomendada:

- conservar color general;
- colorear individualmente en rojo o naranja el punto que incumple;
- mostrar su nombre y visibilidad;
- mostrar qué referencia distal permitió o impidió validar el lado;
- incorporar una pequeña barra `visibilidad actual / umbral 0.50`.

Esto permite explicar por qué un fotograma fue rechazado, no solo informar que fue rechazado.

### 4.4. Advertencia metodológica

Mostrar un texto breve:

> La visibilidad indica disponibilidad estimada por MediaPipe; no equivale a error anatómico ni a precisión clínica. La coherencia se revisa mediante overlay y la clasificación final se valida frente a expertos.

## 5. Paso web de Fase 3: segmentación

### 5.1. Línea temporal interactiva

Debajo del video:

- reposo: gris;
- descenso: azul;
- máxima profundidad: marcador destacado;
- ascenso: verde;
- cierre: gris oscuro;
- fotogramas inválidos: rojo.

El selector de repetición debe mover el video al inicio o a máxima profundidad.

### 5.2. Curva sincronizada

Representar `hip_midpoint_y_smoothed` mediante una gráfica de línea:

- cursor sincronizado con `video.currentTime`;
- banda sombreada por repetición;
- marcadores R1, R2, R3;
- etiquetas de inicio, profundidad y final.

### 5.3. Explicación visual

Mostrar:

```text
centro de caderas =
    (cadera izquierda + cadera derecha) / 2
```

En el video o captura:

- dibujar ambos puntos de cadera;
- dibujar el punto medio;
- dibujar una línea horizontal de referencia para observar el descenso;
- indicar que `y` aumenta hacia abajo.

## 6. Paso web de Fase 4: geometría y variables

### 6.1. Selector de variable

Usar pestañas:

1. tronco;
2. pelvis;
3. rodillas;
4. diferencia bilateral.

Cada pestaña modifica:

- explicación;
- líneas sobre la imagen;
- fórmula;
- gráfica;
- valores de la repetición.

### 6.2. Overlay geométrico para tronco

Dibujar en el fotograma:

- centro de hombros `S`;
- centro de pelvis `P`;
- segmento `S-P`;
- vertical de referencia desde `P`;
- arco del ángulo;
- signo y dirección anatómica.

Panel:

```text
theta = atan2(Sx - Px, Py - Sy)
Repetición 3: 12.376° hacia la izquierda
Umbral de presencia: 12°
Resultado: presente
```

### 6.3. Overlay geométrico para pelvis

Dibujar:

- centro de pelvis `P`;
- centro de tobillos `A`;
- vertical del centro de apoyo;
- posición inicial corregida;
- flecha horizontal entre referencia y posición actual.

Panel:

```text
100 x (offset actual - offset inicial) / W0
Repetición 3: 9.546 % hacia la izquierda
Umbral de presencia: 8 %
Resultado: presente
```

### 6.4. Overlay geométrico para rodillas

Este es el cambio visual más importante.

Por cada lado:

- línea cadera-tobillo;
- punto de rodilla esperado sobre esa línea;
- punto de rodilla real;
- flecha desde el esperado al real;
- color según dirección:
  - medial positiva: rojo si supera presencia;
  - banda intermedia: ámbar;
  - lateral o ausencia: azul/gris.

Panel obligatorio:

| Lado | Valor | Interpretación | Estado |
|---|---:|---|---|
| Izquierdo | 27.285 % | Medial | Presente |
| Derecho | -37.385 % | Lateral | Ausente |

Resultado:

```text
Valgo dinámico visible izquierdo
```

No debe mostrarse solamente `27.285 %`, porque ocultaría cómo fue evaluado el lado derecho.

### 6.5. Overlay de diferencia bilateral

Mostrar:

```text
|27.285 - (-37.385)| = 64.671 %
```

La interfaz debe aclarar:

> La diferencia bilateral compara las alineaciones de ambos lados. No significa que ambas rodillas presenten valgo.

### 6.6. Fórmula sustituida con valores reales

Cada variable debe permitir desplegar:

1. fórmula general;
2. definición de símbolos;
3. valores utilizados;
4. operación resultante;
5. unidad;
6. convención de signo.

Esto es más defendible que presentar únicamente la fórmula abstracta.

## 7. Paso web de Fase 5: regla y clasificación

### 7.1. Barra de tres bandas

Representar:

```text
Ausente | No concluyente | Presente
```

Ejemplo para pelvis:

```text
0------5 % | 5------8 % | 8 % en adelante
                         ^
                       9.546 %
```

La barra no debe denominarse “confianza”.

### 7.2. Tarjeta de trazabilidad

Por repetición y patrón:

| Campo | Contenido |
|---|---|
| Variable | `pelvis_shift_at_peak_pct` |
| Valor | 9.546 % |
| Unidad | % del ancho inicial de hombros |
| Límite de ausencia | 5 % |
| Límite de presencia | 8 % |
| Estado | Presente |
| Dirección | Izquierda |
| Versión | `0.2.0-provisional` |

### 7.3. Multietiqueta

La interfaz debe explicar:

> Las cuatro reglas son independientes. Una repetición puede presentar más de una compensación observable.

La repetición 3 del caso de ejemplo debe mostrarse como demostración:

- inclinación del tronco: presente;
- desplazamiento de pelvis: presente;
- valgo izquierdo: presente;
- asimetría bilateral: presente.

## 8. Video técnico mejorado

### 8.1. Tres videos con funciones distintas

| Video | Usuario | Contenido |
|---|---|---|
| `review.mp4` | Experto | Movimiento anonimizado, sin salida del sistema |
| `overlay.mp4` | Investigador | Puntos, esqueleto y calidad |
| `analysis_overlay.mp4` propuesto | Asesor/jurado/investigador | Fase, referencias geométricas, valores y estados |

El experto no debe acceder al overlay técnico antes de enviar su evaluación.

### 8.2. Contenido del `analysis_overlay.mp4`

Una versión inicial puede incluir:

- repetición y fase actual;
- centro de caderas;
- máxima profundidad;
- valor instantáneo de tronco;
- valor instantáneo de pelvis;
- valor izquierdo y derecho de rodilla;
- diferencia bilateral;
- bandas o estados de las reglas;
- color de calidad del fotograma.

### 8.3. Evitar saturación visual

No conviene dibujar todas las fórmulas permanentemente sobre el video.

Alternativas:

- overlay compacto con valores en tiempo real;
- pestaña seleccionada para destacar una geometría;
- pausa automática en máxima profundidad;
- captura explicativa detallada por variable.

Ruta mínima recomendada:

1. overlay compacto continuo;
2. capturas geométricas detalladas en máxima profundidad;
3. gráficas sincronizadas en la web.

## 9. Contrato de datos recomendado

La interfaz no debe recalcular las fórmulas biomecánicas. Python debe seguir siendo la fuente de verdad.

Agregar un contrato de explicación por caso, por ejemplo:

```text
GET /squat/cases/{case_id}/explanation
```

Contenido:

```json
{
  "quality": {
    "threshold": 0.5,
    "processed_percentage": 100.0,
    "valid_percentage": 100.0
  },
  "segmentation": {
    "signal": "hip_midpoint_y",
    "repetitions": []
  },
  "normalization": {
    "reference": "initial_shoulder_width",
    "value": 0.258264
  },
  "repetitions": [
    {
      "repetition_index": 3,
      "peak_frame": 592,
      "peak_seconds": 24.627597,
      "geometry": {},
      "metrics": {},
      "decisions": []
    }
  ]
}
```

El contrato debe incluir:

- series temporales necesarias para gráficas;
- geometría de los fotogramas clave;
- valores bilaterales;
- reglas y umbrales;
- rutas de artefactos;
- versión del pipeline.

No debe incluir:

- video original sin anonimizar;
- resultados del sistema en endpoints accesibles al experto;
- fórmulas duplicadas o recalculadas en TypeScript.

## 10. Fuentes por componente web

| Componente | Fuente |
|---|---|
| Reproductor de pose | `overlay.mp4` |
| Reproductor experto | `review.mp4` |
| Calidad en tiempo real | `frame_quality.csv` |
| Puntos y coordenadas | `landmarks.csv` |
| Línea temporal | `frame_phases.csv` |
| Eventos | `segmentation_summary.json` |
| Valores instantáneos | `biomechanical_frame_metrics.csv` |
| Resumen por repetición | `biomechanical_summary.json` |
| Umbrales y estados | `findings.json` y `rule_evidence.csv` |
| Vista agregada | `case_report.json` |

En producción, la API debe convertir estas fuentes a JSON acotado y tipado. El navegador no debería descargar y combinar todos los CSV directamente.

## 11. Fases de implementación

### Incremento 1. Corrección informativa

- mostrar valores de rodilla izquierda y derecha;
- aclarar unidades;
- agregar fórmulas y reglas desplegables;
- agregar versión del conjunto de reglas;
- agregar explicación multietiqueta.

### Incremento 2. Endpoint de explicación

- construir contrato Pydantic;
- generar geometría de fotogramas clave;
- exponer series temporales acotadas;
- validar consistencia contra CSV y JSON existentes;
- proteger permisos por rol.

### Incremento 3. Gráficas sincronizadas

- cursor ligado al tiempo del video;
- segmentación por colores;
- selector de repetición;
- selector de variable;
- comparación bilateral de rodillas.

### Incremento 4. Evidencia geométrica

- líneas de referencia;
- puntos reales y esperados;
- arcos y flechas;
- capturas explicativas por repetición y variable.

### Incremento 5. Video técnico

- generar `analysis_overlay.mp4`;
- validar codec H.264;
- agregarlo al reporte y almacenamiento;
- mantener `review.mp4` sin información del sistema.

## 12. Pruebas necesarias

### Backend

- la geometría explicativa reproduce los valores de `biomechanical_frame_metrics.csv`;
- cada repetición contiene cuatro decisiones;
- valgo conserva ambos lados;
- series y eventos usan el mismo índice de fotograma;
- no se exponen resultados a expertos.

### Frontend

- seleccionar una repetición actualiza captura, fórmula y valores;
- el cursor de la gráfica sigue el video;
- las unidades se muestran correctamente;
- un porcentaje nunca se etiqueta como confianza;
- un caso no apto no muestra compensaciones;
- un informe legado solicita reprocesamiento;
- la vista móvil mantiene legibilidad.

### Playwright

1. investigador abre un caso completo;
2. selecciona repetición 3;
3. abre “Rodillas”;
4. observa valores izquierdo y derecho;
5. reproduce desde máxima profundidad;
6. abre la fórmula sustituida;
7. descarga la evidencia técnica;
8. experto verifica que no puede acceder a estos resultados.

## 13. Relación con los objetivos específicos

| Elemento web | Evidencia |
|---|---|
| Overlay y calidad | Objetivo 1 |
| Segmentación sincronizada | Evidencia habilitadora del Objetivo 2 |
| Fórmulas y geometría | Objetivo 2 |
| Bandas y reglas | Objetivo 3 |
| Flujo integrado por caso | Objetivo 4 |
| Comparación posterior con expertos | Objetivo 5 |

## 14. Prioridad recomendada

La siguiente mejora no debería comenzar generando un video complejo. El orden más seguro es:

1. exponer bilateralidad, unidades, fórmulas y reglas en la vista actual;
2. crear el contrato de explicación;
3. añadir gráficas sincronizadas;
4. añadir geometría sobre capturas;
5. generar el video técnico continuo.

Así se obtiene valor demostrativo desde el primer incremento y se evita duplicar cálculos en el frontend.

