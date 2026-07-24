# Evaluación del segundo lote piloto y comportamiento multietiqueta

## 1. Propósito

Este documento registra la evaluación exploratoria de los videos controlados
incorporados el 23 de julio de 2026. Se utilizó el conjunto de reglas
`0.1.0-provisional` sin emplear los nombres de archivo ni las etiquetas
intentadas como entrada del clasificador.

La comparación con el patrón intentado sirve para depuración y calibración. No
equivale a validación experta, no permite calcular desempeño final y no debe
presentarse como exactitud clínica.

## 2. Procesamiento

Cada video siguió el flujo:

1. extracción de pose 2D;
2. segmentación de repeticiones;
3. control de calidad analítica;
4. cálculo de variables biomecánicas;
5. aplicación del conjunto de reglas provisional;
6. revisión de `findings.json`, `rule_evidence.csv`, gráficos y overlays.

De los 12 videos nuevos, 11 fueron aptos para análisis. El caso
`dev_pelvis_der_002` fue excluido porque solo contiene o permite segmentar dos
repeticiones completas, mientras el protocolo exige tres.

## 3. Comparación con el patrón intentado

| Video | Patrón intentado | Resultado principal | Otros resultados | Concordancia exploratoria |
|---|---|---|---|---|
| `dev_negativo_002` | Sin patrón marcado | Todos los patrones ausentes | Ninguno | Exacta |
| `dev_pelvis_der_002` | Pelvis derecha | No clasificado: dos repeticiones | No aplica | No evaluable |
| `dev_pelvis_der_003` | Pelvis derecha | Pelvis derecha, -19,02 % | Tronco izquierdo; asimetría no concluyente | Exacta para el patrón principal |
| `dev_pelvis_izq_002` | Pelvis izquierda | Pelvis izquierda, 35,82 % | Tronco derecho; asimetría presente | Exacta para el patrón principal |
| `dev_pelvis_izq_003` | Pelvis izquierda | Pelvis izquierda, 29,05 % | Tronco derecho; asimetría presente | Exacta para el patrón principal |
| `dev_tronco_der_002` | Tronco derecho | Tronco derecho, -34,73° | Pelvis no concluyente; asimetría presente | Exacta para el patrón principal |
| `dev_tronco_der_003` | Tronco derecho | Tronco derecho, -38,75° | Pelvis no concluyente; asimetría presente | Exacta para el patrón principal |
| `dev_tronco_izq_002` | Tronco izquierdo | Tronco izquierdo, 41,50° | Pelvis no concluyente; asimetría presente | Exacta para el patrón principal |
| `dev_tronco_izq_003` | Tronco izquierdo | Tronco izquierdo, 46,66° | Asimetría presente | Exacta para el patrón principal |
| `dev_valgo_bilateral_001` | Valgo bilateral | Valgo izquierdo, 11,06 % | Asimetría presente | Parcial: no confirma bilateralidad |
| `dev_valgo_der_002` | Valgo derecho | Valgo derecho, 7,09 % | Asimetría presente | Exacta para el patrón principal |
| `dev_valgo_izq_002` | Valgo izquierdo | Valgo izquierdo, 21,37 % | Pelvis no concluyente; asimetría presente | Exacta para el patrón principal |

Entre los 11 videos clasificables, 10 reprodujeron exactamente el patrón
principal intentado. El caso restante reprodujo valgo, pero no de forma
bilateral. Esta proporción es una descripción exploratoria del lote y no una
métrica de desempeño.

## 4. Distancia respecto al umbral provisional

La distancia al umbral de presencia indica cuánto supera el valor medido la
banda provisional. No representa probabilidad ni confianza estadística.

| Caso positivo principal | Magnitud | Umbral de presencia | Margen |
|---|---:|---:|---:|
| Pelvis derecha 003 | 19,02 % | 8 % | 11,02 puntos porcentuales |
| Pelvis izquierda 002 | 35,82 % | 8 % | 27,82 puntos porcentuales |
| Pelvis izquierda 003 | 29,05 % | 8 % | 21,05 puntos porcentuales |
| Tronco derecho 002 | 34,73° | 12° | 22,73° |
| Tronco derecho 003 | 38,75° | 12° | 26,75° |
| Tronco izquierdo 002 | 41,50° | 12° | 29,50° |
| Tronco izquierdo 003 | 46,66° | 12° | 34,66° |
| Valgo derecho 002 | 7,09 % | 5 % | 2,09 puntos porcentuales |
| Valgo izquierdo 002 | 21,37 % | 5 % | 16,37 puntos porcentuales |

