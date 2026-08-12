**Borrador de tesis - Capítulos 1 y 2**

# Sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables para la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral

## Portada

Facultad de Ingeniería

Carrera de Ingeniería de Software

Tesis:

Sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables para la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral

Autor:

Chapoñan Castro, Geancarlos Elías

Para optar el Título Profesional de Ingeniero de Software

Asesor:

Linares Luján, Guillermo Alberto

Lima - Perú

2026

## Resumen

La evaluación de la sentadilla bilateral constituye una práctica relevante en contextos de entrenamiento, análisis funcional y seguimiento del movimiento humano, debido a que permite identificar compensaciones posturales y asimetrías cinemáticas asociadas al control motor, la estabilidad y la coordinación corporal. Sin embargo, este análisis suele depender de observación especializada o de herramientas biomecánicas de alto costo, lo que limita su accesibilidad en escenarios cotidianos de evaluación. Frente a ello, la visión por computadora y los modelos de estimación de pose 2D representan una alternativa viable para analizar el movimiento humano a partir de videos capturados con cámaras convencionales.

En este contexto, la presente investigación tiene como objetivo diseñar e implementar un sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables para detectar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral. La propuesta se centrará en la identificación de landmarks corporales relevantes, el cálculo de variables biomecánicas observables y la aplicación de reglas explicables para detectar patrones como inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y asimetría bilateral general.

Metodológicamente, el estudio tendrá un enfoque cuantitativo, de tipo aplicada, con alcance descriptivo-propositivo y diseño no experimental transversal. Se procesarán videos de sentadillas bilaterales capturados con cámara convencional, y el desempeño técnico del sistema será evaluado mediante métricas de clasificación y concordancia, en comparación con un criterio de referencia basado en evaluación experta. Como resultado esperado, se proyecta desarrollar un prototipo funcional capaz de generar reportes interpretables sobre compensaciones posturales y asimetrías cinemáticas observables durante la ejecución del ejercicio.

Palabras clave: visión por computadora, estimación de pose 2D, sentadilla bilateral, compensaciones posturales, asimetrías cinemáticas, reglas biomecánicas interpretables.

## Índice propuesto

- Introducción
- Capítulo 1. Generalidades
- 1\. Planteamiento del problema
- 1.1. Descripción del problema
- 1.1.1. Pregunta general
- 1.1.2. Preguntas específicas
- 2\. Objetivos
- 2.1. Objetivo general
- 2.2. Objetivos específicos
- 3\. Justificación
- 3.1. Justificación teórica
- 3.2. Justificación metodológica
- 3.3. Justificación práctica
- 3.4. Justificación tecnológica
- 4\. Delimitación
- 4.1. Delimitación espacial
- 4.2. Delimitación temporal
- 4.3. Delimitación temática
- 5\. Hipótesis
- 5.1. Hipótesis general
- 5.2. Hipótesis específicas
- 6\. Variables
- 6.1. Variable 1
- 6.2. Variable 2
- 6.3. Matriz de operacionalización de variables
- Capítulo 2. Marco teórico
- 1\. Estado del arte
- 2\. Marco teórico

## Introducción

El análisis del movimiento humano constituye un campo de creciente interés en ámbitos como la salud, el entrenamiento, la rehabilitación, la ergonomía y la evaluación funcional. Dentro de este contexto, la sentadilla bilateral es uno de los ejercicios funcionales más utilizados para observar control motor, estabilidad y alineación corporal, debido a que involucra la coordinación simultánea del tronco, pelvis y miembros inferiores. Su ejecución permite identificar compensaciones posturales y asimetrías cinemáticas que pueden ser relevantes para el análisis técnico del movimiento.

Tradicionalmente, la evaluación de este ejercicio ha dependido de la observación experta o del uso de equipamiento biomecánico especializado, como sistemas de captura de movimiento, plataformas de fuerza o entornos de laboratorio. Estas opciones, aunque útiles, no siempre resultan accesibles en contextos cotidianos de entrenamiento, tamizaje o seguimiento funcional. En respuesta a esta limitación, la visión por computadora y la estimación de pose humana han surgido como alternativas tecnológicas para analizar movimientos corporales a partir de videos capturados con cámaras convencionales.

No obstante, aunque diversas soluciones actuales permiten clasificar la técnica de la sentadilla como correcta o incorrecta, o bien medir determinados ángulos articulares, no todas traducen los datos obtenidos en compensaciones posturales específicas y biomecánicamente interpretables. Esta brecha plantea la necesidad de desarrollar sistemas que no solo detecten landmarks corporales, sino que también conviertan esos datos en criterios comprensibles para el análisis funcional del movimiento.

En ese sentido, la presente investigación propone el diseño e implementación de un sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables para detectar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral. El estudio busca aportar una herramienta tecnológica accesible y explicable para el análisis preliminar del movimiento humano, sin sustituir la evaluación especializada.

# Capítulo 1. Generalidades

## 1. Planteamiento del problema

El análisis del movimiento humano es una actividad relevante en múltiples escenarios vinculados con la salud, el entrenamiento físico, la rehabilitación y la prevención de alteraciones funcionales. Esta relevancia se refuerza por el creciente interés del entrenamiento de fuerza en población adulta y por la evidencia que vincula este tipo de práctica con beneficios funcionales y de salud cuando se aplica de forma adecuada. La revisión de El-Kotob et al. \[1] muestra que el entrenamiento de fuerza se ha consolidado como una estrategia de interés en población adulta, mientras que trabajos como el de Serafim et al. \[2] y la revisión integrativa de Bonilla et al. \[3] recuerdan que la seguridad del entrenamiento depende en buena medida de la calidad de la ejecución técnica, del control de la carga y de la adecuada selección de ejercicios.

Dentro de este campo, la sentadilla bilateral representa un ejercicio funcional de alta utilidad, ya que permite observar la relación entre estabilidad, control motor, alineación corporal y coordinación de distintos segmentos durante una tarea de flexo-extensión simultánea del tren inferior. Su uso se ha extendido tanto en evaluación física como en programas de entrenamiento y seguimiento corporal. Desde el punto de vista biomecánico, revisiones como la de Straub y Powers \[4] y estudios como el de Graber et al. \[5] muestran que la sentadilla bilateral es una tarea rica en información segmentaria, debido a que pone en juego la coordinación entre tronco, pelvis, cadera, rodilla y tobillo.

Durante la ejecución de la sentadilla bilateral pueden manifestarse diversas compensaciones posturales y asimetrías cinemáticas, como inclinación lateral del tronco, desplazamiento lateral de pelvis, colapso medial visible de rodillas o diferencias entre ambos lados del cuerpo. La literatura reciente también ha mostrado interés en patrones como el valgo dinámico, la distribución asimétrica de la carga y la calidad general del movimiento, tanto en estudios observacionales como en análisis biomecánicos y evaluaciones aplicadas de la calidad de la sentadilla. En ese sentido, Erdman et al. \[6], Forman et al. \[7], Liu et al. \[8] y Kaartinen et al. \[9] aportan antecedentes relevantes.

La identificación de estos patrones suele depender de la experiencia del evaluador, del contexto de observación y, en escenarios más especializados, del uso de tecnologías biomecánicas avanzadas. Sin embargo, distintos trabajos evidencian que la evaluación visual aislada puede presentar limitaciones relevantes. Falk et al. \[10] reportan restricciones en la precisión de la evaluación visual de movimientos lumbopélvicos durante sentadilla y peso muerto, mientras que Gomes et al. \[11], Ressman et al. \[12] y Nutarelli et al. \[13] muestran que la validez y confiabilidad de herramientas observacionales pueden variar, e incluso mejorar cuando el análisis se realiza sobre video en lugar de observación en tiempo real. Esta situación genera limitaciones de acceso, variabilidad en la interpretación y dificultades para disponer de evaluaciones rápidas, consistentes y escalables.

En los últimos años, la visión por computadora y los modelos de estimación de pose humana han ofrecido nuevas posibilidades para analizar movimientos corporales a partir de videos capturados con cámaras convencionales. Dichos avances permiten identificar puntos anatómicos clave del cuerpo (landmarks) en dos dimensiones y derivar métricas geométricas que pueden utilizarse para representar ciertos comportamientos del movimiento. Trabajos como los de Ota et al. \[14], Mercadal-Baudart et al. \[15], Pereira et al. \[16], Lima et al. \[17], Powell et al. \[18] y Kanko et al. \[19] muestran que el análisis del movimiento sin marcadores ya puede alcanzar niveles útiles de validez técnica en diferentes tareas funcionales, mientras que revisiones como las de Halilaj et al. \[20], Armitano-Lago et al. \[21] y Needham et al. \[22] evidencian el crecimiento sostenido de este campo en soluciones accesibles y su proyección hacia contextos aplicados.

Sin embargo, en gran parte de la literatura y de las soluciones tecnológicas disponibles, el análisis se concentra en clasificar la técnica de forma general, en validar la precisión de ángulos o en comparar tecnologías, sin traducir necesariamente esos datos en compensaciones posturales específicas, biomecánicamente explicables y fácilmente interpretables. Este vacío es visible tanto en estudios centrados en clasificación automática del movimiento como en enfoques basados en deep learning o en plataformas tridimensionales sin marcadores de mayor complejidad, como se observa en los trabajos de Shen et al. \[23], Bae et al. \[24], Sadeghi et al. \[25] y Noël et al. \[26].

En consecuencia, se identifica una brecha técnica y metodológica: la necesidad de diseñar un sistema que, utilizando estimación de pose 2D y criterios biomecánicos interpretables, permita detectar de manera explícita compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral, a partir de videos capturados con una cámara convencional. Esta necesidad se vuelve particularmente relevante en escenarios donde no se cuenta con laboratorios de captura de movimiento, sistemas basados en marcadores o configuraciones multicámara avanzadas, pero sí con interés por disponer de una evaluación funcional más estructurada. Bajo este panorama, el desarrollo de un prototipo funcional orientado al análisis explicable del movimiento humano se justifica como una respuesta tecnológicamente viable y metodológicamente coherente.

> ***Nota de apoyo bibliográfico para esta sección: los trabajos de Falk et al. \[10] y Bonilla et al. \[3] resultan especialmente útiles para fortalecer la argumentación del problema y la justificación práctica, mientras que Straub y Powers \[4] y Graber et al. \[5] ayudan a respaldar la relevancia biomecánica de la sentadilla bilateral como objeto de estudio.***

### 1.1. Descripción del problema

