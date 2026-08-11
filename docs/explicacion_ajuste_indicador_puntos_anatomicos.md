# Explicación del ajuste del indicador de puntos anatómicos clave detectados

## 1. Motivo del documento

Este documento explica el ajuste realizado al indicador inicialmente denominado **“Número de puntos anatómicos clave detectados”** dentro de la dimensión **Estimación de pose 2D**. El cambio busca que la matriz de operacionalización, el Instrumento 2 y la redacción metodológica representen exactamente la información generada por el sistema.

El ajuste no modifica el algoritmo ni incorpora una nueva variable. Formaliza un cálculo que ya se encuentra implementado y elimina una ambigüedad en su denominación.

## 2. Problema de la denominación anterior

La expresión “número de puntos anatómicos clave detectados” podía interpretarse de diferentes maneras:

- cantidad de los 33 puntos generados por MediaPipe Pose;
- cantidad de los puntos seleccionados específicamente para la sentadilla;
- cantidad detectada en un fotograma particular;
- cantidad máxima observada durante el video;
- cantidad promedio detectada durante todo el video;
- cantidad de puntos anatómicos diferentes detectados al menos una vez.

Esta ambigüedad es relevante porque el Instrumento 2 registra una sola fila por video, pero la cantidad de puntos detectados puede variar entre fotogramas. Por tanto, una única cantidad sin indicar su forma de agregación no representa de manera precisa el comportamiento temporal de la estimación de pose.

## 3. Funcionamiento actual del sistema

MediaPipe Pose genera 33 puntos corporales. Sin embargo, el pipeline de sentadilla bilateral selecciona 13 puntos relacionados con el análisis frontal:

1. nariz;
2. hombro izquierdo;
3. hombro derecho;
4. cadera izquierda;
5. cadera derecha;
6. rodilla izquierda;
7. rodilla derecha;
8. tobillo izquierdo;
9. tobillo derecho;
10. talón izquierdo;
11. talón derecho;
12. punta del pie izquierda;
13. punta del pie derecha.

En cada fotograma, un punto se considera detectado cuando sus coordenadas bidimensionales `x` e `y` son finitas y su valor de visibilidad es igual o superior a 0,5. En consecuencia, cada fotograma recibe una cantidad comprendida entre 0 y 13.

La cantidad por fotograma se registra en `frame_quality.csv` mediante el campo `detected_keypoints`. Posteriormente, `pose_summary.json` calcula la media aritmética de todos los fotogramas procesados y la almacena en `mean_detected_keypoints`.

## 4. Definición final del indicador

El indicador se denominará:

> **Promedio de puntos anatómicos clave detectados por fotograma.**

Su definición operacional será:

> Media aritmética de la cantidad de los 13 puntos anatómicos seleccionados que poseen coordenadas bidimensionales finitas y visibilidad igual o superior a 0,5 en todos los fotogramas procesados.

Su unidad de medida será:

> **Puntos por fotograma, de un máximo de 13.**

## 5. Fórmula

La fórmula operativa es:

`Promedio de puntos detectados = suma de puntos detectados en todos los fotogramas / número de fotogramas procesados`

De forma abreviada:

`P_prom = (1 / N) × Σ P_f`

donde:

- `P_prom` es el promedio de puntos detectados por fotograma;
- `N` es el número total de fotogramas procesados;
- `P_f` es la cantidad de puntos con visibilidad igual o superior a 0,5 en el fotograma `f`;
- cada `P_f` puede tomar un valor entre 0 y 13.

### Ejemplo

Si un video tuviera tres fotogramas con 13, 12 y 11 puntos detectados:

`P_prom = (13 + 12 + 11) / 3 = 12`

El resultado se expresaría como:

> 12 puntos anatómicos clave detectados por fotograma, de un máximo de 13.

## 6. Diferencia entre cobertura y validez

El promedio de puntos detectados describe la cobertura general de la estimación de pose, pero no determina por sí solo la validez de un fotograma.

La regla vigente para que un fotograma sea utilizable exige coordenadas `x` e `y` finitas y visibilidad igual o superior a 0,5 en:

- hombro izquierdo y derecho;
- cadera izquierda y derecha;
- rodilla izquierda y derecha;
- tobillo izquierdo y derecho;
- al menos una referencia distal por cada pie, que puede ser el talón o la punta del pie.

La nariz no es una referencia necesaria para calcular las variables biomecánicas. Tampoco se exige disponer simultáneamente del talón y de la punta de cada pie si existe al menos una referencia distal suficiente por lado.

