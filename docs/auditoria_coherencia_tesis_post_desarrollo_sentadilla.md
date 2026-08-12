# Auditoría de coherencia de la tesis después del desarrollo del sistema

## 1. Propósito y alcance de esta auditoría

Este documento contrasta la redacción vigente de
`Plantilla_proyecto_de_tesis_completada.md` con el comportamiento realmente
implementado en las fases de extracción de pose 2D, control de calidad,
segmentación temporal, cálculo biomecánico, aplicación de reglas interpretables
y evaluación frente a expertos.

La auditoría no modifica todavía la plantilla principal. Su objetivo es separar:

- correcciones necesarias para que la tesis no prometa mediciones que el sistema
  no realiza;
- mejoras metodológicas que pueden incorporarse sin cambiar el propósito del
  estudio;
- cambios en cadena que deben validarse con el asesor antes de actualizar
  preguntas, objetivos, hipótesis, matriz, instrumentos y anexos.

## 2. Conclusión ejecutiva

El propósito aprobado de la tesis no necesita cambiar. El sistema continúa siendo
una solución monocular 2D, interpretable y no diagnóstica que analiza sentadillas
bilaterales en vista anterior dentro del plano frontal y compara sus resultados
con una referencia experta.

Sí se recomienda un refinamiento metodológico moderado por cuatro razones:

1. La segmentación temporal es un componente indispensable entre la estimación de
   pose y el cálculo biomecánico, pero actualmente no aparece como objetivo,
   dimensión ni procedimiento explícito.
2. La cuarta salida implementada no representa una asimetría corporal general.
   Calcula específicamente la diferencia bilateral entre las alineaciones
   cadera-rodilla-tobillo de ambas rodillas en máxima profundidad.
3. La matriz actual incluye diferencias bilaterales de desplazamiento y
   trayectoria que el prototipo no calcula ni compara con los expertos.
4. La muestra está formulada por video, mientras que el procesamiento y la
   clasificación son realmente por repetición y patrón. Esto debe quedar cerrado
   para evitar ambigüedad y pseudorreplicación.

La opción metodológicamente más coherente consiste en conservar las dos variables,
incorporar una dimensión de segmentación temporal, precisar la cuarta variable
biomecánica y reorganizar la variable de desempeño en métricas de clasificación y
concordancia.

## 3. Hallazgos priorizados

| Prioridad | Hallazgo | Riesgo si no se corrige | Acción recomendada |
| --- | --- | --- | --- |
| Alta | La segmentación temporal está ausente de preguntas, objetivos, hipótesis y matriz | No queda demostrado cómo se pasa de coordenadas por fotograma a una repetición y a su máxima profundidad | Incorporar segmentación como objetivo y dimensión explícitos, o como mínimo integrarla expresamente en el objetivo de cálculo y en el procedimiento |
| Alta | “Asimetría bilateral general/observable” excede lo calculado | Puede interpretarse como evaluación global del cuerpo, trayectorias o postura | Usar “diferencia bilateral de alineación de rodillas” y delimitarla al fotograma de máxima profundidad |
| Alta | La matriz promete diferencias bilaterales de desplazamiento y trayectoria | Los indicadores no tienen salida computacional ni campo equivalente en el Instrumento 3 | Sustituirlos por un único indicador implementado y verificable |
| Alta | No está cerrada la unidad de análisis | Un video con varias repeticiones produciría varias observaciones dependientes | Para la tesis, definir un video como un caso con una repetición completa elegible; la web puede conservar soporte multirrepetición |
| Alta | Los 15 positivos por patrón pueden solaparse | Un caso puede contener varios patrones, por lo que la suma nominal no garantiza 75 casos distintos | Tratar la intención de captura como cuota operativa, no como verdad de referencia; la etiqueta final la determinan los expertos |
| Media | Las fórmulas de las variables se describen de forma genérica | El marco teórico no coincide con el cálculo que ejecuta el prototipo | Incorporar definición, unidad, referencia, signo y fórmula exacta de cada indicador |
| Media | Los criterios de calidad están incompletos en el documento | No se distingue decodificación técnica, pose detectada y validez analítica | Definir las fórmulas y la regla `valid_for_analysis` con 8 puntos centrales y referencias distales |
| Media | “Número de criterios” y “número de umbrales” son indicadores débiles | Miden cantidad de implementación, no desempeño ni calidad | Reemplazarlos por clasificación por patrón, estado de decisión, lateralidad y trazabilidad del umbral aplicado |
| Media | La sección 8.5 solo resume instrumentos | El procedimiento real de las fases 2 a 5 no queda reproducible | Integrar el procedimiento dentro de 8.5, como indicó el asesor para la nueva plantilla |
| Media | Kappa no diferencia claramente sus dos usos | Puede confundirse concordancia sistema-referencia con concordancia entre expertos | Cohen para sistema frente a referencia final; Fleiss para concordancia entre tres expertos |
| Media | “Niveles adecuados” no posee punto de decisión | La hipótesis no define qué resultado la respalda | Acordar un criterio previo o formular la hipótesis como desempeño cuantificado, sin calificarlo arbitrariamente |
| Baja | El texto mezcla constructos teóricos con nombres internos del código | Reduce claridad académica y dificulta mantener el documento | Mantener términos académicos en el cuerpo y nombres técnicos solo en procedimiento, tablas o anexos |