La problemática específica de esta investigación se centra en la ausencia de un sistema accesible y explicable que transforme datos derivados de la estimación de pose 2D en hallazgos biomecánicos útiles para identificar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral. Aunque existen avances en estimación de pose, validación del análisis sin marcadores y clasificación de ejercicios, persiste la necesidad de una propuesta que combine detección visual, cálculo de variables biomecánicas y criterios interpretables de decisión. En otras palabras, no basta con medir ángulos o producir una categoría general de “buen” o “mal” movimiento; se requiere una solución que articule datos visuales, biomecánica observacional y una lógica de salida comprensible.

#### 1.1.1. Pregunta general

¿Cuál es el desempeño técnico del sistema de visión por computadora propuesto para detectar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral, en comparación con un criterio de referencia basado en evaluación experta?

#### 1.1.2. Preguntas específicas

1. ¿Qué puntos anatómicos clave del cuerpo (landmarks) en 2D son relevantes para el análisis biomecánico observable de la sentadilla bilateral mediante visión por computadora?
2. ¿Qué variables biomecánicas observables pueden calcularse a partir de los puntos anatómicos clave del cuerpo (landmarks) en 2D para representar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral?
3. ¿Qué criterios biomecánicos interpretables pueden diseñarse para detectar patrones como inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y asimetría bilateral general?
4. ¿Cómo implementar un prototipo funcional que procese videos de sentadilla bilateral y genere resultados interpretables sobre la ejecución del movimiento?
5. ¿Cuál es el desempeño técnico del sistema propuesto en la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral, en comparación con un criterio de referencia basado en evaluación experta?

## 2. Objetivos

### 2.1. Objetivo general

Diseñar e implementar un sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables para detectar compensaciones posturales y asimetrías cinemáticas durante la ejecución de sentadillas bilaterales.

### 2.2. Objetivos específicos

6. Identificar los puntos anatómicos clave del cuerpo (landmarks) en 2D relevantes para el análisis biomecánico observable de la sentadilla bilateral a partir de videos capturados con cámara convencional.
7. Definir variables biomecánicas observables derivadas de los puntos anatómicos clave del cuerpo (landmarks) en 2D que permitan representar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral.
8. Diseñar criterios biomecánicos interpretables para la detección de patrones posturales como inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y asimetría bilateral general.
9. Implementar un prototipo funcional que procese videos de sentadilla bilateral, estime la postura corporal y genere resultados interpretables sobre las compensaciones posturales y asimetrías cinemáticas detectadas.
10. Evaluar el desempeño técnico del sistema propuesto mediante métricas de clasificación y concordancia frente a un criterio de referencia basado en evaluación experta.

## 3. Justificación

### 3.1. Justificación teórica

Desde el punto de vista teórico, la investigación aporta a la integración entre visión por computadora, estimación de pose humana y biomecánica observacional aplicada al análisis de ejercicios funcionales. Su relevancia radica en organizar una base conceptual que permita transformar puntos anatómicos clave del cuerpo (landmarks) en dos dimensiones en variables biomecánicas observables e interpretables. Asimismo, contribuye a precisar criterios para identificar compensaciones y asimetrías durante la sentadilla bilateral, fortaleciendo el vínculo entre representación computacional del movimiento y análisis funcional del cuerpo humano. Esta articulación teórica se sostiene en antecedentes que van desde la estimación general de pose, desarrollada por Bazarevsky et al. \[27], Stenum et al. \[28] y Rode et al. \[29], hasta estudios específicos sobre sentadilla, análisis del movimiento sin marcadores y evaluación de la calidad del movimiento, como los de Ota et al. \[14], Pereira et al. \[16], Hofer et al. \[30] y Noël et al. \[26].

### 3.2. Justificación metodológica

Metodológicamente, la propuesta es pertinente porque establece un procedimiento sistemático para la captura o selección de videos, el procesamiento de imágenes, la extracción de puntos anatómicos clave del cuerpo (landmarks), el cálculo de variables biomecánicas observables, la aplicación de criterios biomecánicos interpretables y la evaluación del desempeño técnico del sistema. Este enfoque no solo favorece la trazabilidad del desarrollo, sino que además puede adaptarse posteriormente a otros ejercicios funcionales o contextos similares de análisis del movimiento. La pertinencia del método se refuerza con literatura que muestra tanto las capacidades como las limitaciones del análisis del movimiento sin marcadores, ya sea en soluciones monoculares o multicámara. Entre estos antecedentes destacan Straub y Powers \[31], Bae et al. \[24], Halilaj et al. \[20], Armitano-Lago et al. \[21], Kim et al. \[32] y Kanko et al. \[33].

### 3.3. Justificación práctica

En el plano práctico, la investigación busca generar una herramienta de apoyo para el análisis preliminar de la sentadilla bilateral en contextos de entrenamiento, evaluación funcional y seguimiento corporal. El sistema propuesto no pretende reemplazar la evaluación especializada, sino facilitar una detección inicial de compensaciones y asimetrías de forma más accesible y consistente. Esto puede resultar útil en escenarios donde no se cuenta con equipamiento biomecánico avanzado, pero sí con cámaras convencionales y necesidad de observación estructurada del movimiento.

Desde una perspectiva aplicada, esta utilidad se relaciona con dos problemas concretos identificados en la literatura: por un lado, la necesidad de controlar mejor la ejecución técnica y reducir errores potencialmente vinculados con sobreuso o lesión, como señalan Bonilla et al. \[3] y Serafim et al. \[2]; por otro, la variabilidad de las evaluaciones visuales cuando no se dispone de apoyo tecnológico o de revisión por video, aspecto documentado por Falk et al. \[10], Gomes et al. \[11], Ressman et al. \[12] y Nutarelli et al. \[13].

> ***Nota de apoyo bibliográfico para la justificación: Bonilla et al. \[3] servirán para sustentar la relación entre errores técnicos, selección de ejercicios y lesiones en contextos de entrenamiento, mientras que Falk et al. \[10] ayudarán a justificar las limitaciones de la evaluación visual aislada.***

### 3.4. Justificación tecnológica

Desde la perspectiva tecnológica, la investigación se alinea con la formación en Ingeniería de Software al involucrar el diseño de un prototipo funcional, el procesamiento de video, la integración de modelos preentrenados de estimación de pose 2D, el cálculo de variables geométricas, la aplicación de reglas de decisión y la generación de resultados interpretables. Asimismo, permite abordar el sistema como una solución informática evaluable, medible y potencialmente escalable hacia otras aplicaciones del análisis del movimiento humano.

La bibliografía revisada muestra además que el campo tecnológico avanza en distintas direcciones: sistemas monoculares accesibles, como los estudiados por Ino et al. \[34], Usami et al. \[35] y Ohmura et al. \[36]; soluciones de bajo costo como OpenCap, abordadas por Uhlrich et al. \[37], Lima et al. \[17] y Powell et al. \[18]; sistemas tridimensionales sin marcadores de mayor complejidad, como los de Bae et al. \[24] y Noël et al. \[26]; y enfoques de clasificación basados en unidades de medición inercial o deep learning, como el de Sadeghi et al. \[25]. Esto refuerza la pertinencia de que la tesis delimite con claridad su apuesta tecnológica: una solución 2D, monocular, interpretable y viable dentro del alcance aprobado.

## 4. Delimitación

### 4.1. Delimitación espacial

La investigación se desarrollará en un entorno controlado o semicontrolado que permita la captura o selección de videos con visibilidad completa del cuerpo, utilizando una cámara convencional. La evaluación se centrará en el análisis de videos registrados bajo condiciones que favorezcan la correcta detección de landmarks corporales.

Esta delimitación responde también a hallazgos metodológicos de la literatura reciente, en la que se observa que variables como el ángulo de cámara, la alineación del plano de captura, la distancia al sujeto y la presencia de oclusiones afectan el rendimiento del análisis del movimiento sin marcadores. Estudios como los de Ohmura et al. \[36] y Needham et al. \[38] muestran la importancia de protocolos de captura explícitos incluso cuando se emplean soluciones accesibles con smartphone.

### 4.2. Delimitación temporal

El estudio se desarrollará durante el año 2026, periodo en el cual se realizará la recopilación o captura de videos, el desarrollo del prototipo, la validación técnica del sistema y el análisis de resultados.

### 4.3. Delimitación temática

La investigación se centrará en visión por computadora, estimación de pose 2D y criterios biomecánicos interpretables para detectar compensaciones posturales y asimetrías cinemáticas observables durante la sentadilla bilateral. No comprende diagnóstico clínico, análisis biomecánico tridimensional, instrumentación de laboratorio ni sustitución de la evaluación profesional especializada.

Tampoco forma parte del alcance principal el entrenamiento de modelos de deep learning desde cero ni la construcción de un sistema multicámara tridimensional sin marcadores. Dichos enfoques, presentes en parte de la literatura revisada, como en los trabajos de Shen et al. \[23], Bae et al. \[24], Kuo et al. \[39] y Noël et al. \[26], se consideran líneas comparativas o posibles desarrollos futuros, pero no corresponden al núcleo metodológico de la tesis actual.

## 5. Hipótesis

### 5.1. Hipótesis general

El sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables permite detectar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral con niveles adecuados de desempeño técnico frente a un criterio de referencia basado en evaluación experta.

### 5.2. Hipótesis específicas

11. La identificación de landmarks corporales 2D permite representar segmentos corporales relevantes para el análisis biomecánico observable de la sentadilla bilateral.
12. Las variables biomecánicas calculadas a partir de landmarks corporales 2D permiten caracterizar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral.
13. Los criterios biomecánicos interpretables permiten clasificar patrones posturales específicos como inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y asimetría bilateral general.
14. El prototipo funcional permite procesar videos de sentadilla bilateral y generar resultados interpretables sobre la ejecución del movimiento.
15. El sistema propuesto presenta niveles adecuados de desempeño técnico en la detección de compensaciones posturales y asimetrías cinemáticas frente a un criterio de referencia basado en evaluación experta.

## 6. Variables

### 6.1. Variable 1

Sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables

Corresponde a la solución tecnológica desarrollada para procesar videos de sentadilla bilateral, estimar landmarks corporales, calcular variables biomecánicas observables, aplicar criterios biomecánicos interpretables y generar resultados sobre compensaciones posturales y asimetrías cinemáticas.

### 6.2. Variable 2

Desempeño técnico del sistema en la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral

Corresponde al rendimiento del sistema en la identificación de patrones observables del movimiento, evaluado a partir de su capacidad para detectar compensaciones posturales y asimetrías cinemáticas en comparación con un criterio de referencia basado en evaluación experta.

### 6.3. Matriz de operacionalización de variables

#### Introducción a la matriz

