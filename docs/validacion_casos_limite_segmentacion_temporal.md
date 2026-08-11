# Validación de casos límite de segmentación temporal

## 1. Objetivo

Este documento registra la prueba de seis videos controlados destinados a evaluar si la detección de repeticiones depende de una velocidad simétrica o si falla ante pausas, ascensos lentos y oscilaciones en profundidad.

La señal utilizada fue el centro vertical de caderas suavizado (`hip_midpoint_y_smoothed`). En coordenadas de imagen, un valor mayor representa una posición más baja de la pelvis.

## 2. Regla evaluada

Para cada máximo local candidato `P`, la prominencia se calcula como:

```text
prominencia(P) = P - max(BI, BD)
```

`BI` y `BD` son los mínimos de la señal a la izquierda y derecha del candidato dentro de la ventana temporal. La prominencia mínima se obtiene una vez por video:

```text
rango robusto = P95(señal suavizada) - P05(señal suavizada)
prominencia mínima = max(0.03, 0.18 x rango robusto)
```

La versión inicial buscaba las bases hasta tres segundos a cada lado. La prueba comparó esa configuración con una ventana de hasta diez segundos, manteniendo sin cambios:

- la distancia mínima de dos segundos entre máximos;
- la validación de recuperación vertical entre máximos;
- la búsqueda del inicio y cierre mediante el 15 % de amplitud.

## 3. Resultados de los seis videos

| Video controlado | Resultado final | Hallazgo principal |
|---|---:|---|
| `segmentacion_ascenso_y_descenso_similares` | 3 repeticiones | Detectó correctamente ciclos con duraciones semejantes |
| `segmentacion_dos_repeticiones_ligeramente_rápidas` | 2 repeticiones | Detectó repeticiones rápidas sin fusionarlas |
| `segmentacion_dos_repeticiones_última_con_mayor_pausa_y_duración` | 2 repeticiones | Conservó el conteo y corrigió el segundo máximo de `11.47 s` a `12.23 s` |
| `segmentacion_tres_repeticiones_descenso_rápido_ascenso_ligeramente_lento` | 3 repeticiones | Aceptó un descenso de `0.60 s` y un ascenso de `4.17 s` |
| `segmentacion_tres_repeticiones_rápidas` | 3 repeticiones | Conservó ciclos de aproximadamente `1.13 s` |
| `segmentacion_una_repeticion_pausa_larga_máxima_profundidad` | 1 repetición | Corrigió el falso negativo de la ventana de tres segundos; pico en `12.56 s` |

## 4. Interpretación por escenario

### 4.1. Permanencia superior a tres segundos en profundidad

Con una ventana de tres segundos, ambos mínimos laterales podían quedar dentro de la meseta profunda. La diferencia `P - max(BI, BD)` resultaba menor que la prominencia mínima, aunque visualmente existiera un descenso y un retorno completos.

La ventana de diez segundos permitió alcanzar la zona alta anterior y posterior. No se añadió una regla especial para una pausa: se corrigió el horizonte usado para describir el entorno del máximo.

### 4.2. Ascenso más lento que el descenso

La prominencia no compara las duraciones de descenso y ascenso. Busca separación vertical. Por ello, un ascenso lento puede producir una base derecha más tardía sin invalidar el máximo, siempre que el retorno suficiente se encuentre dentro de la ventana.

La base conservadora puede cambiar de lado:

```text
base = max(BI, BD)
```

Si el ascenso todavía está en una posición intermedia, `BD` será relativamente alto y reducirá la prominencia. Esto es correcto: el candidato todavía no demuestra un retorno suficiente dentro del horizonte observado. Al ampliar el horizonte a la duración prevista de una ejecución controlada, el sistema puede encontrar el retorno posterior sin exigir simetría temporal.

### 4.3. Varios máximos dentro de una misma repetición

La distancia de dos segundos no basta por sí sola. Si dos máximos están separados por más de dos segundos, se calcula:

```text
recuperación(p1, p2) = min(señal[p1], señal[p2])
                       - min(señal entre p1 y p2)
```

Si la persona solo se acomoda en profundidad, el valle intermedio continúa cerca de ambos picos y la recuperación es pequeña. Los candidatos se fusionan y se conserva el más profundo. Si la persona retorna suficientemente y vuelve a descender, la recuperación supera el mínimo y se reconocen dos repeticiones.

### 4.4. Repeticiones rápidas

Las repeticiones rápidas probadas conservaron picos separados. El límite relevante no fue la ventana de prominencia, sino la distancia mínima de dos segundos entre máximos de profundidad. Una ejecución extrema con picos separados por menos de dos segundos podría fusionarse; no forma parte del ritmo recomendado para la muestra formal.

## 5. Cálculo del valor 0.03 en el caso del error previo

En `dev_case_1784949757322`, equivalente al video controlado de desplazamiento pélvico, la señal suavizada completa produjo:

```text
P05 = 0.512280
P95 = 0.673052
rango robusto = 0.160772
18 % del rango = 0.028939
prominencia mínima = max(0.03, 0.028939) = 0.03
```

No se eligió una repetición ni un pico para calcular este valor. Los percentiles provienen de todas las muestras de la señal suavizada del video. El umbral global resultante se aplica después a cada candidato y a cada recuperación entre candidatos.

## 6. Decisión técnica y metodológica

Se amplió `peak_window_seconds` de `3.0` a `10.0`. La comparación sobre 40 señales previamente procesadas produjo:

- 38 señales sin cambio de conteo ni de máximos;
- una señal con el mismo conteo y corrección del fotograma de máxima profundidad;
- una señal que corrigió un falso negativo de cero a una repetición.

El protocolo mantiene una repetición continua, controlada y con retorno completo. La referencia de dos segundos de descenso y dos de ascenso sirve para estandarizar la captura, pero no se exige igualdad exacta ni se descarta automáticamente una repetición solo por presentar duraciones diferentes.

Una pausa deliberadamente prolongada, un retorno incompleto o acomodaciones repetidas deben motivar la repetición del intento en la muestra formal. El sistema puede detectar varios de esos casos, pero su aceptación metodológica no debe depender únicamente de que el algoritmo produzca una segmentación.

## 7. Evidencia reproducible

Los artefactos de prueba se generaron en:

```text
D:/sentadilla-biomecanica-release/output/segmentation-edge-cases/
```

La implementación y sus pruebas de regresión se encuentran en:

- `D:/sentadilla-biomecanica-release/src/squat/segmentation.py`;
- `D:/sentadilla-biomecanica-release/tests/squat/test_segmentation.py`.