## 4. Cadena problema-preguntas-objetivos-hipótesis

### 4.1. Estado actual

La cadena vigente contiene cinco objetivos específicos:

1. identificar puntos anatómicos clave;
2. definir variables biomecánicas;
3. diseñar criterios interpretables;
4. implementar el prototipo;
5. evaluar su desempeño.

La secuencia omite el paso que determina qué fotogramas conforman cada ejecución y
cuál es el fotograma de máxima profundidad. Sin ese paso, las variables no tienen
una unidad temporal ni un evento biomecánico de evaluación claramente definidos.

### 4.2. Alternativa recomendada: seis objetivos específicos

Esta alternativa es la más defendible porque cada objetivo produce evidencia
independiente y trazable.

| N.° | Pregunta específica propuesta | Objetivo específico propuesto | Evidencia principal |
| --- | --- | --- | --- |
| 1 | ¿Qué puntos anatómicos clave 2D y condiciones de calidad son necesarios para representar una sentadilla bilateral en vista anterior? | Identificar los puntos anatómicos clave 2D y establecer las condiciones de calidad requeridas para el análisis de la sentadilla bilateral. | `landmarks.csv`, `frame_quality.csv`, resumen de pose y puerta de calidad |
| 2 | ¿Qué procedimiento de segmentación temporal permite delimitar repeticiones completas y localizar el fotograma de máxima profundidad? | Establecer un procedimiento de segmentación temporal basado en la trayectoria vertical del punto medio de las caderas para delimitar repeticiones completas y localizar su máxima profundidad. | `frame_phases.csv`, `repetitions.csv`, prominencia, recuperación y control de calidad por repetición |
| 3 | ¿Qué variables biomecánicas observables pueden calcularse a partir de los puntos 2D y del fotograma de máxima profundidad? | Definir y calcular variables biomecánicas observables de tronco, pelvis y rodillas a partir de puntos anatómicos clave 2D y eventos temporales de la sentadilla. | Curvas por fotograma y valores en máxima profundidad |
| 4 | ¿Qué criterios interpretables permiten clasificar los cuatro patrones observables? | Establecer criterios biomecánicos interpretables para clasificar los cuatro patrones observables por repetición. | Reglas versionadas, umbrales, estado y lateralidad |
| 5 | ¿Cómo implementar un prototipo que integre captura, calidad, segmentación, cálculo, clasificación y reporte? | Implementar un prototipo funcional que integre el procesamiento y la generación de resultados trazables. | API, interfaz, overlays, tablas, gráficos y reportes |
| 6 | ¿Cuál es el desempeño del sistema frente a una referencia experta? | Evaluar el desempeño técnico mediante métricas de clasificación y concordancia frente a una referencia experta. | Matrices de confusión, precisión, sensibilidad, especificidad, F1 y Kappa |

### 4.3. Hipótesis específicas alineadas

Si la universidad exige una hipótesis por objetivo, la cadena puede redactarse así:

1. Los puntos anatómicos clave 2D y las reglas de calidad establecidas permiten
   obtener evidencia visual suficiente para el análisis frontal de la sentadilla
   bilateral bajo el protocolo de captura.
2. La trayectoria vertical del punto medio de las caderas, después de su limpieza
   y análisis de prominencia, permite delimitar repeticiones completas y localizar
   el fotograma de máxima profundidad bajo las condiciones del protocolo.