Por ello, deben diferenciarse dos indicadores:

- **Promedio de puntos anatómicos clave detectados por fotograma:** cobertura general de los 13 puntos seleccionados.
- **Porcentaje de fotogramas válidos:** proporción de fotogramas que cumplen la combinación concreta de referencias requerida para el análisis.

Un video puede presentar un promedio elevado de puntos detectados y, aun así, contener fotogramas inválidos si pierde temporalmente una cadera, rodilla, tobillo u otra referencia esencial.

También deben distinguirse las responsabilidades técnicas:

- OpenCV determina cuántos fotogramas declara el archivo y cuántos logra decodificar;
- MediaPipe estima coordenadas y visibilidad;
- la regla del sistema determina cuáles de esos fotogramas son válidos para análisis.

Por ello:

`Fotogramas procesados (%) = 100 × fotogramas decodificados / fotogramas declarados`

`Fotogramas válidos (%) = 100 × fotogramas que cumplen la regla de pose / fotogramas decodificados`

## 7. Cambios documentales necesarios

### 7.1. Matriz de operacionalización

Dentro de la dimensión **Estimación de pose 2D**, el indicador debe cambiar de:

> Número de puntos anatómicos clave detectados.

a:

> Promedio de puntos anatómicos clave detectados por fotograma.

La unidad “Razón / porcentaje” debe especificarse mejor como:

> Puntos por fotograma, de un máximo de 13 / porcentaje.

El indicador seguirá siendo medido mediante el Instrumento 2. El Instrumento 1 mantendrá el registro cualitativo de disponibilidad de las referencias anatómicas y las condiciones de entrada.

### 7.2. Instrumento 2

La cabecera debe cambiar de:

> N.° de puntos anatómicos clave detectados.

a:

> Promedio de puntos anatómicos clave detectados por fotograma.

La ficha debe incluir una leyenda con la definición, el umbral de visibilidad, el conjunto de 13 puntos y la unidad de medida.

### 7.3. Marco teórico

El indicador debe definirse dentro de la dimensión **Estimación de pose 2D**, diferenciándolo del porcentaje de fotogramas válidos y del porcentaje de fotogramas procesados correctamente.

La explicación conceptual de la estimación de pose y del atributo de visibilidad debe conservar las referencias bibliográficas correspondientes. La selección de 13 puntos y el umbral de 0,5 son decisiones operativas del sistema propuesto y no valores clínicos universales.

### 7.4. Técnicas e instrumentos

La sección 8.5 debe indicar que el Instrumento 2 registra el promedio calculado sobre los fotogramas procesados, no una cantidad aislada de puntos.

### 7.5. Análisis de datos

La sección 8.6 debe incluir este promedio dentro de los indicadores descriptivos del funcionamiento técnico, junto con los porcentajes de fotogramas válidos y procesados correctamente.

## 8. Aspectos que no cambian

El ajuste no modifica:

- MediaPipe Pose;
- los 13 puntos seleccionados;
- el umbral de visibilidad de 0,5;
- la extracción de coordenadas;
- el control de calidad;
- la segmentación temporal;
- las variables biomecánicas;
- las reglas interpretables;
- la muestra;
- los objetivos de investigación;
- los resultados obtenidos en los videos ya procesados.

Los archivos generados anteriormente siguen siendo válidos porque ya contienen el cálculo que ahora se formaliza.

## 9. Justificación metodológica

La modificación fortalece la coherencia entre la matriz de operacionalización, los instrumentos y el software. También permite que el indicador sea:

- específico, porque establece qué puntos se consideran;
- medible, porque define su fórmula;
- reproducible, porque identifica el umbral y la fuente de datos;
- interpretable, porque diferencia cobertura de validez;
- trazable, porque puede verificarse en los archivos generados por el sistema.

En consecuencia, el cambio no amplía el alcance de la tesis. Precisa la forma en que se medirá uno de los indicadores ya aprobados y reduce el riesgo de interpretaciones diferentes por parte del asesor, los validadores de los instrumentos o el jurado.

## 10. Relación con otros documentos

La redacción preparada para su incorporación se encuentra en:

- `ajustes_metodologicos_durante_desarrollo_sentadilla.md`;
- `uso_artefactos_outputs_interfaz_sentadilla.md`.

El cálculo implementado puede verificarse en:

- `frame_quality.csv`, mediante la cantidad detectada por fotograma;
- `pose_summary.json`, mediante el promedio del video;
- el overlay, mediante la cantidad mostrada en cada fotograma.