Las variables del estudio se derivan del problema de investigación, de los objetivos planteados y del enfoque metodológico adoptado. La primera variable representa el sistema tecnológico desarrollado, mientras que la segunda variable corresponde al desempeño técnico del sistema en la detección de patrones del movimiento. A continuación, se presenta una matriz preliminar de operacionalización.

#### Matriz preliminar de operacionalización de variables

| Variable | Definición conceptual | Definición operacional | Dimensiones | Indicadores | Unidad de medida | Instrumentos |
| --- | --- | --- | --- | --- | --- | --- |
| Sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables | Sistema computacional que procesa videos para estimar la postura corporal y aplicar criterios biomecánicos mediante reglas interpretables. | Se evaluará mediante la identificación de landmarks, el cálculo de variables biomecánicas, la aplicación de criterios interpretables y la generación de resultados a través de un prototipo funcional. | Estimación de pose 2D | Número de landmarks detectados; porcentaje de frames válidos; porcentaje de frames procesados correctamente | Razón / porcentaje | Ficha de procesamiento de video |
|  | Sistema computacional que procesa videos para estimar la postura corporal y aplicar criterios biomecánicos mediante reglas interpretables. | Se evaluará mediante la identificación de landmarks, el cálculo de variables biomecánicas, la aplicación de criterios interpretables y la generación de resultados a través de un prototipo funcional. | Extracción y cálculo de variables biomecánicas observables | Inclinación del tronco; desplazamiento lateral de pelvis; alineación rodilla-cadera-tobillo; diferencias bilaterales | Grados / valores normalizados / porcentaje | Matriz de variables biomecánicas |
|  | Sistema computacional que procesa videos para estimar la postura corporal y aplicar criterios biomecánicos mediante reglas interpretables. | Se evaluará mediante la identificación de landmarks, el cálculo de variables biomecánicas, la aplicación de criterios interpretables y la generación de resultados a través de un prototipo funcional. | Aplicación de criterios biomecánicos interpretables | Número de criterios implementados; tipo de compensación detectada; umbrales definidos | Nominal / razón | Matriz de criterios biomecánicos |
|  | Sistema computacional que procesa videos para estimar la postura corporal y aplicar criterios biomecánicos mediante reglas interpretables. | Se evaluará mediante la identificación de landmarks, el cálculo de variables biomecánicas, la aplicación de criterios interpretables y la generación de resultados a través de un prototipo funcional. | Procesamiento y generación de resultados | Carga de video; procesamiento completo; generación de reporte; visualización de resultados | Cumple / no cumple; porcentaje | Ficha de evaluación del prototipo |
| Desempeño técnico del sistema en la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral | Rendimiento del sistema en la identificación de patrones observables del movimiento durante la sentadilla bilateral. | Se medirá comparando los resultados del sistema con un criterio de referencia basado en evaluación experta. | Detección de compensaciones posturales | Inclinación lateral del tronco; desplazamiento lateral de pelvis; valgo dinámico visible | Nominal / ordinal | Ficha de evaluación postural |
|  | Rendimiento del sistema en la identificación de patrones observables del movimiento durante la sentadilla bilateral. | Se medirá comparando los resultados del sistema con un criterio de referencia basado en evaluación experta. | Detección de asimetrías cinemáticas | Diferencia entre lado derecho e izquierdo en alineación corporal; diferencia entre lados en desplazamiento; diferencia entre lados en trayectoria relativa | Diferencia angular / porcentaje / valor normalizado | Matriz de análisis bilateral |
|  | Rendimiento del sistema en la identificación de patrones observables del movimiento durante la sentadilla bilateral. | Se medirá comparando los resultados del sistema con un criterio de referencia basado en evaluación experta. | Desempeño técnico de la detección | Exactitud; precisión; sensibilidad; especificidad; F1-score; índice Kappa | Porcentaje / índice | Matriz de validación del sistema |

# Capítulo 2. Marco teórico

## 1. Estado del arte

El estado del arte de la presente investigación evidencia que la visión por computadora y la estimación de pose humana se han consolidado como líneas de trabajo relevantes para el análisis del movimiento en contextos de salud, deporte y rendimiento físico. La literatura reciente muestra una transición progresiva desde aplicaciones centradas en el reconocimiento general del cuerpo hacia sistemas capaces de cuantificar ejercicios, describir trayectorias segmentarias y apoyar procesos de evaluación funcional. En ese marco, Bazarevsky et al. \[27] presentan BlazePose como uno de los modelos de referencia para la estimación de pose en tiempo real, mientras que Stenum et al. \[28] documentan su expansión hacia contextos clínicos, de rehabilitación y de rendimiento humano. De forma complementaria, Rode et al. \[29] comparan distintos modelos monoculares para análisis clínico del movimiento y muestran que su desempeño depende de la tarea, del grado de auto-oclusión y de la profundidad espacial que se requiera representar. En conjunto, estos antecedentes permiten sostener que la estimación de pose bidimensional ha dejado de ser una técnica meramente experimental para convertirse en una alternativa con aplicación creciente en escenarios funcionales.

Sobre esa base, una parte importante de la literatura se ha orientado a validar sistemas de análisis del movimiento sin marcadores frente a referencias de mayor fidelidad, como la captura de movimiento con marcadores o los sistemas tridimensionales de laboratorio. En esta línea, Ota et al. \[14] constituyen uno de los antecedentes más cercanos a la presente tesis, pues validan un sistema de seguimiento de pose humana durante la sentadilla bilateral y lo comparan con VICON. De manera similar, Schmitz et al. \[40] presentan un antecedente fundacional al contrastar una sola cámara sin marcadores con un sistema basado en marcadores durante la ejecución de la sentadilla, y Pereira et al. \[16] proponen un procedimiento bidimensional para cuantificar la cinemática de los miembros inferiores durante la misma tarea. En una línea complementaria, Mercadal-Baudart et al. \[15] cuantifican ejercicios funcionales mediante una sola cámara y reportan errores mayores precisamente en algunas métricas de asimetría, mientras que Lopes et al. \[41] sintetizan que la validez del análisis bidimensional depende tanto de la tarea como del nivel de precisión exigido. En el extremo tecnológicamente más avanzado, Bae et al. \[24] validan un sistema tridimensional sin marcadores basado en deep learning durante el overhead squat, lo que demuestra el potencial del campo cuando se dispone de infraestructura multicámara, aunque en un nivel de complejidad distinto al de una solución monocular accesible.

Paralelamente, el estado de la cuestión confirma que la sentadilla y sus variantes continúan siendo tareas biomecánicas de alto interés tanto para la evaluación como para la intervención. Straub y Powers \[4] explican que variables como la inclinación del tronco, la posición de la tibia, la profundidad, la separación de los pies y la orientación del apoyo modifican de forma importante la demanda mecánica del ejercicio. En el mismo sentido, Graber et al. \[5] muestran que la posición del tronco y de la pierna influye directamente en la relación de momentos entre cadera y rodilla durante la sentadilla bilateral profunda. Curnow et al. \[42], por su parte, incorporan una lectura clínica reciente de la sentadilla bilateral y de la sentadilla a una pierna (single-leg squat) en grupos con distintas condiciones de cadera. En conjunto, estos trabajos resultan relevantes porque desplazan la sentadilla desde una práctica general de entrenamiento hacia un problema biomecánico concreto, en el cual las relaciones entre tronco, pelvis y miembros inferiores adquieren valor analítico.

Dentro de esa misma literatura, una línea especialmente vinculada con la presente tesis se enfoca en compensaciones específicas y variables observables, sobre todo en torno al valgo dinámico y al control del tronco y la pelvis. Erdman et al. \[6] muestran que una evaluación bidimensional puede asociarse con contribuyentes biomecánicos tridimensionales del valgo dinámico en el plano coronal, mientras que Forman et al. \[7] discuten ese patrón dentro de movimientos basados en sentadilla. Por otra parte, Straub y Powers \[31] validan el uso de video bidimensional para medir el movimiento del tronco y la pelvis en el plano frontal, lo que resulta particularmente útil para sustentar compensaciones como la inclinación lateral del tronco y el desplazamiento lateral de la pelvis. En términos de asimetría bilateral, Liu et al. \[8] muestran que la carga asimétrica en la sentadilla con barra modifica los momentos articulares y la actividad muscular de los miembros inferiores, lo cual refuerza la importancia de considerar diferencias entre lados como parte del análisis funcional del movimiento.

Otra línea importante del estado del arte se orienta a la clasificación automática del movimiento y a la evaluación de la calidad de ejecución. Dajime et al. \[43] proponen un sistema de clasificación de la calidad del movimiento basado en variables cinemáticas obtenidas con Kinect y regresión logística multiclase, evidenciando que las variables biomecánicas pueden estructurarse como insumo para diferenciar patrones funcionales. En una línea más reciente, Kim y Park \[44] desarrollan un enfoque de machine learning interpretable para clasificar el desempeño en la sentadilla a una pierna a partir de variables de tronco, pelvis y rodilla, mientras que Shen et al. \[23] avanzan hacia una evaluación más automatizada mediante deep learning aplicada al tamizaje funcional del movimiento (functional movement screening). A su vez, Kianifar et al. \[45] y Sadeghi et al. \[25] representan antecedentes de clasificación automática de patrones de riesgo o errores de sentadilla a partir de unidades de medición inercial y modelos de mayor complejidad. En conjunto, estos estudios muestran que el campo no solo busca medir el movimiento, sino también transformar esa medición en una decisión automática. No obstante, en muchos casos la salida final continúa siendo global o poco explicable desde la biomecánica observacional.

El estado del arte reciente también confirma un crecimiento sostenido de soluciones de bajo costo para el análisis del movimiento sin marcadores y de plataformas accesibles fuera del laboratorio. Armitano-Lago et al. \[21] presentan un análisis SWOT de sistemas portables y de bajo costo, identificando fortalezas en accesibilidad y oportunidades de adopción, pero también debilidades asociadas a precisión, oclusión y protocolo. En la misma línea, Uhlrich et al. \[37], Lima et al. \[17] y Powell et al. \[18] muestran el potencial de OpenCap y de otras aproximaciones basadas en smartphones o captura asequible para aproximarse a mediciones biomecánicas útiles en tareas funcionales, incluyendo la sentadilla y la sentadilla bilateral (double-leg squat). De manera complementaria, trabajos como los de Ino et al. \[34], Usami et al. \[35] y Ohmura et al. \[36] refuerzan la relevancia de la captura con una sola cámara o smartphone, mientras que Kim et al. \[32] y Noël et al. \[26] permiten comparar conceptualmente los alcances de los enfoques monoculares, multicámara y tridimensionales. Todo ello indica que el análisis del movimiento sin marcadores ya no constituye un escenario marginal, sino una línea técnicamente activa y en expansión.