3. Las relaciones geométricas calculadas en el fotograma de máxima profundidad
   permiten cuantificar la inclinación lateral del tronco, el desplazamiento
   lateral de pelvis, la desviación medial de cada rodilla y la diferencia
   bilateral de alineación de rodillas.
4. Los criterios interpretables permiten clasificar de manera independiente la
   presencia, ausencia, lateralidad o indeterminación de cada patrón observable.
5. El prototipo funcional permite procesar videos elegibles y generar resultados
   estructurados, trazables y comprensibles.
6. El sistema presenta concordancia cuantificable con la referencia experta en los
   cuatro patrones evaluados.

La expresión “niveles adecuados” solo debe conservarse si se define antes del
análisis qué valor de F1 o Kappa será considerado adecuado. Sin ese criterio, es
preferible “concordancia cuantificable” o declarar que las métricas serán estimadas
e interpretadas sin un punto de aprobación arbitrario.

### 4.4. Alternativa conservadora

Si el asesor no autoriza aumentar el número de objetivos, la segmentación puede
integrarse en el objetivo actual de variables:

> Establecer el procedimiento de segmentación temporal y definir las variables
> biomecánicas observables derivadas de los puntos anatómicos clave 2D para
> delimitar repeticiones, localizar la máxima profundidad y representar los
> patrones evaluados durante la sentadilla bilateral.

Esta opción requiere menos cambios, pero combina dos productos diferentes y es
menos clara para demostrar el cumplimiento del objetivo.

## 5. Reorganización recomendada de las variables

### 5.1. Variable 1

Se conserva la denominación general:

> Sistema de visión por computadora basado en estimación de pose 2D y criterios
> biomecánicos interpretables.

Se recomienda reorganizarla en cuatro dimensiones. Esto evita aumentar el número
de dimensiones y elimina indicadores que solo describen funcionalidades de la
interfaz.

| Dimensión recomendada | Indicadores medibles | Unidad o escala | Instrumento |
| --- | --- | --- | --- |
| 1. Estimación de pose 2D y calidad analítica | Promedio de puntos anatómicos clave detectados por fotograma; porcentaje de fotogramas procesados correctamente; porcentaje global de fotogramas válidos | Puntos por fotograma, máximo 13; porcentaje | Instrumentos 1 y 2 |
| 2. Segmentación temporal de la sentadilla | Repeticiones completas detectadas; porcentaje de fotogramas válidos por repetición; validez del fotograma de máxima profundidad; duración de descenso, ascenso y repetición | Conteo; porcentaje; sí/no; segundos | Instrumento 2 |
| 3. Cálculo de variables biomecánicas observables | Inclinación lateral del tronco; desplazamiento lateral de pelvis; desviación medial de rodilla izquierda y derecha; diferencia bilateral de alineación de rodillas | Grados; porcentaje de `W0` | Instrumento 2 |
| 4. Aplicación de criterios interpretables y generación de resultados | Estado por patrón; lateralidad o predominio; umbral aplicado; salida no concluyente; reporte generado | Nominal; cumple/no cumple | Instrumento 2 |

La prominencia observada, la prominencia mínima, la separación de dos segundos, la
ventana de diez segundos y la recuperación entre máximos deben documentarse como
parámetros versionados del procedimiento. No conviene presentarlos como indicadores
de la variable, porque no son resultados de investigación ni criterios clínicos.

### 5.2. Variable 2

Puede conservarse la denominación general, pero sus dimensiones deben medir
desempeño y no repetir las salidas de la Variable 1.

| Dimensión recomendada | Indicadores | Unidad o escala | Instrumento/base |
| --- | --- | --- | --- |
| 1. Desempeño de clasificación por patrón | Exactitud, precisión, sensibilidad, especificidad y F1 por cada patrón; F1 macro como resumen | Proporción o porcentaje | Instrumento 3 y base consolidada de análisis |
| 2. Concordancia de las clasificaciones | Kappa de Cohen entre sistema y referencia final; Kappa de Fleiss entre tres expertos, si participan tres | Índice entre -1 y 1 | Instrumento 3 y base consolidada de análisis |

Los cuatro patrones deben tratarse como categorías de evaluación de estas
dimensiones, no como dimensiones adicionales de desempeño.

## 6. Corrección de la cuarta variable biomecánica

### 6.1. Denominación recomendada

> Diferencia bilateral de alineación de rodillas.

Una denominación aún más explícita para su definición es:

