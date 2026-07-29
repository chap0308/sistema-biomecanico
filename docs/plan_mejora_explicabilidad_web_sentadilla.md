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

### 2.1. Doble representación de la evidencia

La visualización interactiva no reemplazará los artefactos generados por Python. Se mantendrán dos representaciones del mismo análisis:

| Representación | Propósito | Tratamiento |
|---|---|---|
| PNG, CSV, JSON, Excel y videos | Evidencia reproducible, trazabilidad y descarga | Se generan en `outputs`, se almacenan en los buckets y permanecen disponibles para descarga |
| Gráficas y tablas web | Lectura, exploración y explicación del resultado | Se renderizan con datos JSON acotados derivados de los mismos artefactos |

Por tanto, `pose_quality.png`, `segmentation.png` y `biomechanical_metrics.png` deben seguir generándose, almacenándose y descargándose. Sin embargo, no serán la única ni necesariamente la principal forma de consultar esos datos en la interfaz. La web mostrará por defecto su equivalente interactivo y ofrecerá una acción secundaria como “Descargar gráfico original (PNG)”.

Las imágenes y videos que contienen evidencia visual del participante, como overlays, capturas de fotogramas clave y videos anonimizados, sí deben conservarse como medios visuales. No corresponde sustituirlos por una gráfica.

### 2.2. Criterio de componentes y complejidad

Se utilizarán componentes shadcn existentes para `Card`, `Tabs`, `Table`, `Badge`, `Progress`, `Skeleton`, `Button` y paginación. Para las gráficas se incorporará el componente `Chart` de shadcn y su dependencia mínima de visualización, previsiblemente Recharts, cuando comience ese incremento.

No se incorporarán inicialmente Zustand, TanStack Query ni una capa adicional de estado global. La página del caso cargará los datos iniciales desde un Server Component de Next.js y limitará el código cliente a la isla interactiva que sincroniza video, pestaña, repetición, cursor y gráfica. Esta decisión evita duplicar caché, estado y solicitudes sin una necesidad demostrada.

El criterio visual será de divulgación técnica y no de tablero saturado: una evidencia principal, una variable seleccionada y detalle progresivo. Los componentes de shadcn se usarán donde aporten estructura o accesibilidad, no como obligación para cada elemento.

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

Debajo de estas tarjetas, sustituir la imagen estática como vista principal por una gráfica interactiva de calidad:

- porcentaje de puntos críticos detectados por fotograma;
- visibilidad mínima observada;
- línea horizontal del umbral de visibilidad;
- bandas o marcas para fotogramas válidos y no válidos;
- cursor sincronizado con el reproductor.

`pose_quality.png` permanecerá disponible en “Artefactos técnicos” y como descarga. La gráfica web se construirá con una serie acotada procedente de `frame_quality.csv`, sin recalcular la validez en TypeScript.

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

La gráfica debe implementarse con el componente `Chart` de shadcn, una línea principal suavizada y, solo cuando el usuario solicite detalle técnico, una línea secundaria tenue con `hip_midpoint_y` sin suavizar. Esto permite explicar la reducción de ruido sin mostrar ambas señales permanentemente.

`hip_midpoint_y` no constituye una compensación ni una variable biomecánica final. Es una señal intermedia de segmentación temporal que permite:

- localizar descenso, máxima profundidad y ascenso;
- separar repeticiones;
- justificar los fotogramas elegidos para calcular las variables;
- sincronizar el video con el proceso interno.

Para una audiencia no técnica, el eje puede denominarse “posición vertical del centro de caderas” y debe indicarse que en coordenadas de imagen el valor aumenta hacia abajo.

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

La pestaña seleccionada será el único foco geométrico visible sobre el video o la captura. Junto al medio se mostrará un overlay compacto con el valor instantáneo, la unidad y el estado de calidad. Esta combinación evita dibujar simultáneamente tronco, pelvis y ambas geometrías de rodilla.

La gráfica asociada a la pestaña mostrará únicamente las series necesarias:

| Pestaña | Series |
|---|---|
| Tronco | inclinación lateral del tronco |
| Pelvis | desplazamiento lateral normalizado |
| Rodillas | desviación medial izquierda y derecha |
| Diferencia bilateral | diferencia absoluta entre ambas alineaciones |

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