Junto con los avances tecnológicos, la literatura también ha problematizado el papel de la observación experta y de la evaluación visual del movimiento. Falk et al. \[10] muestran limitaciones importantes en la precisión de las evaluaciones visuales de movimientos lumbopélvicos durante sentadilla y peso muerto. En la misma dirección, Gomes et al. \[11] cuestionan la validez de muchas escalas visuales utilizadas en clínica para la sentadilla a una pierna, Ressman et al. \[12] reportan valores de confiabilidad entre moderados y sustanciales en su revisión con meta-análisis, y Nutarelli et al. \[13] muestran que la evaluación en video grabado puede resultar más confiable que la observación en tiempo real. Estos hallazgos son especialmente relevantes para la tesis, pues sostienen que el criterio experto sigue siendo útil, pero requiere estructura, criterios definidos y, de ser posible, apoyo de revisión por video. A ello se añade el contexto aplicado del entrenamiento y la prevención: Bonilla et al. \[3], El-Kotob et al. \[1] y Serafim et al. \[2] ayudan a justificar que el entrenamiento de fuerza, aun cuando es beneficioso para la salud, exige mayor atención a la calidad de la ejecución y a la prevención de errores técnicos potencialmente asociados con lesión o sobreuso.

En términos generales, el estado de la cuestión muestra que el tema ya cuenta con bases sólidas en estimación de pose, análisis del movimiento sin marcadores, biomecánica de la sentadilla, evaluación funcional y clasificación automática del movimiento. No obstante, la revisión también permite reconocer vacíos relevantes para la presente tesis. En primer lugar, una parte considerable de los estudios se concentra en la sentadilla a una pierna, el overhead squat, las tareas de salto o el análisis general de la calidad del movimiento, pero no en la sentadilla bilateral como foco principal. En segundo lugar, muchos trabajos validan ángulos, puntos anatómicos o cinemática global, pero no traducen esa información en compensaciones posturales específicas y asimetrías cinemáticas interpretables. En tercer lugar, los enfoques más automatizados tienden a priorizar salidas globales de clasificación o arquitecturas de deep learning de mayor complejidad, sin ofrecer siempre una relación clara entre la variable biomecánica observada y la decisión final. Finalmente, persiste la necesidad de articular sistemas accesibles con criterios de referencia basados en evaluación experta, en lugar de depender exclusivamente de laboratorios instrumentales o configuraciones multicámara avanzadas.

En consecuencia, la literatura revisada permite afirmar que existe una base científica suficiente para sustentar una propuesta basada en visión por computadora y estimación de pose 2D; sin embargo, también confirma la pertinencia del problema de investigación. Aún se observa espacio para una solución que combine cámara convencional, estimación de pose monocular, criterios biomecánicos interpretables y evaluación del desempeño técnico frente a una referencia experta, específicamente orientada a la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral. Ese vacío constituye, precisamente, el punto de entrada que define la contribución de la presente tesis.

## 2. Marco teórico

### 2.1. Visión por computadora

La visión por computadora es una rama de la inteligencia artificial y del procesamiento digital de imágenes orientada a permitir que los sistemas computacionales interpreten información visual obtenida a partir de imágenes o videos. Su aplicación en el análisis del movimiento humano ha crecido de manera significativa gracias a la disponibilidad de cámaras convencionales, modelos preentrenados y herramientas de procesamiento capaces de extraer información estructurada del cuerpo humano.

En el contexto de la salud y el rendimiento físico, la visión por computadora ha pasado de tareas centradas en el reconocimiento general de objetos a aplicaciones más específicas de análisis funcional, evaluación postural, cuantificación del ejercicio y seguimiento del movimiento. La revisión de Stenum et al. \[28] muestra precisamente esta transición, al documentar el uso creciente de la estimación de pose en contextos clínicos, de rehabilitación y de rendimiento humano. Del mismo modo, el desarrollo de modelos ligeros como BlazePose, propuesto por Bazarevsky et al. \[27], ha favorecido el uso de análisis corporal a partir de dispositivos de bajo costo y cámaras convencionales.

En el contexto de esta tesis, la visión por computadora constituye la base tecnológica para capturar y procesar la información visual contenida en videos de sentadilla bilateral, permitiendo derivar representaciones útiles para el análisis biomecánico del movimiento. No obstante, su adopción en escenarios funcionales exige no solo detectar el cuerpo, sino traducir la información visual a variables biomecánicas significativas, comparables y clínicamente o técnicamente interpretables.

### 2.2. Estimación de pose humana

La estimación de pose humana consiste en identificar automáticamente puntos anatómicos clave del cuerpo (landmarks) a partir de imágenes o secuencias de video. Estos puntos representan articulaciones o regiones anatómicas relevantes, como hombros, caderas, rodillas y tobillos, y permiten construir una representación geométrica del cuerpo útil para tareas de análisis postural y cinemático.

Los modelos de estimación de pose pueden operar en 2D o 3D, y su precisión depende de factores como el número de cámaras, la calidad de imagen, la existencia de oclusiones y la complejidad del movimiento. En estudios recientes, como el de Rode et al. \[29], se observa que los modelos monoculares abiertos presentan diferencias importantes de desempeño, especialmente cuando el movimiento involucra auto-oclusión, cambios profundos de perspectiva o segmentos con menor visibilidad. Por ello, la selección del modelo de pose no es una decisión menor, sino una parte central del diseño metodológico del sistema.

La importancia de esta técnica en la presente investigación radica en que proporciona la base sobre la cual se derivan variables biomecánicas observables y criterios de decisión interpretables para detectar compensaciones durante la sentadilla bilateral. Sin landmarks corporales consistentes, no sería posible calcular trayectorias, desplazamientos segmentarios ni diferencias bilaterales de forma estructurada.

### 2.3. Estimación de pose 2D

La estimación de pose 2D representa los puntos anatómicos clave del cuerpo (landmarks) en un plano bidimensional, utilizando coordenadas proyectadas sobre la imagen o el video. Este enfoque ofrece ventajas de accesibilidad y simplicidad, ya que puede funcionar con una sola cámara convencional. Sin embargo, también presenta limitaciones, especialmente en lo relacionado con profundidad, oclusión, dependencia del ángulo de cámara y precisión en movimientos complejos.

La literatura reciente respalda el uso de este enfoque cuando el objetivo no es reconstruir completamente la biomecánica 3D, sino detectar patrones funcionales observables. Trabajos como Straub y Powers \[31] y la revisión de Lopes et al. \[41] muestran que el análisis 2D puede ser útil para variables del plano frontal, particularmente en tronco y pelvis, aunque su validez depende de la tarea, la variable y el nivel de exactitud requerido. Esto es importante para la tesis, ya que varias de las compensaciones objetivo, como la inclinación lateral del tronco o el desplazamiento lateral de pelvis, pertenecen precisamente a un dominio observacional en el que el 2D puede resultar funcional.

En esta tesis, la estimación de pose 2D será empleada como la base computacional del sistema, asumiendo sus alcances y limitaciones dentro de un entorno controlado o semicontrolado de captura. Esta decisión responde a un criterio de viabilidad y accesibilidad, en contraste con enfoques multi-view 3D más complejos, como el descrito por Bae et al. \[24], que si bien ofrecen mayor fidelidad espacial, requieren múltiples cámaras, sincronización y una infraestructura considerablemente más exigente.

### 2.4. Biomecánica de la sentadilla bilateral

La sentadilla bilateral es un ejercicio funcional que involucra la coordinación del tronco, pelvis, cadera, rodilla y tobillo durante una secuencia de descenso y ascenso. Su ejecución requiere control motor, estabilidad, alineación segmentaria y distribución adecuada del movimiento entre ambos lados del cuerpo.

Desde una perspectiva biomecánica, el análisis de la sentadilla bilateral permite observar patrones de alineación corporal y compensaciones relacionadas con el control del movimiento. La revisión de Straub y Powers \[4] subraya que variables como la inclinación del tronco, la posición de la tibia, la profundidad, la separación de pies y la orientación del apoyo modifican las demandas mecánicas del ejercicio. Asimismo, Graber et al. \[5] muestran que la posición del tronco y del segmento distal de la pierna influye en la relación de momentos entre cadera y rodilla durante una sentadilla bilateral profunda, lo que evidencia la relevancia de observar la mecánica segmentaria y no solo el resultado global del movimiento.

Esto la convierte en un ejercicio de alto interés para el análisis funcional mediante visión por computadora, porque ofrece un escenario concreto en el que pueden observarse desalineaciones, estrategias compensatorias y asimetrías entre lados a partir de variables visibles desde video.

### 2.5. Compensaciones posturales durante la sentadilla bilateral

Las compensaciones posturales son modificaciones observables en la ejecución del movimiento que pueden reflejar estrategias de adaptación, pérdida de estabilidad o desequilibrios funcionales. En la sentadilla bilateral, algunas compensaciones relevantes son:

- inclinación lateral del tronco,
- desplazamiento lateral de pelvis,
- valgo dinámico visible,
- y asimetría bilateral general.

Estas compensaciones constituyen el foco principal del sistema propuesto, por lo que su definición y caracterización conceptual serán fundamentales para establecer criterios biomecánicos interpretables. En la literatura, una de las compensaciones más estudiadas es el valgo dinámico, cuya relevancia funcional se observa tanto en estudios de asociación 2D-3D como el de Erdman et al. \[6], como en revisiones específicas sobre movimientos basados en sentadilla, como la de Forman et al. \[7]. Si bien el valgo dinámico no agota el espectro de compensaciones posibles, sí ejemplifica cómo una alteración visible puede relacionarse con una organización biomecánica más compleja.

En el caso de la tesis, el interés no se centra en diagnosticar clínicamente cada compensación, sino en identificar de forma consistente patrones observables que sirvan como hallazgos biomecánicos preliminares dentro de una ejecución de sentadilla bilateral.

### 2.6. Asimetrías cinemáticas

Las asimetrías cinemáticas se refieren a diferencias observables entre ambos lados del cuerpo durante la ejecución del movimiento. En el contexto de la sentadilla bilateral, pueden manifestarse como diferencias en trayectoria, desplazamiento, alineación o sincronía entre segmentos homólogos.

La presente investigación considera estas asimetrías como una dimensión central de la evaluación del sistema, dado que representan un componente relevante del análisis funcional del ejercicio. Estudios como el de Mercadal-Baudart et al. \[15] muestran que la cuantificación sin marcadores desde una sola cámara puede capturar distintas métricas biomecánicas de ejercicios funcionales, aunque reportan errores mayores precisamente en algunas mediciones de asimetría. Esta observación es importante porque señala una zona donde el análisis requiere prudencia metodológica y delimitación clara.