> Diferencia bilateral entre las desviaciones mediales normalizadas de las
> alineaciones cadera-rodilla-tobillo en máxima profundidad.

### 6.2. Razón del cambio

El sistema calcula:

\[
D_{bilateral}=|D_{izquierda}-D_{derecha}|
\]

donde ambas desviaciones ya se encuentran normalizadas por el mismo ancho inicial
de hombros. Esta operación no evalúa diferencias de trayectoria, sincronía,
desplazamiento general del cuerpo, rotación ni asimetría estructural. Por tanto, no
respalda la denominación “asimetría bilateral general”.

El lado con mayor desviación medial firmada puede informarse como predominio
izquierdo o derecho. Esto describe el resultado geométrico y no constituye una
causa anatómica ni un diagnóstico.

### 6.3. Impacto documental

El cambio afecta preguntas, objetivos, hipótesis, marco teórico, matriz de
operacionalización, Instrumentos 2 y 3, protocolos para evaluadores, base
consolidada, tablas y etiquetas visibles. No obliga a cambiar el propósito general,
pero sí requiere una sustitución consistente en todos los documentos.

Si el título aprobado contiene la expresión amplia “asimetrías cinemáticas”, se
recomienda conservarlo hasta consultar al asesor y delimitar operacionalmente que
la tesis evalúa una única diferencia cinemática bilateral específica.

## 7. Fórmulas que deben aparecer en el marco teórico

Las fórmulas deben acompañarse de definición, unidad, convención de signo, evento
temporal y alcance. El marco teórico explica el constructo; la metodología precisa
la implementación.

### 7.1. Indicadores de pose y calidad

Promedio de puntos detectados por fotograma:

\[
\bar K=\frac{1}{F_{dec}}\sum_{f=1}^{F_{dec}}K_f
\]

`K_f` es la cantidad de los 13 puntos seleccionados con coordenadas 2D finitas y
visibilidad mayor o igual que 0,5 en el fotograma `f`.

Porcentaje de fotogramas procesados correctamente:

\[
P_{proc}=100\frac{F_{dec}}{F_{declarados}}
\]

Porcentaje de fotogramas válidos:

\[
P_{valid}=100\frac{\sum_f valid\_for\_analysis(f)}{F_{dec}}
\]

Un fotograma es válido cuando ambos hombros, caderas, rodillas y tobillos son
utilizables y existe al menos una referencia distal utilizable por cada pie
(talón o punta del pie). La visibilidad crítica mínima es el menor valor entre los
ocho puntos centrales; no es un promedio.

### 7.2. Segmentación temporal

Señal de segmentación:

\[
h_y(f)=\frac{y_{cadera\ izquierda}(f)+y_{cadera\ derecha}(f)}{2}
\]

Después de interpolar huecos temporales, la señal se suaviza con una mediana móvil
y un promedio móvil centrados. La ventana actual equivale aproximadamente a 0,20
segundos.

Prominencia mínima adaptativa:

\[
p_{min}=\max(0,03;\ 0,18(P_{95}-P_{05}))
\]

Prominencia local acotada:

\[
p(P)=P-\max(B_I,B_D)
\]

La implementación busca las bases dentro de una ventana de hasta diez segundos a
cada lado. La documentación antigua que todavía menciona tres segundos debe
actualizarse.

Recuperación entre dos máximos candidatos:

\[
R=\min(P_1,P_2)-\min(h_y[P_1:P_2])
\]

Si `R < p_min`, los máximos se interpretan como una pausa u oscilación en una misma
repetición y se conserva el más profundo. Estas reglas son heurísticas versionadas
del prototipo y deben validarse con casos controlados; no son puntos de corte
biomecánicos universales.

### 7.3. Variables biomecánicas

Ancho inicial de hombros:

\[
W_0=mediana(|x_{HI}-x_{HD}|)
\]

Se calcula en fotogramas válidos del reposo inicial y sirve como referencia de
escala para las distancias horizontales.

Inclinación lateral del tronco:

\[
\theta=atan2(S_x-P_x,\ P_y-S_y)
\]

Se expresa en grados. La magnitud se compara con los umbrales y el signo informa la
dirección anatómica.

Desplazamiento lateral de pelvis:

\[
Pelvis_{\%}=100\frac{offset_{pelvis}(f_{pico})-offset_{pelvis,inicial}}{W_0}
\]

Desviación medial de rodilla:

\[
t=\frac{K_y-H_y}{A_y-H_y}
\]