El valgo derecho es el caso positivo más próximo al umbral y merece nuevas
réplicas. Los patrones de tronco y pelvis fueron representados con magnitudes
claramente superiores a las bandas actuales.

## 5. Análisis de `dev_valgo_izq_002`

El sistema produjo:

- valgo izquierdo: `presente`;
- asimetría bilateral: `presente`;
- pelvis izquierda: `no_concluyente`;
- inclinación del tronco: `ausente`.

### 5.1 Valores por repetición

| Repetición | Pelvis (%) | Estado pelvis | Rodilla izquierda (%) | Estado valgo izquierdo |
|---|---:|---|---:|---|
| 1 | 5,57 | No concluyente | 21,37 | Presente |
| 2 | 1,81 | Ausente | 13,25 | Presente |
| 3 | 9,55 | Presente a la izquierda | 27,29 | Presente |

El desplazamiento pélvico se observa con mayor claridad en la tercera
repetición. La regla exige que al menos dos de tres repeticiones coincidan en
estado y dirección. Por ello, el resultado final de pelvis es
`no_concluyente`, aunque una repetición sí supere el umbral.

Esta salida es preferible a declarar presencia a partir del promedio o de una
sola repetición, porque conserva la variabilidad real del caso.

### 5.2 Presencia simultánea de patrones

El caso demuestra que un video puede producir varias salidas:

- un patrón específico positivo: valgo izquierdo;
- una consecuencia transversal positiva: asimetría bilateral;
- una señal adicional insuficientemente repetible: pelvis no concluyente.

El sistema no obliga a seleccionar una única clase. Cada patrón se evalúa
mediante una regla independiente y se conserva su propio estado.

## 6. Análisis del valgo bilateral

En `dev_valgo_bilateral_001`, la rodilla izquierda presentó desviación medial
positiva en las tres repeticiones. La rodilla derecha registró:

- repetición 1: 2,00 %, ausente por encontrarse en el límite inferior;
- repetición 2: -14,15 %, desviación lateral;
- repetición 3: -18,89 %, desviación lateral.

Por ello, el sistema detectó valgo izquierdo y no bilateral. Visualmente ambas
rodillas pueden parecer próximas al centro, pero la regla compara cada rodilla
con su propia línea cadera-tobillo. Conviene repetir este caso procurando que
ambas rodillas se desplacen medialmente respecto a esas referencias, no solo
que se aproximen entre sí.

## 7. Uso multietiqueta en los instrumentos

La plantilla de tesis no utiliza expresamente el término “clasificador
multietiqueta”, pero su estructura metodológica ya permite este comportamiento.

### Instrumento 2

Registra por video:

- los valores de las cuatro variables biomecánicas;
- el umbral aplicado;
- la clasificación de cada patrón;
- los estados ausente, presente o no concluyente.

Si se mantiene una sola columna denominada “Tipo de compensación detectada”,
los hallazgos pueden consignarse como una lista, por ejemplo:

`valgo izquierdo / asimetría bilateral / pelvis no concluyente`.

Para la exportación automática es preferible conservar una columna por patrón,
porque evita perder estados negativos o no concluyentes.

### Instrumento 3

Cada evaluador y el sistema clasifican por separado:

- tronco;
- pelvis;
- valgo;
- asimetría bilateral.

Una misma fila de video puede contener simultáneamente, por ejemplo:

- tronco: `derecha`;
- pelvis: `izquierda`;
- valgo: `ausente`;
- asimetría: `presente`.

No existe contradicción, porque esas columnas representan patrones distintos.

### Base interna de análisis

Para calcular métricas, cada video se desdobla en cuatro pares
`video-patrón`. Así, una clasificación correcta de valgo no compensa un error
en pelvis, y cada patrón obtiene su propia matriz de confusión y puntaje F1.

La redacción metodológica puede aclararse posteriormente con la siguiente
oración:

> Cada patrón será evaluado de manera independiente; por ello, un mismo video
> podrá recibir simultáneamente más de una clasificación positiva, y la unidad
> de comparación para el análisis será el par video-patrón.

## 8. Hallazgos para la siguiente calibración

1. No deben modificarse los umbrales a partir de este lote aislado.
2. La asimetría aparece en varios casos de tronco y valgo; debe revisarse con
   más negativos, casos aislados y evaluación visual antes de decidir si el
   umbral es sensible o si los patrones realmente coexisten.
3. El valgo derecho 002 requiere réplicas porque su margen sobre el umbral es
   reducido.
4. El valgo bilateral debe repetirse con control independiente de ambas
   rodillas.
5. Los videos no aptos deben conservarse como evidencia del control de calidad,
   pero no entrar a la evaluación de reglas.