Por ello, la tesis no plantea una reconstrucción exhaustiva de la asimetría corporal, sino una detección de asimetrías cinemáticas observables que puedan justificarse a partir de diferencias laterales en desplazamiento, alineación o comportamiento relativo de segmentos.

### 2.7. Criterios biomecánicos interpretables

Los criterios biomecánicos interpretables son reglas o condiciones que permiten traducir datos geométricos y cinemáticos en patrones comprensibles de compensación o asimetría. A diferencia de modelos de caja negra, este enfoque busca que la decisión del sistema pueda relacionarse explícitamente con variables observables y umbrales definidos.

Esta perspectiva resulta especialmente importante en la presente tesis, ya que el objetivo no es solo clasificar el movimiento, sino ofrecer resultados comprensibles y justificables a partir de la evidencia visual procesada. La diferencia con enfoques de deep learning más automatizados, como el de Shen et al. \[23], es que en este trabajo la decisión del sistema no dependerá exclusivamente de un patrón aprendido de extremo a extremo, sino de un encadenamiento explícito entre:

- puntos anatómicos clave del cuerpo (landmarks),
- variables biomecánicas,
- reglas de decisión,
- y resultado final.

En este sentido, la tesis se aproxima más a enfoques híbridos e interpretables como el de Kim y Park \[44], donde las variables de tronco, pelvis y rodilla se utilizan para explicar el desempeño funcional, aunque en la presente propuesta el núcleo seguirá siendo una lógica basada en criterios biomecánicos y no en una clasificación aprendida como componente principal.

### 2.8. Evaluación del desempeño de sistemas de clasificación

La evaluación del desempeño técnico de un sistema de detección o clasificación requiere el uso de métricas cuantitativas que permitan comparar sus resultados frente a un criterio de referencia. Entre las más relevantes para esta investigación se encuentran:

- exactitud,
- precisión,
- sensibilidad o recall,
- especificidad,
- F1-score,
- matriz de confusión,
- e índice Kappa de concordancia.

Estas métricas permitirán valorar la capacidad del sistema propuesto para detectar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral de manera consistente y comparable con la evaluación experta. La literatura revisada muestra diferentes formas de validación: algunos estudios comparan sistemas sin marcadores con sistemas de captura de movimiento basados en marcadores o con sistemas tridimensionales de referencia, como los trabajos de Ota et al. \[14], Pereira et al. \[16], Schmitz et al. \[40] y Bae et al. \[24]; otros comparan modelos frente a análisis clínico o criterio experto, como los estudios de Kim y Park \[44] y Falk et al. \[10].

En la presente tesis, el foco no estará en reproducir un gold standard instrumental de laboratorio, sino en determinar qué tan bien el sistema coincide con una referencia basada en evaluación experta. Esta elección es coherente con el alcance aplicado del estudio y con el objetivo de construir una herramienta funcional, interpretable y accesible.

### 2.9. Captura de movimiento sin marcadores y soluciones de bajo costo

El desarrollo reciente de la captura de movimiento sin marcadores ha abierto una línea importante de investigación orientada a reducir costos, simplificar la captura y ampliar el acceso al análisis del movimiento fuera del laboratorio. Revisiones como la de Armitano-Lago et al. \[21] muestran que los sistemas sin marcadores de bajo costo poseen fortalezas claras en portabilidad, accesibilidad y potencial de uso aplicado, pero también enfrentan debilidades relacionadas con precisión, oclusión, consistencia entre dispositivos y dependencia del protocolo de captura.

La aparición de soluciones como OpenCap amplía todavía más este escenario. Trabajos como los de Uhlrich et al. \[37], Lima et al. \[17] y Powell et al. \[18] muestran que las plataformas basadas en smartphones y reconstrucción sin marcadores pueden aproximarse a mediciones biomecánicas útiles en tareas funcionales, incluyendo la sentadilla y la sentadilla bilateral (double-leg squat). Estos estudios son relevantes para la tesis porque refuerzan la idea de que el análisis del movimiento con tecnologías accesibles ya no es solo una posibilidad teórica, sino una línea consolidada de desarrollo.

Sin embargo, la tesis se diferencia de esos enfoques en un aspecto importante: no busca una reconstrucción tridimensional general del movimiento, sino una detección bidimensional de compensaciones y asimetrías observables mediante criterios biomecánicos interpretables. En este sentido, las soluciones de bajo costo basadas en análisis sin marcadores actúan como marco de referencia y validación del campo, pero no definen directamente el núcleo del sistema propuesto.

### 2.10. Captura monocular, multi-view y condiciones de adquisición

Uno de los temas metodológicos más relevantes en la literatura reciente es la diferencia entre enfoques monoculares, de múltiples vistas (multi-view) y sistemas híbridos. Los estudios revisados muestran que el paso de una sola cámara a configuraciones múltiples permite reducir problemas de profundidad y oclusión, a costa de aumentar de forma considerable la complejidad técnica y operativa. Esto se observa tanto en trabajos de validación tridimensional sin marcadores, como el de Bae et al. \[24], como en comparaciones más recientes entre enfoques de una sola cámara y de múltiples cámaras, como el estudio de Kim et al. \[32].

Los artículos de Ino et al. \[34], Usami et al. \[35] y Ohmura et al. \[36] también muestran que los sistemas accesibles con una sola cámara o un solo smartphone pueden producir resultados útiles si se cuidan variables de captura como:

- orientación de la cámara,
- distancia al sujeto,
- alineación del plano de grabación,
- calidad de iluminación,
- y estabilidad del encuadre.

Por otro lado, Needham et al. \[38] sugieren que el rendimiento de la captura de movimiento sin marcadores puede variar cuando se abandona el entorno ideal de laboratorio y se trabaja en contextos más restringidos. Esta observación es especialmente valiosa para la tesis, porque justifica la necesidad de definir un protocolo de captura controlado o semicontrolado y delimitar con claridad el alcance del análisis.

En síntesis, la literatura respalda el uso de captura monocular cuando el objetivo es observacional y funcional, siempre que se acepten sus limitaciones y se controle cuidadosamente la adquisición de video. Esta conclusión es coherente con la decisión metodológica de la tesis.

### 2.11. Evaluación de la calidad del movimiento

El concepto de evaluación de la calidad del movimiento (movement quality assessment) ha ganado relevancia en la literatura contemporánea porque desplaza el análisis desde la mera medición angular hacia la interpretación funcional del movimiento. La revisión de alcance de Hofer et al. \[30] muestra que esta línea integra distintos tipos de sensores y representaciones para clasificar ejecuciones aceptables o aberrantes, mientras que la revisión con metaanálisis de Wijekulasuriya et al. \[46] profundiza en cómo se han desarrollado estas herramientas en poblaciones atléticas y qué tan consistentes resultan sus contenidos y criterios.

Este enfoque es muy cercano al propósito de la tesis. Aunque el sistema propuesto no pretende evaluar de forma exhaustiva toda la “calidad del movimiento” como constructo general, sí comparte su lógica principal: utilizar señales observables para identificar desviaciones funcionales relevantes durante una tarea concreta. En este caso, la tarea es la sentadilla bilateral y las desviaciones de interés son las compensaciones posturales y las asimetrías cinemáticas.

La diferencia es que la tesis propone una delimitación más específica y biomecánicamente estructurada, centrada en patrones observables concretos, en lugar de utilizar una escala global o una clasificación amplia de “movimiento bueno” o “malo”.

### 2.12. Evaluación experta, observación visual y revisión por video

La comparación frente a un criterio experto constituye un elemento central de la metodología de la tesis, por lo que resulta necesario sustentar teóricamente la validez y las limitaciones de la observación humana del movimiento. Los estudios revisados muestran una doble realidad. Por un lado, la evaluación visual sigue siendo ampliamente utilizada en clínica, deporte y tamizaje funcional. Por otro, su precisión y confiabilidad pueden variar según la experiencia del evaluador, la complejidad de la tarea y el modo de observación.

La evidencia presentada por Falk et al. \[10], Gomes et al. \[11], Ressman et al. \[12], Whatman et al. \[47] y Nutarelli et al. \[13] sugiere que:

- la evaluación visual tiene utilidad práctica,
- pero no siempre presenta validez o confiabilidad suficientes cuando se usa como única referencia,
- y que el análisis sobre video puede ofrecer ventajas frente a la observación en tiempo real.

Para la tesis, esto tiene dos implicancias importantes. Primero, justifica el uso de una referencia basada en evaluación experta en lugar de exigir necesariamente un laboratorio basado en marcadores. Segundo, sugiere que la referencia debe estar cuidadosamente estructurada, idealmente mediante fichas, criterios definidos y revisión de video, para reducir la variabilidad del juicio humano.

Así, la evaluación experta no debe entenderse como una verdad absoluta, sino como un criterio de referencia razonable y coherente con el alcance aplicado del estudio.

### 2.13. Síntesis del marco teórico

El marco teórico desarrollado permite sostener que la propuesta de investigación se sitúa en la intersección entre cuatro líneas conceptuales complementarias:

- la visión por computadora como base para capturar y representar el movimiento humano;
- la estimación de pose 2D como alternativa accesible para tareas funcionales observables;
- la biomecánica de la sentadilla bilateral como fundamento para definir variables e interpretar compensaciones;
- y la evaluación del movimiento como un proceso que puede beneficiarse de criterios explícitos, soporte tecnológico y validación frente a referencia experta.

En conjunto, estos elementos permiten delimitar con mayor precisión el alcance de la tesis. El sistema propuesto no pretende reconstruir toda la complejidad biomecánica del movimiento humano ni reemplazar los sistemas instrumentales de laboratorio. Su aporte se ubica en un nivel distinto: transformar video monocular en información biomecánicamente interpretable, útil para detectar compensaciones posturales y asimetrías cinemáticas observables durante la sentadilla bilateral.

# Capítulo 3. Metodología

## 1. Enfoque de investigación

La presente investigación tendrá un enfoque cuantitativo, debido a que se trabajará con variables observables derivadas de la estimación de pose 2D, se calcularán medidas geométricas y biomecánicas obtenidas a partir de videos de sentadilla bilateral y se evaluará el desempeño técnico del sistema mediante métricas numéricas de clasificación y concordancia. Este enfoque resulta coherente con la naturaleza del problema de investigación, ya que el objetivo no es interpretar percepciones subjetivas de los participantes, sino diseñar, implementar y evaluar una solución tecnológica capaz de transformar datos visuales en resultados biomecánicamente interpretables.