\[
K_{x,esperado}=H_x+t(A_x-H_x)
\]

\[
D_{rodilla}=100\frac{s_{medial}(K_{x,real}-K_{x,esperado})}{W_0}
\]

La fórmula se aplica por separado a cada lado. Solo una desviación medial positiva
puede activar la regla de valgo; una desviación lateral negativa no se convierte en
valgo mediante valor absoluto.

Las cuatro variables que entran a las reglas se toman en el fotograma etiquetado
como máxima profundidad de cada repetición elegible. Las series completas se
conservan como evidencia, pero no se promedian para clasificar el patrón.

## 8. Procedimiento recomendado para la sección 8.5

El borrador anterior posee una sección de procedimiento útil, pero debe actualizarse
con el flujo realmente implementado. Debido a que la nueva plantilla no contiene
un apartado independiente, se recomienda incorporarlo al final de 8.5 bajo el
subtítulo “Procedimiento de aplicación”.

### Etapa 1. Captura, registro y aceptación manual

- obtener consentimiento y codificar el caso;
- grabar una ejecución sin carga externa, en vista anterior y bajo el protocolo;
- registrar condiciones de captura mediante el Instrumento 1;
- excluir manualmente incumplimientos críticos del protocolo.

### Etapa 2. Decodificación y estimación de pose

- OpenCV abre el archivo y decodifica sus fotogramas;
- cada fotograma se convierte de BGR a RGB para MediaPipe Pose;
- MediaPipe estima los puntos y sus valores de visibilidad;
- el sistema conserva 13 puntos y calcula calidad por fotograma;
- se generan CSV, JSON, overlay, video anonimizado y gráficos técnicos.

### Etapa 3. Segmentación temporal y puerta de calidad

- se construye `hip_midpoint_y` con ambas caderas;
- se interpolan huecos únicamente para continuidad temporal;
- se aplican mediana y promedio móviles;
- se detectan máximos mediante prominencia y distancia temporal;
- la recuperación evita dividir una pausa profunda en dos repeticiones;
- se etiquetan reposo, descenso, máxima profundidad, ascenso y cierre;
- se excluyen repeticiones con menos de 80 % de fotogramas válidos o con un
  fotograma de máxima profundidad inválido.

### Etapa 4. Cálculo biomecánico

- se calcula `W0` en reposo inicial;
- se obtienen las series de tronco, pelvis y rodillas;
- se extraen los valores del fotograma de máxima profundidad;
- se registra una salida independiente por repetición y patrón.

### Etapa 5. Clasificación interpretable

- se aplican umbrales provisionales versionados;
- cada patrón se clasifica como ausente, no concluyente o presente;
- se registra dirección, lateralidad o predominio cuando corresponda;
- pueden coexistir varios patrones en una misma repetición.

### Etapa 6. Evaluación experta y análisis

- dos o tres expertos evalúan de forma ciega cada repetición mediante el
  Instrumento 3;
- se construye la referencia experta final conforme a la regla establecida;
- se compara cada par repetición-patrón con la salida del sistema;
- se calculan métricas por patrón y un resumen agregado explícitamente definido.

## 9. Muestra y unidad de análisis

### 9.1. Recomendación para la tesis

Mantener 75 videos, pero establecer que cada video de la muestra formal contiene
una sola repetición completa elegible. De esta manera:

- unidad de registro: video o caso;
- unidad biomecánica: repetición completa;
- unidad de clasificación: par repetición-patrón;
- máximo analítico previsto: 75 repeticiones por 4 patrones = 300 pares, antes de
  excluir resultados no concluyentes.

El soporte multirrepetición de la plataforma puede presentarse como capacidad del
prototipo, pero no debe alterar la unidad de análisis de la tesis aprobada.

### 9.2. Cuotas de captura

Los 15 casos planeados para cada patrón deben describirse como intención controlada
de captura, no como etiqueta verdadera. Un video puede mostrar más de un patrón y
la referencia final depende de los expertos. Los 15 casos sin patrón intentado
tampoco deben asumirse automáticamente como negativos.

Si se decide aceptar varias repeticiones de una misma persona o video en la muestra
formal, debe cambiarse la unidad a “ejecución evaluable” y declararse la dependencia
entre observaciones. Esa alternativa requiere revisar tamaño muestral y análisis,
por lo que no se recomienda para el plan actual.

## 10. Delimitación y limitaciones que conviene incorporar