La implementación web priorizará la tercera opción antes de generar un video técnico más complejo. La selección de una pestaña controlará tanto la geometría destacada como la gráfica y la tabla resumida. El video mantendrá solamente un overlay compacto y legible.

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
  ],
  "chart_series": {
    "quality": [],
    "segmentation": [],
    "biomechanics": []
  },
  "artifact_downloads": [],
  "table_previews": []
}
```

El contrato debe incluir:

- series temporales necesarias para gráficas;
- geometría de los fotogramas clave;
- valores bilaterales;
- reglas y umbrales;
- rutas de artefactos;
- versión del pipeline.

También debe diferenciar:

- `chart_series`: puntos temporales necesarios para renderizar gráficas;
- `table_previews`: filas seleccionadas, paginadas o resumidas para lectura web;
- `artifact_downloads`: archivos completos disponibles para descarga;
- `key_frame_geometry`: coordenadas explicativas del fotograma seleccionado.

Las series deben incluir `frame_index` y `time_seconds` como claves comunes. Cuando el volumen sea alto, la API podrá reducir puntos exclusivamente para visualización, conservando siempre eventos, máximos, mínimos y cambios de fase. Los CSV originales no se alterarán.

No debe incluir:

- video original sin anonimizar;
- resultados del sistema en endpoints accesibles al experto;
- fórmulas duplicadas o recalculadas en TypeScript.

## 10. Fuentes por componente web

| Componente | Fuente canónica | Representación web |
|---|---|---|
| Reproductor de pose | `overlay.mp4` | Video |
| Reproductor experto | `review.mp4` | Video |
| Calidad en tiempo real | `frame_quality.csv` | Gráfica sincronizada y resumen |
| Puntos y coordenadas | `landmarks.csv` | Overlay y tabla técnica acotada |
| Línea temporal | `frame_phases.csv` | Línea temporal y gráfica |
| Eventos | `segmentation_summary.json` | Marcadores de inicio, profundidad y final |
| Valores instantáneos | `biomechanical_frame_metrics.csv` | Gráfica por variable |
| Resumen por repetición | `biomechanical_summary.json` | Tarjetas y tabla |
| Umbrales y estados | `findings.json` y `rule_evidence.csv` | Bandas de decisión y trazabilidad |
| Vista agregada | `case_report.json` | Resumen del caso |
| Gráficos archivables | PNG generados por el pipeline | Descarga y vista secundaria |

En producción, la API debe convertir estas fuentes a JSON acotado y tipado. El navegador no debería descargar y combinar todos los CSV directamente.

### 10.1. Tablas y descargas

Los CSV continuarán siendo artefactos técnicos completos, pero la web no debe presentarlos como texto crudo ni cargar todas sus filas. Se ofrecerán:

1. una tabla resumida por repetición con variables, lados, unidades y estados;
2. una vista técnica paginada con una selección de columnas relevantes;
3. filtros por repetición, fase o variable cuando correspondan;
4. descarga del CSV original;
5. descarga en Excel cuando el flujo de exportación del instrumento lo requiera.

La tabla de landmarks no debe listar por defecto todos los puntos de todos los fotogramas. La vista inicial mostrará el fotograma seleccionado, los puntos críticos usados y su visibilidad. El archivo completo seguirá disponible como descarga.

Para `biomechanical_frame_metrics.csv`, la tabla técnica puede mostrar:

| Campo | Utilidad visible |
|---|---|
| Tiempo y fotograma | Relacionar fila, gráfica y video |
| Repetición y fase | Ubicar el momento analizado |
| Tronco y pelvis | Mostrar valor instantáneo y dirección |
| Rodilla izquierda y derecha | Evitar ocultar la bilateralidad |
| Diferencia bilateral | Explicar la cuarta variable |

El formateo incorrecto de un CSV en una hoja de cálculo no debe resolverse modificando su contenido científico. La exportación debe conservar UTF-8, separador consistente y tipos numéricos; la interfaz y el archivo Excel serán las representaciones orientadas a lectura.

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

### Incremento 3. Gráficas y tablas interactivas

- incorporar `Chart` de shadcn con una sola dependencia de gráficos;
- reemplazar como vista principal `pose_quality.png`, `segmentation.png` y `biomechanical_metrics.png`;
- mantener PNG, CSV y JSON en almacenamiento y descarga;
- mostrar tablas resumidas y vistas técnicas paginadas;
- cargar cada bloque explicativo bajo `Suspense` con `Skeleton`, manteniendo la obtención inicial de datos en el servidor;
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
- los puntos de las gráficas reproducen las series canónicas dentro de la precisión de presentación;
- la reducción de puntos no elimina eventos ni extremos relevantes;
- los enlaces de descarga corresponden a los artefactos almacenados;
- no se exponen resultados a expertos.

### Frontend

- seleccionar una repetición actualiza captura, fórmula y valores;
- el cursor de la gráfica sigue el video;
- cambiar de pestaña actualiza gráfica, geometría y tabla sin alterar el video;
- las tablas técnicas no cargan el CSV completo en el navegador;
- los PNG originales y archivos tabulares permanecen descargables;
- estados vacíos, carga y error usan componentes accesibles;
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
7. consulta una tabla técnica acotada;
8. descarga el PNG y el archivo tabular originales;
9. experto verifica que no puede acceder a estos resultados.

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
2. crear el contrato de explicación con series, tablas acotadas y descargas;
3. sustituir las imágenes de gráficos como vista principal por gráficas y tablas interactivas;
4. sincronizar video, repetición, pestaña y cursor;
5. añadir geometría sobre capturas o video según la pestaña seleccionada;
6. generar el video técnico continuo solo si las evidencias anteriores no resultan suficientes.

Así se obtiene valor demostrativo desde el primer incremento, se conservan los artefactos reproducibles y se evita duplicar cálculos en el frontend. El video técnico queda como mejora posterior porque la combinación de reproductor, gráfica, tabla y geometría seleccionada puede cubrir la explicación con menor complejidad.

## 15. Estado de implementación

Los cinco incrementos quedaron implementados en la rama de desarrollo:

1. **Corrección informativa:** las tarjetas muestran bilateralidad de rodillas, unidad metodológica, fórmula, convención de signo y versión de reglas.
2. **Contrato de explicación:** `GET /squat/cases/{case_id}/explanation` entrega series acotadas, repeticiones, decisiones, geometría de fotogramas clave y artefactos descargables sin recalcular métricas.
3. **Gráficas y tablas:** la vista del caso representa calidad, segmentación, variables y reglas mediante componentes shadcn y Recharts. Los datos se filtran por repetición y el cursor sigue el tiempo del video.
4. **Evidencia geométrica:** la pestaña seleccionada muestra un esquema normalizado de tronco, pelvis, rodillas o diferencia bilateral a máxima profundidad. Los centros y proyecciones se calculan en Python.
5. **Video técnico:** el pipeline genera `analysis_overlay.mp4` con repetición, fase, calidad, valores instantáneos y cantidad de reglas presentes. El archivo se codifica en H.264, se declara en el reporte y se almacena como artefacto privado.
6. **Inspección en máxima profundidad:** al seleccionar el evento de máxima profundidad, el reproductor posiciona el video en el instante correspondiente y lo mantiene en pausa para facilitar la revisión de la geometría y su contraste con las gráficas.
7. **Sincronización por repetición:** el tiempo del video determina automáticamente la repetición activa. La navegación persistente dentro de Trazabilidad permite avanzar, retroceder o seleccionar una ejecución y actualiza de forma conjunta gráficas, tablas, geometría y reglas. Cada gráfica marca el inicio, la máxima profundidad y el final de la repetición.

Las imágenes `pose_quality.png`, `segmentation.png` y `biomechanical_metrics.png`, los CSV, los JSON y los videos anteriores permanecen en `outputs` y en almacenamiento. La web usa representaciones interactivas como vista principal y conserva los archivos originales para auditoría y descarga.

La validación real se ejecutó sobre `dev_case_1784949788300`. El video técnico resultante conservó la resolución `478 × 850`, una frecuencia aproximada de `29.86 FPS` y codec H.264.

La verificación E2E local cubre autenticación, registro asistido de un caso, consulta de resultados y evaluación ciega por un experto. Playwright se ejecuta con grabación habilitada para conservar evidencia audiovisual de cada recorrido.