La elección de este enfoque también se alinea con antecedentes metodológicos de la literatura revisada. Estudios como los de Ota et al. \[14], Pereira et al. \[16], Bae et al. \[24] y Lima et al. \[17] muestran que la evaluación de sistemas de análisis del movimiento basados en video suele sustentarse en comparaciones cuantitativas de validez, confiabilidad y error, mientras que trabajos como los de Kim y Park \[44] y Falk et al. \[10] refuerzan la pertinencia de utilizar métricas objetivas para valorar el desempeño técnico frente a una referencia definida.

## 2. Tipo y alcance de investigación

La investigación será de tipo aplicada, porque busca desarrollar una solución tecnológica orientada a un problema concreto: la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral mediante visión por computadora. Su interés principal no se limita a ampliar conocimiento teórico de manera abstracta, sino a traducir ese conocimiento en un prototipo funcional capaz de operar sobre videos registrados con cámara convencional y producir resultados útiles para el análisis preliminar del movimiento.

En cuanto al alcance, la investigación será descriptivo-propositiva. Será descriptiva porque identificará y organizará variables biomecánicas observables, patrones posturales y criterios de decisión asociados a la ejecución de la sentadilla bilateral. A la vez, será propositiva porque, a partir de esa base conceptual y técnica, diseñará e implementará un sistema capaz de detectar dichos patrones de manera estructurada e interpretable. Este tipo de delimitación es coherente con propuestas recientes de análisis del movimiento que combinan descripción de variables, construcción de reglas o modelos y evaluación funcional del sistema resultante, como puede observarse en Ota et al. \[14], Kim y Park \[44], Hofer et al. \[30] y Noël et al. \[26].

## 3. Diseño de investigación

El diseño de la investigación será no experimental, transversal y tecnológico-propositivo. Será no experimental porque no se manipularán deliberadamente las condiciones corporales, funcionales o clínicas de las personas registradas en los videos; el estudio observará y analizará ejecuciones de sentadilla bilateral tal como ocurren bajo condiciones de captura definidas por el protocolo. Será transversal porque los videos se recopilarán y procesarán dentro de un periodo específico del desarrollo de la tesis, sin seguimiento longitudinal de los participantes. Finalmente, será tecnológico-propositivo porque culminará con el diseño, implementación y evaluación de un prototipo funcional.

Este diseño resulta congruente con el alcance aprobado del estudio y con la literatura metodológica del campo. Los trabajos de Ota et al. \[14], Dajime et al. \[43], Bae et al. \[24], Uhlrich et al. \[37] y Lima et al. \[17] muestran que las investigaciones sobre análisis del movimiento asistido por video, modelos de pose y evaluación de ejercicios funcionales suelen apoyarse en diseños observacionales y validaciones técnicas de prototipos o sistemas, sin requerir intervención experimental directa sobre la condición física de los participantes.

## 4. Población

La población del estudio estará conformada por videos de personas ejecutando sentadillas bilaterales, capturados mediante cámara convencional bajo condiciones definidas de registro. Desde el punto de vista metodológico, la unidad de análisis principal no será la persona en abstracto, sino el video procesable que contenga una ejecución observable del ejercicio y que permita extraer puntos anatómicos clave del cuerpo (landmarks), calcular variables biomecánicas y comparar los resultados del sistema con una referencia experta.

Esta definición poblacional es consistente con el problema de investigación, dado que el sistema propuesto operará sobre insumos audiovisuales y no sobre mediciones instrumentales directas de laboratorio. Además, se alinea con estudios que emplean registros en video como base para el análisis funcional del movimiento, la validación de sistemas markerless y la comparación con criterios expertos o referencias biomecánicas, como Ota et al. \[14], Mercadal-Baudart et al. \[15], Pereira et al. \[16], Lima et al. \[17] y Nutarelli et al. \[13].

## 5. Muestra

La muestra estará constituida por un conjunto de entre 20 y 30 videos válidos de sentadilla bilateral, seleccionados de manera no probabilística e intencional, de acuerdo con criterios técnicos y metodológicos definidos por el investigador. La elección de un muestreo no probabilístico responde a la necesidad de asegurar que cada video cumpla condiciones mínimas de utilidad analítica, como visibilidad corporal suficiente, calidad de captura, plano adecuado y posibilidad real de estimación de pose. En este estudio, la prioridad no será la representatividad estadística poblacional en sentido estricto, sino la disponibilidad de registros válidos para diseñar, probar y evaluar técnicamente el sistema.

La unidad de análisis de la muestra será un video válido por caso, correspondiente a una ejecución de sentadilla bilateral que pueda ser procesada de manera completa por el sistema y revisada por los evaluadores expertos. Los videos serán capturados preferentemente bajo un protocolo controlado o semicontrolado definido por el investigador, con el fin de reducir variaciones innecesarias en encuadre, iluminación, distancia y visibilidad corporal.

Este criterio resulta coherente con antecedentes del campo, donde la selección de registros suele condicionarse por la calidad de captura, el protocolo de grabación y la posibilidad de comparar resultados de manera consistente. La literatura revisada muestra que variables como la posición de cámara, el entorno, la visibilidad segmentaria y la oclusión influyen directamente en la confiabilidad del análisis, como señalan Lopes et al. \[41], Armitano-Lago et al. \[21], Kim et al. \[32], Ohmura et al. \[36] y Needham et al. \[38].

### 5.1. Criterios de inclusión

Los criterios de inclusión propuestos para la selección de la muestra serán los siguientes:

- videos de personas ejecutando sentadillas bilaterales completas o suficientemente observables para identificar la fase de descenso y ascenso;
- registros de personas adultas capaces de ejecutar la sentadilla bilateral sin asistencia externa;
- grabaciones con visibilidad del cuerpo completo o, como mínimo, de los segmentos necesarios para el análisis del tronco, pelvis y miembros inferiores;
- videos capturados con cámara convencional en vista frontal o en el plano definido por el protocolo metodológico;
- registros con calidad visual suficiente para la detección estable de puntos anatómicos clave del cuerpo (landmarks) en 2D;
- y videos que permitan una revisión experta razonable para clasificar compensaciones posturales y asimetrías cinemáticas observables.

### 5.2. Criterios de exclusión

Los criterios de exclusión propuestos serán los siguientes:

- videos con oclusión significativa del cuerpo o de segmentos clave para el análisis;
- grabaciones con iluminación deficiente, desenfoque excesivo o inestabilidad que afecte la detección de pose;
- videos con movimientos incompletos, fuera de plano o con interrupciones relevantes en la ejecución;
- registros de personas con asistencia externa, implementos que oculten segmentos relevantes o condiciones visibles que impidan una observación funcional razonable del movimiento;
- registros en los que el modelo de estimación de pose no detecte adecuadamente los puntos anatómicos requeridos;
- y videos cuya calidad no permita una clasificación experta consistente de los patrones de interés.

Estos criterios se sostienen en recomendaciones metodológicas y hallazgos del estado del arte que destacan la influencia del protocolo de captura, el encuadre y la visibilidad sobre la validez del análisis del movimiento sin marcadores, como se observa en Bae et al. \[24], Armitano-Lago et al. \[21], Ohmura et al. \[36] y Needham et al. \[38].

## 6. Técnicas e instrumentos de recolección de datos

La técnica principal de recolección de datos será el análisis de video, complementado por registro estructurado de resultados y evaluación experta. A partir de esta técnica, se recopilarán o seleccionarán videos de sentadilla bilateral para su procesamiento mediante el sistema propuesto y para su posterior comparación con una referencia basada en observación experta.

Los instrumentos de recolección de datos incluirán, como mínimo:

- ficha de registro de videos, para documentar código del caso, condiciones de captura, calidad visual y observaciones técnicas;
- matriz de puntos anatómicos clave del cuerpo (landmarks) y variables biomecánicas observables, para sistematizar la extracción y el cálculo de medidas;
- ficha de evaluación experta de compensaciones posturales y asimetrías cinemáticas, para generar la referencia de comparación;
- ficha de procesamiento del sistema, para registrar videos procesados, frames válidos, variables obtenidas y hallazgos detectados;
- y matriz de validación del sistema, para consolidar resultados de clasificación, concordancia y métricas de desempeño.

La inclusión de una ficha de evaluación experta y de revisión en video encuentra respaldo metodológico en la literatura que analiza la confiabilidad de la observación del movimiento. Falk et al. \[10], Gomes et al. \[11], Ressman et al. \[12], Whatman et al. \[47] y Nutarelli et al. \[13] muestran que la observación humana puede ser útil como referencia, pero mejora cuando se apoya en criterios definidos, estructura de evaluación y revisión audiovisual.

En el presente estudio, la referencia experta será construida con la participación de dos evaluadores con perfil de entrenador con experiencia en análisis del movimiento. Cada evaluador revisará los videos de forma estructurada mediante una ficha diseñada para clasificar los patrones de interés del estudio. En caso de incorporarse un tercer evaluador durante el desarrollo de la tesis, este podrá utilizarse para fortalecer el análisis de concordancia o resolver discrepancias mediante consenso o mayoría.

## 7. Procedimiento

El procedimiento metodológico se organizará en etapas secuenciales, cada una vinculada con uno o más objetivos específicos de la investigación.

### 7.1. Etapa 1: selección y organización de videos

En una primera etapa se recopilarán o seleccionarán los videos de sentadilla bilateral que formarán parte de la muestra. Cada registro será codificado y evaluado según criterios de calidad visual, plano de grabación, visibilidad corporal y posibilidad de procesamiento. Esta etapa permitirá depurar la muestra y asegurar que los datos de entrada cumplan condiciones mínimas para el análisis.

### 7.2. Etapa 2: estimación de pose e identificación de landmarks

En la segunda etapa se aplicará un modelo preentrenado de estimación de pose 2D para identificar puntos anatómicos clave del cuerpo (landmarks) relevantes para la sentadilla bilateral, como hombros, caderas, rodillas, tobillos y otros puntos necesarios para el cálculo de variables. La selección de esta etapa responde a la lógica central del sistema y se sustenta en antecedentes como BlazePose de Bazarevsky et al. \[27], así como en validaciones funcionales recientes presentadas por Ota et al. \[14], Pereira et al. \[16], Lima et al. \[17] y Kanko et al. \[19].

### 7.3. Etapa 3: cálculo de variables biomecánicas observables

En la tercera etapa se calcularán variables geométricas y biomecánicas derivadas de los landmarks detectados. Entre ellas se consideran la inclinación lateral del tronco, el desplazamiento lateral de pelvis, la alineación observacional rodilla-cadera-tobillo, así como diferencias bilaterales relativas. La definición de estas variables se fundamenta en la literatura biomecánica y metodológica vinculada a la sentadilla bilateral y al análisis 2D de tronco y pelvis, especialmente en Straub y Powers \[31], Straub y Powers \[4], Graber et al. \[5], Erdman et al. \[6] y Forman et al. \[7].