La delimitación del borrador anterior puede recuperarse, actualizándola con estas
precisiones:

- análisis 2D monocular en vista anterior dentro del plano frontal;
- sentadilla bilateral sin carga externa;
- una repetición completa por video para la muestra formal;
- cámara convencional y entorno controlado o semicontrolado;
- cuatro patrones observables definidos, sin inferencia de causas anatómicas;
- sin diagnóstico clínico, reconstrucción 3D, evaluación sagital/posterior ni
  estimación de rotaciones profundas;
- sin personalización de umbrales por antropometría;
- sin detección automática del contacto del talón o de soportes bajo los pies;
- sensibilidad a perspectiva, oclusión, ropa, iluminación y calidad de pose;
- umbrales biomecánicos provisionales sujetos a validación experta;
- segmentación basada en una señal 2D y parámetros temporales versionados.

También debe declararse que la visibilidad informada por MediaPipe representa
confianza del modelo y no exactitud anatómica demostrada frente a captura de
movimiento de laboratorio.

## 11. Referencias y justificaciones pendientes

No es necesario encontrar un artículo que “invente” cada operación de geometría
analítica. Deben respaldarse tres niveles diferentes:

1. pertinencia biomecánica de medir tronco, pelvis y alineación de rodilla;
2. validez y límites del análisis monocular 2D;
3. fundamento del procesamiento de señales utilizado para segmentar repeticiones.

La bibliografía actual cubre razonablemente los dos primeros niveles. Para el
tercero falta incorporar al marco teórico una fuente académica sobre segmentación
de repeticiones mediante señales verticales, máximos y prominencia. La documentación
de SciPy y pandas puede citarse como referencia técnica de implementación, pero no
debe sustituir por sí sola el sustento científico. El antecedente de
Sobrino-Santos et al. (2025), ya identificado durante el desarrollo, es un candidato
para la estrategia general de detección de repeticiones.

## 12. Inconsistencias documentales adicionales

1. La fórmula del promedio de puntos detectados aparece incompleta después de la
   conversión a Markdown. Debe restaurarse con símbolos y variables definidos.
2. El marco teórico permite expresar inclinación del tronco “en grados o razón
   normalizada”, pero el sistema solo la utiliza en grados. Debe fijarse esa unidad.
3. La alineación rodilla-cadera-tobillo se describe como “ángulo, distancia o
   criterio”. Debe reemplazarse por la desviación medial normalizada realmente
   implementada.
4. “Diferencias bilaterales” se formula como diferencia angular, porcentual o
   normalizada. Debe fijarse como diferencia absoluta porcentual entre las dos
   desviaciones de rodilla.
5. La documentación detallada conserva al menos una mención antigua a una ventana
   de prominencia de tres segundos. La versión implementada utiliza diez segundos.
6. El cronograma todavía menciona una “matriz complementaria” en una actividad,
   aunque se decidió que esa base pertenece al análisis y no es un instrumento.
7. El procedimiento debe usar “fotogramas” en la redacción académica y reservar
   `frame`, nombres de columnas y claves internas para anexos técnicos.

## 13. Orden de actualización recomendado

No debe modificarse primero el marco teórico de forma aislada. El orden correcto es:

1. confirmar con el asesor si se aprueba un sexto objetivo para segmentación;
2. confirmar la denominación “diferencia bilateral de alineación de rodillas”;
3. cerrar la unidad formal como una repetición elegible por video;
4. actualizar preguntas, objetivos e hipótesis;
5. reorganizar la matriz de operacionalización;
6. actualizar marco teórico y fórmulas;
7. incorporar el procedimiento en 8.5;
8. actualizar 8.6, delimitaciones y limitaciones;
9. sincronizar instrumentos, protocolos, tablas Excel y anexos;
10. regenerar el documento Word desde la versión Markdown validada.

## 14. Decisiones que requieren confirmación

Antes de alterar la plantilla principal conviene confirmar únicamente tres puntos:

1. si la segmentación temporal tendrá objetivo específico propio o se integrará en
   el objetivo de cálculo biomecánico;
2. si el nombre de la cuarta salida se reemplazará de forma global o se mantendrá
   el título general y solo se precisará su definición operacional;
3. si la muestra formal conservará exactamente una repetición completa por video.

Las demás correcciones son de coherencia técnica y pueden aplicarse después de esas
tres decisiones sin cambiar la finalidad aprobada de la tesis.