### 7.4. Etapa 4: diseño de criterios biomecánicos interpretables

En la cuarta etapa se establecerán criterios biomecánicos interpretables basados en umbrales, relaciones geométricas o condiciones observables para detectar patrones de compensación postural y asimetría cinemática. Esta etapa responde al interés central de la tesis por evitar una salida de caja negra y, en su lugar, generar resultados justificables a partir de variables visibles. La pertinencia de este enfoque se apoya en trabajos interpretables o híbridos como los de Kim y Park \[44], así como en la discusión conceptual sobre evaluación de la calidad del movimiento de Hofer et al. \[30].

### 7.5. Etapa 5: implementación del prototipo funcional

En la quinta etapa se desarrollará un prototipo capaz de cargar o procesar videos, estimar la pose corporal, calcular variables biomecánicas, aplicar criterios interpretables y generar resultados comprensibles sobre compensaciones y asimetrías. Desde la perspectiva de Ingeniería de Software, esta etapa integrará procesamiento de video, lógica de análisis, organización de datos y generación de salidas técnicas del sistema.

### 7.6. Etapa 6: evaluación del desempeño técnico del sistema

En la sexta etapa se compararán los resultados generados por el sistema con un criterio de referencia basado en evaluación experta. La comparación se realizará sobre las categorías o hallazgos definidos para cada video o ejecución analizada. Para ello, dos evaluadores expertos revisarán de manera independiente los videos mediante una ficha estructurada de compensaciones y asimetrías. Posteriormente, sus registros podrán compararse entre sí para valorar concordancia y utilizarse como referencia frente al sistema. En caso de discrepancia importante entre ambos evaluadores, se podrá recurrir a una revisión de consenso; si se incorpora un tercer evaluador, también podrá emplearse un criterio de mayoría. A partir de esta confrontación se calcularán métricas de desempeño como exactitud, precisión, sensibilidad, especificidad, F1-score y concordancia, según corresponda. Esta etapa encuentra sustento en la forma de validación reportada por Ota et al. \[14], Bae et al. \[24], Kim y Park \[44], Falk et al. \[10] y Nutarelli et al. \[13].

## 8. Técnicas de análisis de datos

El análisis de datos combinará técnicas descriptivas y métricas de evaluación del desempeño del sistema.

En primer lugar, se realizará un análisis descriptivo de los videos procesados, considerando cantidad de registros aceptados, número de frames o segmentos válidos, porcentaje de procesamiento exitoso y distribución de patrones detectados. Este análisis permitirá caracterizar el comportamiento general del sistema y de la muestra utilizada.

En segundo lugar, se analizarán las variables biomecánicas obtenidas por el sistema mediante medidas descriptivas como promedios, máximos, mínimos, rangos y desviación estándar, según la naturaleza de cada variable. Esto permitirá comprender cómo se distribuyen las medidas observables que sustentan las decisiones del sistema.

En tercer lugar, se construirá una matriz de confusión para comparar las clasificaciones o hallazgos del sistema con la referencia experta. A partir de ella se calcularán métricas de desempeño como exactitud, precisión, sensibilidad o recall, especificidad y F1-score. Estas métricas son coherentes con la literatura de validación de sistemas de clasificación y análisis del movimiento, tal como se observa en Kim y Park \[44], Bae et al. \[24] y las secciones metodológicas discutidas en el marco teórico.

En cuarto lugar, se considerará el cálculo de concordancia entre evaluadores mediante índice Kappa de Cohen, dado que la propuesta metodológica actual contempla dos evaluadores expertos. Si durante el desarrollo del estudio se incorpora un tercer evaluador, podrá ampliarse el análisis con Kappa de Fleiss. Esta decisión se justifica porque la comparación no se limitará a una sola métrica de clasificación, sino que buscará valorar también el grado de acuerdo entre sistema y referencia humana estructurada, en consonancia con los enfoques de confiabilidad discutidos por Ressman et al. \[12], Whatman et al. \[47] y Nutarelli et al. \[13].

En caso de que determinadas variables continuas del sistema se contrasten con mediciones continuas de referencia, podrá incorporarse adicionalmente análisis de correlación o error absoluto medio. No obstante, el núcleo del análisis permanecerá centrado en la detección de patrones observables y en el desempeño de clasificación del prototipo.

## 9. Aspectos éticos

La investigación considerará principios éticos básicos vinculados con el uso responsable de videos y datos personales. Si se utilizan registros capturados específicamente para la tesis, se deberá solicitar el consentimiento informado de las personas participantes, explicando el propósito académico del estudio, el tratamiento de los datos y el alcance no clínico del sistema. Si se emplean videos provenientes de una fuente previamente autorizada, se deberá verificar que su uso sea compatible con fines de investigación académica.

Asimismo, se procurará resguardar la identidad de los participantes mediante codificación, anonimización de registros y almacenamiento controlado de la información. Los videos no serán utilizados con fines distintos a los establecidos en la investigación. Del mismo modo, se dejará explícito que el sistema propuesto no tiene finalidad diagnóstica clínica, sino que constituye una herramienta de apoyo para el análisis preliminar del movimiento.

También se recomienda declarar el uso responsable de herramientas computacionales e inteligencia artificial dentro del proceso de desarrollo y redacción, en concordancia con los lineamientos institucionales aplicables y con principios de integridad académica.

## 10. Cronograma propuesto

El cronograma del estudio se ajustará al calendario real del Programa de Titulación y a la disponibilidad de actividades académicas del periodo correspondiente. De manera general, las fases previstas comprenden:

- revisión y consolidación del marco metodológico;
- definición del protocolo de captura y de los instrumentos de registro;
- recopilación o selección de videos;
- desarrollo e integración del prototipo funcional;
- procesamiento de videos y cálculo de variables;
- evaluación experta y validación técnica del sistema;
- análisis de resultados;
- y redacción final del documento de tesis.

En la versión final del documento, este cronograma podrá presentarse como tabla mensual o matriz de actividades por semanas, de acuerdo con el formato que solicite la universidad o el asesor.

## Nota para la siguiente etapa

La presente base de redacción deja estructurado el documento hasta el Capítulo 3, incorporando:

- título final confirmado,
- corrección de la pregunta principal,
- ajuste de variables y dimensiones,
- matriz preliminar de operacionalización,
- estructura del estado del arte y marco teórico,
- base metodológica alineada a la maqueta aprobada,
- integración de artículos núcleo y complementarios,
- y ampliación bibliográfica hasta superar el mínimo objetivo.

La siguiente etapa consistirá en:

- insertar citas formales según el estilo IEEE u otro formato definido por el asesor,
- reforzar con datos estadísticos el planteamiento del problema y la justificación,
- convertir parte de la síntesis bibliográfica en tablas y recursos visuales del estado del arte,
- revisar el ajuste final de muestra, instrumentos y cronograma con el asesor,
- y preparar la transición hacia resultados esperados, anexos e integración bibliográfica final.

# Referencias

\[1] El-Kotob et al., “Resistance training and health in adults: an overview of systematic reviews,” PubMed / Appl Physiol Nutr Metab, 2020. doi: 10.1139/apnm-2020-0245. Disponible en: https://pubmed.ncbi.nlm.nih.gov/33054335/

\[2] Serafim et al., “Which resistance training is safest to practice? A systematic review,” PMC / Journal of Orthopaedic Surgery and Research, 2023. doi: 10.1186/s13018-023-03781-x. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC10099898/

\[3] Bonilla et al., “Exercise Selection and Common Injuries in Fitness Centers: A Systematic Integrative Review and Practical Recommendations,” IJERPH / MDPI / PMC, 2022. doi: 10.3390/ijerph191912710. Disponible en: https://www.mdpi.com/1660-4601/19/19/12710

\[4] Straub y Powers, “A Biomechanical Review of the Squat Exercise: Implications for Clinical Practice,” Int J Sports Phys Ther / PMC, 2024. doi: 10.26603/001c.94600. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC10987311/

\[5] Graber et al., “The effect of trunk and shank position on the hip-to-knee moment ratio in a bilateral squat,” Physical Therapy in Sport / PubMed, 2023. doi: 10.1016/j.ptsp.2023.03.005. Disponible en: https://pubmed.ncbi.nlm.nih.gov/37001335/

\[6] Erdman et al., “A 2D video-based assessment is associated with 3D biomechanical contributors to dynamic knee valgus in the coronal plane,” Frontiers in Sports and Active Living / PMC, 2024. doi: 10.3389/fspor.2024.1352286. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC10978775/

\[7] Forman et al., “The Use of Elastic Resistance Bands to Reduce Dynamic Knee Valgus in Squat-Based Movements: A Narrative Review,” Int J Sports Phys Ther / PMC, 2023. doi: 10.26603/001c.87764. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC10547095/

\[8] Liu et al., “Effects of Barbell Squats with Asymmetric Loading on the Joint Moment and Muscle Activity of Lower Limbs,” J Hum Kinet / PubMed / PMC, 2025/2026. doi: 10.5114/jhk/202020. Disponible en: https://pubmed.ncbi.nlm.nih.gov/41766814/

\[9] Pellicciari et al., “Associations Between Anthropometric Characteristics, Self-Reported Musculoskeletal and Visceral Symptoms, and Squat Movement Quality: A Cross-Section Study,” J Funct Morphol Kinesiol / PMC, 2026. doi: 10.3390/jfmk11010086. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC13028339/

\[10] Falk et al., “How accurate are visual assessments by physical therapists of lumbo-pelvic movements during the squat and deadlift?,” Physical Therapy in Sport / ScienceDirect, 2021. doi: 10.1016/j.ptsp.2021.05.011. Disponible en: https://www.sciencedirect.com/science/article/pii/S1466853X21000924

\[11] Gomes et al., “Are visual assessments of the single-leg squat valid to be used in clinical practice? A systematic review of measurement properties based on the COSMIN guideline,” PubMed / Physical Therapy in Sport, 2023. doi: 10.1016/j.ptsp.2023.07.009. Disponible en: https://pubmed.ncbi.nlm.nih.gov/37549590/

\[12] Ressman et al., “Visual assessment of movement quality in the single leg squat test: a review and meta-analysis of inter-rater and intrarater reliability,” PMC / BMJ Open Sport Exerc Med, 2019. doi: 10.1136/bmjsem-2019-000541. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC6579566/

\[13] Nutarelli et al., “Inter-rater reliability of real-time compared to recorded single-leg squat assessment with the qualitative analysis of single leg loading assessment tool (QASLS) in healthy individuals,” Musculoskeletal Science and Practice / ScienceDirect, 2026. doi: 10.1016/j.msksp.2025.103445. Disponible en: https://www.sciencedirect.com/science/article/pii/S2468781225001936

\[14] Ota et al., “Verification of reliability and validity of motion analysis systems during bilateral squat using human pose tracking algorithm,” Gait & Posture / ScienceDirect, 2020. doi: 10.1016/j.gaitpost.2020.05.027. Disponible en: https://www.sciencedirect.com/science/article/pii/S0966636220301776

\[15] Mercadal-Baudart et al., “Exercise quantification from single camera view markerless 3D pose estimation,” Heliyon / ScienceDirect, 2024. doi: 10.1016/j.heliyon.2024.e27596. Disponible en: https://www.sciencedirect.com/science/article/pii/S2405844024036272

\[16] Pereira et al., “Markerless Pixel-Based Pipeline for Quantifying 2D Lower Limb Kinematics During Squatting: A Preliminary Validation Study,” Biomechanics / MDPI, 2026. doi: 10.3390/biomechanics6010001. Disponible en: https://www.mdpi.com/2673-7078/6/1/1

\[17] Lima et al., “Validity and reliability of trunk and lower-limb kinematics during squatting, hopping, jumping and side-stepping using OpenCap markerless motion capture application,” J Sports Sci / PubMed, 2024. doi: 10.1080/02640414.2024.2415233. Disponible en: https://pubmed.ncbi.nlm.nih.gov/39444219/

\[18] Powell et al., “Validation of OpenCap on lower extremity kinematics during functional tasks,” Journal of Biomechanics / ScienceDirect, 2025. doi: 10.1016/j.jbiomech.2025.112602. Disponible en: https://www.sciencedirect.com/science/article/pii/S0021929025001137

\[19] Kanko et al., “Markerless motion capture estimates of lower extremity kinematics and kinetics are comparable to marker-based across 8 movements,” J Sports Sci / PubMed, 2023. doi: 10.1080/02640414.2023.2231987. Disponible en: https://pubmed.ncbi.nlm.nih.gov/37552921/

\[20] Yoma et al., “Reliability and validity of lower extremity and trunk kinematics measured with markerless motion capture during sports-related and functional tasks: A systematic review,” Journal of Sports Sciences / Taylor & Francis, 2025. doi: 10.1080/02640414.2025.2518359. Disponible en: https://www.tandfonline.com/doi/full/10.1080/02640414.2025.2518359

\[21] Armitano-Lago et al., “A SWOT Analysis of Portable and Low-Cost Markerless Motion Capture Systems to Assess Lower-Limb Musculoskeletal Kinematics in Sport,” Frontiers in Sports and Active Living / PubMed / PMC, 2022. doi: 10.3389/fspor.2021.809898. Disponible en: https://pubmed.ncbi.nlm.nih.gov/35146425/

\[22] Ogura et al., “Are we there yet? A systematic review and meta-analysis of the validity and reliability of automated markerless motion capture systems during jumping tasks,” J Sports Sci / PubMed, 2025. doi: 10.1080/02640414.2025.2589689. Disponible en: https://pubmed.ncbi.nlm.nih.gov/41293872/

\[23] Shen et al., “Markerless vision-based functional movement screening movements evaluation with deep neural networks,” iScience / ScienceDirect, 2024. doi: 10.1016/j.isci.2023.108705. Disponible en: https://www.sciencedirect.com/science/article/pii/S2589004223027827

\[24] Bae et al., “Concurrent validity and test reliability of the deep learning markerless motion capture system during the overhead squat,” Scientific Reports / Nature / PMC, 2024. doi: 10.1038/s41598-024-79707-2. Disponible en: https://www.nature.com/articles/s41598-024-79707-2

\[25] Sadeghi et al., “Squat errors classification based on National Academy of Sports Medicine guidelines using IMU and deep learning algorithms,” Computers in Biology and Medicine / ScienceDirect, 2025. doi: 10.1016/j.compbiomed.2025.110962. Disponible en: https://www.sciencedirect.com/science/article/pii/S0010482525013149

\[26] Noël et al., “A conceptual framework and review of multi-method approaches for 3D markerless motion capture in sports and exercise,” J Sports Sci / PubMed, 2025. doi: 10.1080/02640414.2025.2544667. Disponible en: https://pubmed.ncbi.nlm.nih.gov/40198152/

\[27] Bazarevsky et al., “BlazePose: On-device Real-time Body Pose tracking,” arXiv / CVPR Workshop, 2020. doi: 10.48550/arXiv.2006.10204. Disponible en: https://arxiv.org/abs/2006.10204

\[28] Stenum et al., “Applications of Pose Estimation in Human Health and Performance across the Lifespan,” Sensors / MDPI, 2021. doi: 10.3390/s21217315. Disponible en: https://www.mdpi.com/1424-8220/21/21/7315

\[29] Rode et al., “Assessment of monocular human pose estimation models for clinical movement analysis,” Scientific Reports / Nature / PMC, 2025. doi: 10.1038/s41598-025-22626-7. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC12589393/

\[30] Hofer et al., “Human Movement Quality Assessment Using Sensor Technologies in Recreational and Professional Sports: A Scoping Review,” Sensors / PMC, 2022. doi: 10.3390/s22134786. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC9269395/

\[31] Straub y Powers, “Utility of 2D Video Analysis for Assessing Frontal Plane Trunk and Pelvis Motion during Stepping, Landing, and Change in Direction Tasks: A Validity Study,” Int J Sports Phys Ther / PMC, 2022. doi: 10.26603/001c.30994. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC8805121/

\[32] Kim et al., “Verification of Markerless Gait Analysis: Multi-Camera and Single-Camera Approaches in Comparison to Marker-Based Gait Analysis,” Medicina / MDPI, 2026. doi: 10.3390/medicina62020418. Disponible en: https://www.mdpi.com/1648-9144/62/2/418

\[33] Edwards et al., “The Validity and Usability of Markerless Motion Capture and Inertial Measurement Units for Quantifying Dynamic Movements,” Med Sci Sports Exerc / PubMed, 2025. doi: 10.1249/MSS.0000000000003579. Disponible en: https://pubmed.ncbi.nlm.nih.gov/39733226/

\[34] Ino et al., “Validity of AI-Based Gait Analysis for Simultaneous Measurement of Bilateral Lower Limb Kinematics Using a Single Video Camera,” Sensors / PubMed / PMC, 2023. doi: 10.3390/s23249799. Disponible en: https://pubmed.ncbi.nlm.nih.gov/38139644/

\[35] Usami et al., “Gait Analysis Using an Artificial Intelligence-Based Motion Capture System With a Single Smartphone Camera,” Cureus / PubMed / PMC, 2025. doi: 10.7759/cureus.87837. Disponible en: https://pubmed.ncbi.nlm.nih.gov/40809664/

\[36] Ohmura et al., “Assessing the Validity and Reliability of a Markerless Motion Capture System for Sagittal-Plane Gait Range of Motion,” Cureus / PubMed / PMC, 2025. doi: 10.7759/cureus.99875. Disponible en: https://pubmed.ncbi.nlm.nih.gov/41583137/

\[37] Uhlrich et al., “OpenCap: Human movement dynamics from smartphone videos,” PLoS Comput Biol / PubMed, 2023. doi: 10.1371/journal.pcbi.1011462. Disponible en: https://pubmed.ncbi.nlm.nih.gov/37856442/

\[38] Ruder et al., “Evaluating the Agreement of Markerless Motion Capture for Joint Angle Estimation in a Constrained Hallway Setting Compared With a Traditional Laboratory Setting,” J Appl Biomech / PubMed, 2026. doi: 10.1123/jab.2025-0265. Disponible en: https://pubmed.ncbi.nlm.nih.gov/41679295

\[39] Horsak et al., “Validity and reliability of monocular 3D markerless gait analysis in simulated pathological gait: A comparative study with OpenCap,” Journal of Biomechanics / ScienceDirect, 2025. doi: 10.1016/j.jbiomech.2025.112986. Disponible en: https://www.sciencedirect.com/science/article/pii/S0021929025004981

\[40] Schmitz et al., “The measurement of in vivo joint angles during a squat using a single camera markerless motion capture system as compared to a marker based system,” Gait & Posture / ScienceDirect, 2015. doi: 10.1016/j.gaitpost.2015.01.028. Disponible en: https://www.sciencedirect.com/science/article/pii/S0966636215000314

\[41] Lopes et al., “Reliability and Validity of Frontal Plane Kinematics of the Trunk and Lower Extremity Measured With 2-Dimensional Cameras During Athletic Tasks: A Systematic Review With Meta-analysis,” J Orthop Sports Phys Ther / PubMed, 2018. doi: 10.2519/jospt.2018.8006. Disponible en: https://pubmed.ncbi.nlm.nih.gov/29895235/

\[42] Curnow et al., “Lower limb biomechanics in femoroacetabular impingement syndrome, asymptomatic cam morphology, and controls during bilateral and single-leg squatting,” Gait & Posture / ScienceDirect, 2026. doi: 10.1016/j.gaitpost.2026.110131. Disponible en: https://www.sciencedirect.com/science/article/pii/S0966636226000391

\[43] Dajime, Smith y Zhang, “Automated classification of movement quality using the Microsoft Kinect V2 sensor,” Computers in Biology and Medicine / ScienceDirect, 2020. doi: 10.1016/j.compbiomed.2020.104021. Disponible en: https://www.sciencedirect.com/science/article/pii/S0010482520303528

\[44] Kim y Park, “Smartphone-Based Interpretable Machine Learning for Classifying Single-Leg Squat Performance Using Trunk, Pelvic, and Knee Kinematics: Cross-Sectional Study,” JMIR mHealth and uHealth / PubMed / ScienceDirect, 2026. doi: 10.2196/85126. Disponible en: https://pubmed.ncbi.nlm.nih.gov/41818471/

\[45] Kianifar et al., “Automated Assessment of Dynamic Knee Valgus and Risk of Knee Injury During the Single Leg Squat,” IEEE J Transl Eng Health Med / PMC, 2017. doi: 10.1109/JTEHM.2017.2736559. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC5706595/

\[46] Wijekulasuriya et al., “The Development and Content of Movement Quality Assessments in Athletic Populations: A Systematic Review and Multilevel Meta-Analysis,” PMC / Sports Medicine - Open, 2025. doi: 10.1186/s40798-025-00813-0. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC11757847/

\[47] Whatman et al., “Classification of Lower Extremity Movement Patterns Based on Visual Assessment: Reliability and Correlation With 2-Dimensional Video Analysis,” J Athl Train / PMC, 2014. doi: 10.4085/1062-6050-49.3.17. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC4080603/
