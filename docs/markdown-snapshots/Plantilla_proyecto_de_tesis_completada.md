Resultado de imagen de universidad tecnologica del peru

**UTP Lima Sur**

**Ingeniería de Software**

**Plan de Tesis**

Sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables para la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral en Lima Sur, 2026

**Integrantes**

Chapoñan Castro, Geancarlos Elías (U19301344)

**Docente**

Linares Luján, Guillermo Alberto

Lima, Perú

2026

[1\. PROBLEMA DE INVESTIGACIÓN 4](#1-problema-de-investigación)

[2\. PREGUNTA GENERAL Y ESPECÍFICAS 6](#2-pregunta-general-y-específicas)

[2.1 Pregunta general 6](#21-pregunta-general)

[2.2 Preguntas específicas 6](#22-preguntas-específicas)

[3\. OBJETIVO GENERAL Y ESPECÍFICOS 7](#3-objetivo-general-y-específicos)

[3.1 Objetivo General 7](#31-objetivo-general)

[3.2 Objetivos Específicos 7](#32-objetivos-específicos)

[4\. JUSTIFICACIÓN 7](#4-justificación)

[4.1 Justificación teórica 7](#41-justificación-teórica)

[4.2 Justificación metodológica 8](#42-justificación-metodológica)

[4.3 Justificación práctica 8](#43-justificación-práctica)

[5\. REVISIÓN DE LA LITERATURA ACTUAL O ESTADO DEL ARTE 9](#5-revisión-de-la-literatura-actual-o-estado-del-arte)

[6\. MARCO TEÓRICO 13](#6-marco-teórico)

[Variable 1: Sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables. 13](#variable-1-sistema-de-visión-por-computadora-basado-en-estimación-de-pose-2d-y-criterios-biomecánicos-interpretables)

[Variable 2: Desempeño técnico del sistema en la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral. 18](#variable-2-desempeño-técnico-del-sistema-en-la-detección-de-compensaciones-posturales-y-asimetrías-cinemáticas-durante-la-sentadilla-bilateral)

[7\. HIPÓTESIS 23](#7-hipótesis)

[7.1 Hipótesis general 23](#71-hipótesis-general)

[7.2 Hipótesis específicas 23](#72-hipótesis-específicas)

[8\. METODOLOGÍA 23](#8-metodología)

[8.1 Tipo y diseño 23](#81-tipo-y-diseño)

[8.2 Población 24](#82-población)

[8.3 Muestra 24](#83-muestra)

[8.4 Muestreo 25](#84-muestreo)

[8.5 Técnicas e instrumentos 25](#85-técnicas-e-instrumentos)

[8.6 Análisis de datos 28](#86-análisis-de-datos)

[8.7 Aspectos éticos 29](#87-aspectos-éticos)

[9\. CRONOGRAMA DE TRABAJO 29](#9-cronograma-de-trabajo)

[10\. PRESUPUESTO 34](#10-presupuesto)

[11\. BIBLIOGRAFÍA 35](#11-bibliografía)

[12\. ANEXOS 41](#12-anexos)

[Anexo 1 41](#anexo-1)

[Anexo 2 43](#anexo-2)

[Anexo 3 46](#anexo-3)

[Anexo 4 47](#anexo-4)

# 1. PROBLEMA DE INVESTIGACIÓN

El análisis del movimiento humano es una actividad relevante en múltiples escenarios vinculados con la salud, el entrenamiento físico, la rehabilitación y la prevención de alteraciones funcionales. Esta relevancia se refuerza por el creciente interés del entrenamiento de fuerza en población adulta y por la evidencia que vincula este tipo de práctica con beneficios funcionales y de salud cuando se aplica de forma adecuada. La revisión de El-Kotob et al. \[1] muestra que el entrenamiento de fuerza se ha consolidado como una estrategia de interés en población adulta, mientras que trabajos como el de Serafim et al. \[2] y la revisión integrativa de Bonilla et al. \[3] recuerdan que la seguridad del entrenamiento depende en buena medida de la calidad de la ejecución técnica, del control de la carga y de la adecuada selección de ejercicios.

Dentro de este campo, la sentadilla bilateral representa un ejercicio funcional de alta utilidad, ya que permite observar la relación entre estabilidad, control motor, alineación corporal y coordinación de distintos segmentos durante una tarea de flexo-extensión simultánea del tren inferior. Su uso se ha extendido tanto en evaluación física como en programas de entrenamiento y seguimiento corporal. Desde el punto de vista biomecánico, revisiones como la de Straub y Powers \[4] y estudios como el de Graber et al. \[5] muestran que la sentadilla bilateral es una tarea rica en información segmentaria, debido a que pone en juego la coordinación entre tronco, pelvis, cadera, rodilla y tobillo.

Durante la ejecución de la sentadilla bilateral pueden manifestarse diversas compensaciones posturales y asimetrías cinemáticas, como inclinación lateral del tronco, desplazamiento lateral de pelvis, colapso medial visible de rodillas o diferencias entre ambos lados del cuerpo. La literatura reciente también ha mostrado interés en patrones como el valgo dinámico, la distribución asimétrica de la carga y la calidad general del movimiento, tanto en estudios observacionales como en análisis biomecánicos y evaluaciones aplicadas de la calidad de la sentadilla. En ese sentido, Erdman et al. \[6], Forman et al. \[7], Liu et al. \[8] y Kaartinen et al. \[9] aportan antecedentes relevantes.

La identificación de estos patrones suele depender de la experiencia del evaluador, del contexto de observación y, en escenarios más especializados, del uso de tecnologías biomecánicas avanzadas. Sin embargo, distintos trabajos evidencian que la evaluación visual aislada puede presentar limitaciones relevantes. Falk et al. \[10] reportan restricciones en la precisión de la evaluación visual de movimientos lumbopélvicos durante sentadilla y peso muerto, mientras que Gomes et al. \[11], Ressman et al. \[12] y Nutarelli et al. \[13] muestran que la validez y confiabilidad de herramientas observacionales pueden variar, e incluso mejorar cuando el análisis se realiza sobre video en lugar de observación en tiempo real. Esta situación genera limitaciones de acceso, variabilidad en la interpretación y dificultades para disponer de evaluaciones rápidas, consistentes y escalables.

En los últimos años, la visión por computadora y los modelos de estimación de pose humana han ofrecido nuevas posibilidades para analizar movimientos corporales a partir de videos capturados con cámaras convencionales. Dichos avances permiten identificar puntos anatómicos clave del cuerpo (landmarks) en dos dimensiones y derivar métricas geométricas que pueden utilizarse para representar ciertos comportamientos del movimiento. Trabajos como los de Ota et al. \[14], Mercadal-Baudart et al. \[15], Pereira et al. \[16], Lima et al. \[17], Powell et al. \[18] y Kanko et al. \[19] muestran que el análisis del movimiento sin marcadores ya puede alcanzar niveles útiles de validez técnica en diferentes tareas funcionales, mientras que revisiones como las de Halilaj et al. \[20], Armitano-Lago et al. \[21] y Needham et al. \[22] evidencian el crecimiento sostenido de este campo en soluciones accesibles y su proyección hacia contextos aplicados.

Sin embargo, en gran parte de la literatura y de las soluciones tecnológicas disponibles, el análisis se concentra en clasificar la técnica de forma general, en validar la precisión de ángulos o en comparar tecnologías, sin traducir necesariamente esos datos en compensaciones posturales específicas, biomecánicamente explicables y fácilmente interpretables. Este vacío es visible tanto en estudios centrados en clasificación automática del movimiento como en enfoques basados en deep learning o en plataformas tridimensionales sin marcadores de mayor complejidad, como se observa en los trabajos de Shen et al. \[23], Bae et al. \[24], Sadeghi et al. \[25] y Noël et al. \[26].

En consecuencia, se identifica una brecha técnica y metodológica: la necesidad de diseñar un sistema que, utilizando estimación de pose 2D y criterios biomecánicos interpretables, permita detectar de manera explícita compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral, a partir de videos capturados con una cámara convencional. Esta necesidad se vuelve particularmente relevante en escenarios donde no se cuenta con laboratorios de captura de movimiento, sistemas basados en marcadores o configuraciones multicámara avanzadas, pero sí con interés por disponer de una evaluación funcional más estructurada. Bajo este panorama, el desarrollo de un prototipo funcional orientado al análisis explicable del movimiento humano se justifica como una respuesta tecnológicamente viable y metodológicamente coherente.

# 2. PREGUNTA GENERAL Y ESPECÍFICAS

## 2.1 Pregunta general

¿Cuál es el desempeño técnico del sistema de visión por computadora propuesto para detectar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral, en comparación con un criterio de referencia basado en evaluación experta en Lima Sur, 2026?

## 2.2 Preguntas específicas

- a. ¿Qué puntos anatómicos clave del cuerpo (landmarks) en 2D son relevantes para el análisis biomecánico observable de la sentadilla bilateral mediante visión por computadora?
- b. ¿Qué variables biomecánicas observables pueden calcularse a partir de los puntos anatómicos clave del cuerpo (landmarks) en 2D para representar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral?
- c. ¿Qué criterios biomecánicos interpretables pueden diseñarse para detectar patrones como inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y asimetría bilateral general?
- d. ¿Cómo implementar un prototipo funcional que procese videos de sentadilla bilateral y genere resultados interpretables sobre la ejecución del movimiento?
- e. ¿Cuál es el desempeño técnico del sistema propuesto en la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral, en comparación con un criterio de referencia basado en evaluación experta?

# 3. OBJETIVO GENERAL Y ESPECÍFICOS

## 3.1 Objetivo General

Diseñar e implementar un sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables para detectar compensaciones posturales y asimetrías cinemáticas durante la ejecución de sentadillas bilaterales en Lima Sur, 2026.

## 3.2 Objetivos Específicos

- a. Identificar los puntos anatómicos clave del cuerpo (landmarks) en 2D relevantes para el análisis biomecánico observable de la sentadilla bilateral a partir de videos capturados con cámara convencional.
- b. Definir variables biomecánicas observables derivadas de los puntos anatómicos clave del cuerpo (landmarks) en 2D que permitan representar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral.
- c. Diseñar criterios biomecánicos interpretables para la detección de patrones posturales como inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y asimetría bilateral general.
- d. Implementar un prototipo funcional que procese videos de sentadilla bilateral, estime la postura corporal y genere resultados interpretables sobre las compensaciones posturales y asimetrías cinemáticas detectadas.
- e. Evaluar el desempeño técnico del sistema propuesto mediante métricas de clasificación y concordancia frente a un criterio de referencia basado en evaluación experta.

# 4. JUSTIFICACIÓN

## 4.1 Justificación teórica

Desde el punto de vista teórico, la investigación aporta a la integración entre visión por computadora, estimación de pose humana y biomecánica observacional aplicada al análisis de ejercicios funcionales. Su relevancia radica en organizar una base conceptual que permita transformar puntos anatómicos clave del cuerpo (landmarks) en dos dimensiones en variables biomecánicas observables e interpretables. Asimismo, contribuye a precisar criterios para identificar compensaciones y asimetrías durante la sentadilla bilateral, fortaleciendo el vínculo entre representación computacional del movimiento y análisis funcional del cuerpo humano. Esta articulación teórica se sostiene en antecedentes que van desde la estimación general de pose, desarrollada por Bazarevsky et al. \[27], Stenum et al. \[28] y Rode et al. \[29], hasta estudios específicos sobre sentadilla, análisis del movimiento sin marcadores y evaluación de la calidad del movimiento, como los de Ota et al. \[14], Pereira et al. \[16], Hofer et al. \[30] y Noël et al. \[26].

## 4.2 Justificación metodológica

Metodológicamente, la propuesta es pertinente porque establece un procedimiento sistemático para la captura o selección de videos, el procesamiento de imágenes, la extracción de puntos anatómicos clave del cuerpo (landmarks), el cálculo de variables biomecánicas observables, la aplicación de criterios biomecánicos interpretables y la evaluación del desempeño técnico del sistema. Este enfoque no solo favorece la trazabilidad del desarrollo, sino que además puede adaptarse posteriormente a otros ejercicios funcionales o contextos similares de análisis del movimiento. La pertinencia del método se refuerza con literatura que muestra tanto las capacidades como las limitaciones del análisis del movimiento sin marcadores, ya sea en soluciones monoculares o multicámara. Entre estos antecedentes destacan Straub y Powers \[31], Bae et al. \[24], Halilaj et al. \[20], Armitano-Lago et al. \[21], Kim et al. \[32] y Kanko et al. \[33].

## 4.3 Justificación práctica

En el plano práctico, la investigación busca generar una herramienta de apoyo para el análisis preliminar de la sentadilla bilateral en contextos de entrenamiento, evaluación funcional y seguimiento corporal. El sistema propuesto no pretende reemplazar la evaluación especializada, sino facilitar una detección inicial de compensaciones y asimetrías de forma más accesible y consistente. Esto puede resultar útil en escenarios donde no se cuenta con equipamiento biomecánico avanzado, pero sí con cámaras convencionales y necesidad de observación estructurada del movimiento. En ese sentido, el aporte del sistema no radica en negar que algunas compensaciones visibles puedan identificarse a simple vista, sino en transformar esa observación en un procedimiento técnico estandarizado, interpretable, reproducible y evaluable frente a expertos, con trazabilidad de variables, reglas de decisión y resultados.

Desde una perspectiva aplicada, esta utilidad se relaciona con dos problemas concretos identificados en la literatura: por un lado, la necesidad de controlar mejor la ejecución técnica y reducir errores potencialmente vinculados con sobreuso o lesión, como señalan Bonilla et al. \[3] y Serafim et al. \[2]; por otro, la variabilidad de las evaluaciones visuales cuando no se dispone de apoyo tecnológico o de revisión por video, aspecto documentado por Falk et al. \[10], Gomes et al. \[11], Ressman et al. \[12] y Nutarelli et al. \[13].

Complementariamente, la dimensión tecnológica de la propuesta se alinea con la formación en Ingeniería de Software al involucrar el diseño de un prototipo funcional, el procesamiento de video, la integración de modelos preentrenados de estimación de pose 2D, el cálculo de variables geométricas, la aplicación de reglas de decisión y la generación de resultados interpretables. Asimismo, permite abordar el sistema como una solución informática evaluable, medible y potencialmente escalable hacia otras aplicaciones del análisis del movimiento humano.

La bibliografía revisada muestra además que el campo tecnológico avanza en distintas direcciones: sistemas monoculares accesibles, como los estudiados por Ino et al. \[34], Usami et al. \[35] y Ohmura et al. \[36]; soluciones de bajo costo como OpenCap, abordadas por Uhlrich et al. \[37], Lima et al. \[17] y Powell et al. \[18]; sistemas tridimensionales sin marcadores de mayor complejidad, como los de Bae et al. \[24] y Noël et al. \[26]; y enfoques de clasificación basados en unidades de medición inercial o deep learning, como el de Sadeghi et al. \[25]. Esto refuerza la pertinencia de que la tesis delimite con claridad su apuesta tecnológica: una solución 2D, monocular, interpretable y viable dentro del alcance aprobado.

# 5. REVISIÓN DE LA LITERATURA ACTUAL O ESTADO DEL ARTE

El estado del arte de la presente investigación evidencia que la visión por computadora y la estimación de pose humana se han consolidado como líneas de trabajo relevantes para el análisis del movimiento en contextos de salud, deporte y rendimiento físico. La literatura reciente muestra una transición progresiva desde aplicaciones centradas en el reconocimiento general del cuerpo hacia sistemas capaces de cuantificar ejercicios, describir trayectorias segmentarias y apoyar procesos de evaluación funcional. En ese marco, Bazarevsky et al. \[27] presentan BlazePose como uno de los modelos de referencia para la estimación de pose en tiempo real, mientras que Stenum et al. \[28] documentan su expansión hacia contextos clínicos, de rehabilitación y de rendimiento humano. De forma complementaria, Rode et al. \[29] comparan distintos modelos monoculares para análisis clínico del movimiento y muestran que su desempeño depende de la tarea, del grado de auto-oclusión y de la profundidad espacial que se requiera representar. En conjunto, estos antecedentes permiten sostener que la estimación de pose bidimensional ha dejado de ser una técnica meramente experimental para convertirse en una alternativa con aplicación creciente en escenarios funcionales.

Sobre esa base, una parte importante de la literatura se ha orientado a validar sistemas de análisis del movimiento sin marcadores frente a referencias de mayor fidelidad, como la captura de movimiento con marcadores o los sistemas tridimensionales de laboratorio. En esta línea, Ota et al. \[14] constituyen uno de los antecedentes más cercanos a la presente tesis, pues validan un sistema de seguimiento de pose humana durante la sentadilla bilateral y lo comparan con VICON. De manera similar, Schmitz et al. \[38] presentan un antecedente fundacional al contrastar una sola cámara sin marcadores con un sistema basado en marcadores durante la ejecución de la sentadilla, y Pereira et al. \[16] proponen un procedimiento bidimensional para cuantificar la cinemática de los miembros inferiores durante la misma tarea. En una línea complementaria, Mercadal-Baudart et al. \[15] cuantifican ejercicios funcionales mediante una sola cámara y reportan errores mayores precisamente en algunas métricas de asimetría, mientras que Lopes et al. \[39] sintetizan que la validez del análisis bidimensional depende tanto de la tarea como del nivel de precisión exigido. En el extremo tecnológicamente más avanzado, Bae et al. \[24] validan un sistema tridimensional sin marcadores basado en deep learning durante la sentadilla por encima de la cabeza, lo que demuestra el potencial del campo cuando se dispone de infraestructura multicámara, aunque en un nivel de complejidad distinto al de una solución monocular accesible.

Paralelamente, el estado de la cuestión confirma que la sentadilla y sus variantes continúan siendo tareas biomecánicas de alto interés tanto para la evaluación como para la intervención. Straub y Powers \[4] explican que variables como la inclinación del tronco, la posición de la tibia, la profundidad, la separación de los pies y la orientación del apoyo modifican de forma importante la demanda mecánica del ejercicio. En el mismo sentido, Graber et al. \[5] muestran que la posición del tronco y de la pierna influye directamente en la relación de momentos entre cadera y rodilla durante la sentadilla bilateral profunda. Curnow et al. \[40], por su parte, incorporan una lectura clínica reciente de la sentadilla bilateral y de la sentadilla a una pierna (single-leg squat) en grupos con distintas condiciones de cadera. En conjunto, estos trabajos resultan relevantes porque desplazan la sentadilla desde una práctica general de entrenamiento hacia un problema biomecánico concreto, en el cual las relaciones entre tronco, pelvis y miembros inferiores adquieren valor analítico.

Dentro de esa misma literatura, una línea especialmente vinculada con la presente tesis se enfoca en compensaciones específicas y variables observables, sobre todo en torno al valgo dinámico y al control del tronco y la pelvis. Erdman et al. \[6] muestran que una evaluación bidimensional puede asociarse con contribuyentes biomecánicos tridimensionales del valgo dinámico en el plano coronal, mientras que Forman et al. \[7] discuten ese patrón dentro de movimientos basados en sentadilla. Por otra parte, Straub y Powers \[31] validan el uso de video bidimensional para medir el movimiento del tronco y la pelvis en el plano frontal, lo que resulta particularmente útil para sustentar compensaciones como la inclinación lateral del tronco y el desplazamiento lateral de la pelvis. En términos de asimetría bilateral, Liu et al. \[8] muestran que la carga asimétrica en la sentadilla con barra modifica los momentos articulares y la actividad muscular de los miembros inferiores, lo cual refuerza la importancia de considerar diferencias entre lados como parte del análisis funcional del movimiento.

Otra línea importante del estado del arte se orienta a la clasificación automática del movimiento y a la evaluación de la calidad de ejecución. Dajime et al. \[41] proponen un sistema de clasificación de la calidad del movimiento basado en variables cinemáticas obtenidas con Kinect y regresión logística multiclase, evidenciando que las variables biomecánicas pueden estructurarse como insumo para diferenciar patrones funcionales. En una línea más reciente, Kim y Park \[42] desarrollan un enfoque de machine learning interpretable para clasificar el desempeño en la sentadilla a una pierna a partir de variables de tronco, pelvis y rodilla, mientras que Shen et al. \[23] avanzan hacia una evaluación más automatizada mediante deep learning aplicada al tamizaje funcional del movimiento (functional movement screening). A su vez, Kianifar et al. \[43] y Sadeghi et al. \[25] representan antecedentes de clasificación automática de patrones de riesgo o errores de sentadilla a partir de unidades de medición inercial y modelos de mayor complejidad. En conjunto, estos estudios muestran que el campo no solo busca medir el movimiento, sino también transformar esa medición en una decisión automática. No obstante, en muchos casos la salida final continúa siendo global o poco explicable desde la biomecánica observacional.

El estado del arte reciente también confirma un crecimiento sostenido de soluciones de bajo costo para el análisis del movimiento sin marcadores y de plataformas accesibles fuera del laboratorio. Armitano-Lago et al. \[21] presentan un análisis SWOT de sistemas portables y de bajo costo, identificando fortalezas en accesibilidad y oportunidades de adopción, pero también debilidades asociadas a precisión, oclusión y protocolo. En la misma línea, Uhlrich et al. \[37], Lima et al. \[17] y Powell et al. \[18] muestran el potencial de OpenCap y de otras aproximaciones basadas en smartphones o captura asequible para aproximarse a mediciones biomecánicas útiles en tareas funcionales, incluyendo la sentadilla y la sentadilla bilateral. De manera complementaria, trabajos como los de Ino et al. \[34], Usami et al. \[35] y Ohmura et al. \[36] refuerzan la relevancia de la captura con una sola cámara o smartphone, mientras que Kim et al. \[32] y Noël et al. \[26] permiten comparar conceptualmente los alcances de los enfoques monoculares, multicámara y tridimensionales. Todo ello indica que el análisis del movimiento sin marcadores ya no constituye un escenario marginal, sino una línea técnicamente activa y en expansión.

Junto con los avances tecnológicos, la literatura también ha problematizado el papel de la observación experta y de la evaluación visual del movimiento. Falk et al. \[10] muestran limitaciones importantes en la precisión de las evaluaciones visuales de movimientos lumbopélvicos durante sentadilla y peso muerto. En la misma dirección, Gomes et al. \[11] cuestionan la validez de muchas escalas visuales utilizadas en clínica para la sentadilla a una pierna, Ressman et al. \[12] reportan valores de confiabilidad entre moderados y sustanciales en su revisión con meta-análisis, y Nutarelli et al. \[13] muestran que la evaluación en video grabado puede resultar más confiable que la observación en tiempo real. Estos hallazgos son especialmente relevantes para la tesis, pues sostienen que el criterio experto sigue siendo útil, pero requiere estructura, criterios definidos y, de ser posible, apoyo de revisión por video. A ello se añade el contexto aplicado del entrenamiento y la prevención: Bonilla et al. \[3], El-Kotob et al. \[1] y Serafim et al. \[2] ayudan a justificar que el entrenamiento de fuerza, aun cuando es beneficioso para la salud, exige mayor atención a la calidad de la ejecución y a la prevención de errores técnicos potencialmente asociados con lesión o sobreuso.

En términos generales, el estado de la cuestión muestra que el tema ya cuenta con bases sólidas en estimación de pose, análisis del movimiento sin marcadores, biomecánica de la sentadilla, evaluación funcional y clasificación automática del movimiento. No obstante, la revisión también permite reconocer vacíos relevantes para la presente tesis. En primer lugar, una parte considerable de los estudios se concentra en la sentadilla a una pierna, la sentadilla por encima de la cabeza, las tareas de salto o el análisis general de la calidad del movimiento, pero no en la sentadilla bilateral como foco principal. En segundo lugar, muchos trabajos validan ángulos, puntos anatómicos o cinemática global, pero no traducen esa información en compensaciones posturales específicas y asimetrías cinemáticas interpretables. En tercer lugar, los enfoques más automatizados tienden a priorizar salidas globales de clasificación o arquitecturas de deep learning de mayor complejidad, sin ofrecer siempre una relación clara entre la variable biomecánica observada y la decisión final. Finalmente, persiste la necesidad de articular sistemas accesibles con criterios de referencia basados en evaluación experta, en lugar de depender exclusivamente de laboratorios instrumentales o configuraciones multicámara avanzadas.

En consecuencia, la literatura revisada permite afirmar que existe una base científica suficiente para sustentar una propuesta basada en visión por computadora y estimación de pose 2D; sin embargo, también confirma la pertinencia del problema de investigación. Aún se observa espacio para una solución que combine cámara convencional, estimación de pose monocular, criterios biomecánicos interpretables y evaluación del desempeño técnico frente a una referencia experta, específicamente orientada a la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral. Ese vacío constituye, precisamente, el punto de entrada que define la contribución de la presente tesis.

De manera explícita, el vacío de investigación que aborda esta tesis consiste en que la literatura revisada no ofrece, para el caso específico de la sentadilla bilateral evaluada con cámara convencional y estimación de pose 2D, una propuesta centrada en detectar compensaciones posturales y asimetrías cinemáticas mediante criterios biomecánicos interpretables y con evaluación del desempeño frente a una referencia experta estructurada. Aunque existen estudios de validación sin marcadores, clasificación automática del movimiento y análisis funcional de tareas relacionadas, persiste la necesidad de una solución accesible, monocular y explicable orientada específicamente a ese problema, lo cual justifica de forma directa la realización del presente estudio.

# 6. MARCO TEÓRICO

El marco teórico del presente estudio se organizará directamente a partir de las dos variables definidas en la matriz de operacionalización. Esta decisión permite que cada dimensión y cada indicador conserve coherencia con los instrumentos que posteriormente se emplearán en la metodología. Bajo este criterio, la exposición desarrolla la definición conceptual de las variables, la definición teórica de cada dimensión y la conceptualización específica de cada indicador con respaldo bibliográfico.

## Variable 1: Sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables.

Definición conceptual. La primera variable corresponde al sistema computacional que procesa videos de sentadilla bilateral para estimar la postura corporal, extraer información geométrica del cuerpo, calcular variables biomecánicas observables y aplicar reglas interpretables orientadas a la detección de compensaciones posturales y asimetrías cinemáticas. Conceptualmente, esta variable se apoya en la visión por computadora como campo capaz de transformar imágenes y videos en información estructurada, y en la estimación de pose humana como técnica que permite representar el cuerpo mediante puntos anatómicos clave del cuerpo (landmarks) en contextos funcionales, como señalan Bazarevsky et al. \[27], Stenum et al. \[28] y Rode et al. \[29]. En el ámbito del análisis del movimiento, distintos trabajos muestran que estas herramientas ya poseen utilidad técnica en tareas deportivas y clínicas cuando se delimitan adecuadamente sus condiciones de captura y su propósito analítico, como se observa en Ota et al. \[14], Lima et al. \[17] y Kanko et al. \[19].

Dimensión 1: estimación de pose 2D. Esta dimensión representa la capacidad del sistema para detectar y seguir puntos anatómicos clave corporales en un plano bidimensional a partir de una sola cámara convencional. Su relevancia teórica proviene de que la estimación de pose 2D constituye la base computacional sobre la cual se construyen las mediciones posteriores del sistema, especialmente en escenarios donde se prioriza accesibilidad y viabilidad frente a esquemas multicámara más complejos, como plantean Bazarevsky et al. \[27], Rode et al. \[29] y Lopes et al. \[39]. Diversos antecedentes muestran que el rendimiento de esta dimensión depende de variables como el protocolo de captura, la oclusión, la calidad visual y la tarea motriz observada, tal como discuten Kim et al. \[32], Ohmura et al. \[36] y Needham et al. \[45].

- Indicador 1.1: promedio de puntos anatómicos clave detectados por fotograma. Este indicador expresa la cobertura media de las referencias corporales seleccionadas durante el procesamiento del video. Para cada fotograma se contabilizan los puntos cuya visibilidad alcanza el umbral mínimo establecido y, posteriormente, se obtiene la media aritmética de todos los fotogramas procesados. En el sistema propuesto se consideran 13 puntos: nariz y referencias bilaterales de hombros, caderas, rodillas, tobillos, talones y puntas de los pies. Su valor se expresa como cantidad promedio de puntos detectados por fotograma, respecto de un máximo de 13. Este indicador permite describir la estabilidad general de la estimación de pose, en concordancia con lo desarrollado por Bazarevsky et al. \[27] y Rode et al. \[29]. El indicador puede expresarse como  = (1 / N) × Σ , donde N representa el número de fotogramas procesados y la cantidad de los 13 puntos seleccionados cuya visibilidad es igual o superior a 0,5 en el fotograma f. La selección de los 13 puntos y el umbral de 0,5 corresponden a decisiones operativas del sistema propuesto y no constituyen valores clínicos universales El promedio de puntos detectados describe la cobertura de la estimación de pose, pero no determina por sí solo la validez analítica del fotograma. Esta depende de la disponibilidad de ambos hombros, caderas, rodillas y tobillos, además de al menos una referencia distal por cada pie, que puede ser el talón o la punta del pie.

- Indicador 1.2: porcentaje de fotogramas válidos. Este indicador se define como la proporción de fotogramas del video que contienen detección suficiente de puntos anatómicos clave para sostener el análisis biomecánico. Su formulación conceptual es distinta al procesamiento correcto, porque se concentra en la calidad analítica de los fotogramas y no en el éxito general del flujo computacional. Puede expresarse como: fotogramas válidos / total de fotogramas analizados x 100. La literatura sobre análisis del movimiento sin marcadores muestra que la validez de un registro depende de conservar secuencias suficientemente estables para evitar errores por oclusión, desenfoque o pérdida de referencias corporales, como reportan Lopes et al. \[39], Ohmura et al. \[36] y Needham et al. \[45].

- Indicador 1.3: porcentaje de fotogramas procesados correctamente. Este indicador representa la proporción de fotogramas que logran completar satisfactoriamente el flujo técnico del sistema, desde la lectura del video hasta la obtención de salida estructurada. A diferencia del porcentaje de fotogramas válidos, aquí el énfasis está en el desempeño funcional del flujo computacional y no exclusivamente en la utilidad biomecánica del fotograma. Puede formularse como: fotogramas procesados sin error / total de fotogramas leídos x 100. Su uso resulta coherente con enfoques de validación técnica de sistemas sin marcadores, donde la estabilidad del procesamiento es parte del desempeño global del sistema, como muestran Ota et al. \[14], Lima et al. \[17] y Kanko et al. \[19].

Dimensión 2: extracción y cálculo de variables biomecánicas observables. Esta dimensión alude a la transformación de puntos anatómicos clave 2D en medidas geométricas o cinemáticas que representen patrones observables del movimiento. Teóricamente, su importancia radica en que la visión por computadora por sí sola no genera interpretación biomecánica; esta surge cuando las coordenadas corporales se convierten en variables funcionalmente significativas para la tarea analizada, como sostienen Straub y Powers \[31], Straub y Powers \[4] y Graber et al. \[5]. En estudios recientes, el uso de una sola cámara ha permitido cuantificar ejercicios funcionales y representar variables de tronco, pelvis y miembros inferiores con distintos niveles de precisión, aunque con mayores retos en métricas ligadas a asimetría, como se observa en Mercadal-Baudart et al. \[15], Pereira et al. \[16] y Lopes et al. \[39].

- Indicador 2.1: inclinación del tronco. Este indicador representa la desviación angular o relativa del eje troncal respecto a una referencia vertical o respecto al plano de observación. Su fundamentación teórica deriva de la literatura que reconoce al tronco como uno de los segmentos más sensibles para evaluar estrategias compensatorias durante la sentadilla bilateral, como exponen Straub y Powers \[31], Straub y Powers \[4] y Graber et al. \[5]. En términos conceptuales, puede definirse mediante la relación geométrica entre hombros, pelvis y eje vertical, y su valor puede expresarse en grados o en una razón normalizada.

- Indicador 2.2: desplazamiento lateral de pelvis. Este indicador expresa la desviación horizontal del centro pélvico o del punto medio entre caderas durante la ejecución del gesto. Su interés biomecánico radica en que el control frontal de pelvis se asocia con estabilidad y distribución del movimiento entre ambos lados del cuerpo, como se aprecia en Straub y Powers \[31] y Erdman et al. \[6]. Conceptualmente, puede estimarse como el desplazamiento relativo del punto medio pélvico respecto a una línea de referencia corporal o respecto a la posición inicial del movimiento.

- Indicador 2.3: alineación rodilla-cadera-tobillo. Este indicador representa la relación espacial observable entre cadera, rodilla y tobillo en el plano frontal, especialmente útil para reconocer colapso medial o alineaciones alteradas durante el gesto. Su fundamento teórico se conecta con la evaluación del valgo dinámico y con la utilidad del video bidimensional para representar relaciones angulares o de proyección entre segmentos del miembro inferior, como muestran Erdman et al. \[6], Forman et al. \[7] y Kianifar et al. \[43]. En términos conceptuales, puede formularse como ángulo, distancia relativa o criterio de alineación observacional.

- Indicador 2.4: diferencias bilaterales. Este indicador representa la diferencia relativa entre lado derecho e izquierdo en variables equivalentes del movimiento. Teóricamente, sirve como aproximación a la asimetría cinemática y se justifica porque una parte de la literatura reporta que las mediciones sin marcadores pueden capturar diferencias laterales, aunque con sensibilidad variable según la tarea y el tipo de medida, como indican Mercadal-Baudart et al. \[15] y Liu et al. \[8]. Conceptualmente, puede expresarse como diferencia absoluta, diferencia porcentual o valor normalizado entre lados.

Dimensión 3: aplicación de criterios biomecánicos interpretables. Esta dimensión se refiere al conjunto de reglas explícitas mediante las cuales el sistema traduce variables geométricas en patrones comprensibles de compensación o asimetría. Su importancia teórica radica en que la presente tesis no propone una salida de caja negra, sino una lógica de decisión explicable basada en relaciones visibles del movimiento. Este enfoque se distingue de las arquitecturas de clasificación puramente automáticas y se aproxima más a estrategias interpretables o híbridas, en las que la salida puede justificarse a partir de variables identificables, como se advierte en Kim y Park \[42], Shen et al. \[23] y Hofer et al. \[30].

- Indicador 3.1: número de criterios implementados. Este indicador expresa la cantidad de reglas biomecánicas explícitas que el sistema incorpora para clasificar compensaciones o asimetrías. Su sentido conceptual no es solo cuantitativo, sino estructural, pues refleja el nivel de formalización de la lógica interpretativa del sistema. En términos prácticos, puede registrarse como conteo absoluto de criterios aplicados en el prototipo.

- Indicador 3.2: tipo de compensación detectada. Este indicador representa la clase de hallazgo que el sistema es capaz de emitir a partir de sus reglas, por ejemplo inclinación lateral del tronco, desplazamiento lateral de pelvis o valgo dinámico visible. Conceptualmente, su función es vincular la lógica del sistema con categorías biomecánicas comprensibles para la evaluación funcional Erdman et al. \[6] y Forman et al. \[7]. Se expresa en escala nominal, pues su objetivo es clasificar el tipo de patrón observado.

- Indicador 3.3: umbrales definidos. Este indicador se refiere a los valores de decisión o condiciones geométricas que activan una clasificación dentro del sistema. Su relevancia teórica proviene de que un criterio interpretable requiere no solo variables, sino también límites o relaciones explícitas para evitar arbitrariedad analítica. Puede registrarse como número de umbrales implementados, rango definido o criterio lógico asociado a cada compensación.

Dimensión 4: procesamiento y generación de resultados. Esta dimensión corresponde a la capacidad del prototipo para ejecutar de manera integrada la carga del video, el procesamiento de la información, la aplicación de criterios y la entrega de una salida utilizable. Su fundamento teórico se vincula con la concepción de la variable como un sistema funcional y no solo como un conjunto aislado de cálculos. En investigaciones aplicadas de visión por computadora orientadas al movimiento, la utilidad técnica depende también de que el flujo completo pueda operar de forma estable, reproducible y trazable Ota et al. \[14], Uhlrich et al. \[37] y Lima et al. \[17].

- Indicador 4.1: carga de video. Este indicador expresa la capacidad del prototipo para recibir y abrir correctamente un archivo audiovisual compatible con el análisis. Conceptualmente, representa la puerta de entrada del sistema y puede expresarse en formato binario de cumplimiento o no cumplimiento.

- Indicador 4.2: procesamiento completo. Este indicador se refiere a la capacidad del sistema para completar de inicio a fin las etapas previstas del análisis sin interrupciones críticas. Se diferencia del procesamiento correcto por fotograma porque aquí la unidad es el caso o video completo. Puede expresarse como cumple / no cumple o como porcentaje de casos completados.

- Indicador 4.3: generación de reporte. Este indicador representa la capacidad del sistema para producir una salida estructurada con variables calculadas y hallazgos detectados. Teóricamente, este aspecto es clave porque la utilidad de un sistema interpretable depende de que los resultados puedan conservarse, revisarse y compararse con la referencia experta. Su medición puede plantearse de manera nominal o binaria.

- Indicador 4.4: visualización de resultados. Este indicador alude a la presentación comprensible de los hallazgos emitidos por el sistema, ya sea en forma textual, tabular o gráfica. Conceptualmente, se vincula con la trazabilidad y comunicabilidad del resultado final, y puede evaluarse como presencia o ausencia de la salida visual prevista.

## Variable 2: Desempeño técnico del sistema en la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral.

Definición conceptual. La segunda variable corresponde al rendimiento del sistema en la identificación de patrones observables del movimiento durante la sentadilla bilateral, evaluado mediante comparación con una referencia basada en evaluación experta. Su definición conceptual se vincula con la literatura sobre validez, confiabilidad y utilidad de sistemas de análisis del movimiento, así como con los estudios que comparan soluciones automáticas o semiautomáticas frente a juicio experto o frente a referencias biomecánicas de mayor fidelidad, como se observa en Ota et al. \[14], Kim y Park \[42], Bae et al. \[24] y Ressman et al. \[12]. Esta variable no describe simplemente la existencia del sistema, sino la calidad con la que dicho sistema detecta compensaciones y asimetrías de forma consistente.

Dimensión 1: detección de compensaciones posturales. Esta dimensión expresa la capacidad del sistema para identificar patrones observables de compensación durante la sentadilla bilateral. Su fundamento teórico se encuentra en la biomecánica del ejercicio y en la evaluación funcional del plano frontal, donde el tronco, la pelvis y la alineación de rodilla constituyen referencias de alta relevancia para reconocer estrategias compensatorias, como describen Straub y Powers \[31], Straub y Powers \[4], Graber et al. \[5] y Erdman et al. \[6]. La literatura sobre revisión por video y observación estructurada también refuerza la pertinencia de estas categorías cuando se delimitan de forma explícita, como muestran Falk et al. \[10], Gomes et al. \[11] y Nutarelli et al. \[13].

- Indicador 1.1: inclinación lateral del tronco. En esta variable, el indicador representa la capacidad del sistema para clasificar correctamente la presencia, ausencia o lateralidad de la inclinación troncal durante el gesto. Teóricamente, este patrón se considera una compensación relevante porque modifica la organización segmentaria del movimiento y puede reflejar estrategias de descarga o control insuficiente Straub y Powers \[4] y Graber et al. \[5]. Su registro se plantea en escala nominal u ordinal según la clasificación adoptada.

- Indicador 1.2: desplazamiento lateral de pelvis. Este indicador expresa la capacidad del sistema para reconocer desviaciones laterales pélvicas durante la ejecución de la sentadilla. Su importancia conceptual deriva de la relación entre control frontal de pelvis, estabilidad y distribución del movimiento entre miembros inferiores Straub y Powers \[31] y Erdman et al. \[6]. Se registra como categoría de presencia, lateralidad o ausencia del patrón.

- Indicador 1.3: valgo dinámico visible. Este indicador representa la capacidad del sistema para detectar colapso medial visible de rodilla o aproximación alterada de la rodilla hacia la línea media en relación con cadera y tobillo. La literatura lo considera uno de los patrones observacionales más estudiados en tareas basadas en sentadilla Erdman et al. \[6], Forman et al. \[7] y Kianifar et al. \[43]. Su expresión es categórica, ya sea por lado, bilateralidad o ausencia.

Dimensión 2: detección de asimetrías cinemáticas. Esta dimensión alude a la capacidad del sistema para reconocer diferencias observables entre lado derecho e izquierdo durante la ejecución del movimiento. Su fundamento teórico se apoya en la noción de asimetría cinemática como diferencia en alineación, desplazamiento o trayectoria entre segmentos homólogos, relevante para el análisis funcional de tareas bilaterales, como sugieren Mercadal-Baudart et al. \[15] y Liu et al. \[8]. En sistemas accesibles, esta dimensión requiere especial cuidado conceptual porque no toda diferencia lateral constituye por sí sola una alteración clínicamente significativa; por ello, la tesis la aborda como asimetría observable y no como diagnóstico.

- Indicador 2.1: diferencia entre lado derecho e izquierdo en alineación corporal. Este indicador representa la capacidad del sistema para reconocer desigualdad lateral en la organización corporal visible entre ambos hemicuerpos. Conceptualmente, se apoya en el análisis comparativo de relaciones segmentarias equivalentes entre lados y puede expresarse como diferencia angular, categorización de presencia o índice relativo.

- Indicador 2.2: diferencia entre lados en desplazamiento. Este indicador se refiere a la capacidad del sistema para identificar diferencias laterales en magnitud o dirección de desplazamiento de segmentos o puntos corporales relevantes. Su fundamento teórico deriva de la comparación bilateral como recurso para estimar desbalance motor observable \[15]. Puede expresarse como diferencia absoluta, diferencia porcentual o clasificación de asimetría presente/ausente.

- Indicador 2.3: diferencia entre lados en trayectoria relativa. Este indicador representa la capacidad del sistema para reconocer que ambos lados no siguen un comportamiento cinemático equivalente durante descenso o ascenso. Conceptualmente, incorpora la dimensión dinámica de la asimetría, más allá de una sola postura instantánea. Su medición puede definirse como diferencia relativa entre series o como clasificación nominal de asimetría de trayectoria.

Dimensión 3: desempeño técnico de la detección. Esta dimensión representa la calidad global de la salida del sistema cuando se la compara con una referencia experta estructurada. Teóricamente, se apoya en los marcos de evaluación de sistemas de clasificación y en la literatura de confiabilidad observacional, donde no basta con detectar patrones, sino que se requiere valorar qué tan correctamente y qué tan consistentemente se detectan, como se discute en Kim y Park \[42], Bae et al. \[24], Ressman et al. \[12], Whatman et al. \[44] y Nutarelli et al. \[13]. Esta dimensión es la que conecta directamente la variable con la matriz de validación y con el análisis de datos previsto en la metodología.

- Indicador 3.1: exactitud. Este indicador representa la proporción total de clasificaciones correctas del sistema respecto del total de casos evaluados. Conceptualmente, ofrece una visión global del acierto del modelo, aunque no distingue por sí sola entre clases frecuentes o infrecuentes. Puede expresarse como: clasificaciones correctas / total de casos x 100.

- Indicador 3.2: precisión. Este indicador expresa la proporción de casos identificados por el sistema como positivos que realmente corresponden a la categoría de referencia. Su utilidad teórica radica en valorar cuántos hallazgos emitidos por el sistema son efectivamente correctos. Puede formularse como: verdaderos positivos / (verdaderos positivos + falsos positivos).

- Indicador 3.3: sensibilidad. Este indicador representa la capacidad del sistema para detectar correctamente los casos positivos existentes en la referencia. En términos conceptuales, permite valorar el nivel de recuperación de compensaciones o asimetrías realmente presentes. Puede formularse como: verdaderos positivos / (verdaderos positivos + falsos negativos).

- Indicador 3.4: especificidad. Este indicador expresa la capacidad del sistema para reconocer correctamente los casos negativos, es decir, aquellos en los que el patrón no está presente. Su valor teórico radica en evitar la sobredetección de compensaciones o asimetrías. Puede formularse como: verdaderos negativos / (verdaderos negativos + falsos positivos).

- Indicador 3.5: puntaje F1 (F1-score). Este indicador integra precisión y sensibilidad en una sola medida armónica, útil cuando interesa equilibrar falsos positivos y falsos negativos en problemas de clasificación. Su empleo se encuentra ampliamente extendido en sistemas de evaluación automática del movimiento Kim y Park \[42] y Bae et al. \[24]. Conceptualmente, puede expresarse como: F1 = 2 x (precisión x sensibilidad) / (precisión + sensibilidad).

- Indicador 3.6: índice Kappa. Este indicador representa el grado de concordancia más allá del azar entre clasificaciones del sistema y referencia humana, o entre evaluadores cuando se analiza consistencia del criterio experto. Su fundamento conceptual se apoya en estudios de confiabilidad observacional que advierten la necesidad de no depender únicamente de porcentajes simples de coincidencia Ressman et al. \[12], Whatman et al. \[44] y Nutarelli et al. \[13]. En esta tesis se prevé principalmente Kappa de Cohen, y Kappa de Fleiss si se incorpora un tercer evaluador. De forma conceptual, el índice puede expresarse como: kappa = (Po - Pe) / (1 - Pe), donde Po es la proporción de acuerdo observado y Pe es la proporción de acuerdo esperada por azar.

# 7. HIPÓTESIS

## 7.1 Hipótesis general

El sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables permite detectar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral con niveles adecuados de desempeño técnico frente a un criterio de referencia basado en evaluación experta en Lima Sur, 2026.

## 7.2 Hipótesis específicas

- a. La identificación de puntos anatómicos clave corporales 2D permite representar segmentos corporales relevantes para el análisis biomecánico observable de la sentadilla bilateral.
- b. Las variables biomecánicas calculadas a partir de puntos anatómicos clave corporales 2D permiten caracterizar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral.
- c. Los criterios biomecánicos interpretables permiten clasificar patrones posturales específicos como inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y asimetría bilateral general.
- d. El prototipo funcional permite procesar videos de sentadilla bilateral y generar resultados interpretables sobre la ejecución del movimiento.
- e. El sistema propuesto presenta niveles adecuados de desempeño técnico en la detección de compensaciones posturales y asimetrías cinemáticas frente a un criterio de referencia basado en evaluación experta.

# 8. METODOLOGÍA

## 8.1 Tipo y diseño

La investigación será de enfoque cuantitativo y de tipo aplicada. Se adopta el enfoque cuantitativo porque se trabajará con variables observables derivadas de la estimación de pose 2D, se calcularán medidas geométricas y biomecánicas obtenidas a partir de videos de sentadilla bilateral y se evaluará el desempeño técnico del sistema mediante métricas numéricas de clasificación y concordancia. Será de tipo aplicada porque busca desarrollar una solución tecnológica orientada a un problema concreto: la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral.

En cuanto al alcance, la investigación será descriptivo-propositiva. Será descriptiva porque identificará y organizará variables biomecánicas observables, patrones posturales y criterios de decisión asociados a la ejecución del ejercicio. Será propositiva porque, a partir de esa base, diseñará e implementará un sistema funcional capaz de detectar dichos patrones de manera estructurada e interpretable. El diseño será no experimental, transversal y tecnológico-evaluativo. Será no experimental porque no se manipularán deliberadamente las condiciones corporales de las personas registradas; transversal porque los videos se recopilarán y analizarán dentro de un periodo específico; y tecnológico-evaluativo porque culminará con el diseño, implementación, uso y evaluación técnica del prototipo funcional frente a una referencia basada en evaluación experta. Esta elección metodológica es congruente con estudios como Ota et al. \[14], Dajime et al. \[41], Bae et al. \[24], Uhlrich et al. \[37] y Lima et al. \[17].

## 8.2 Población

La población del estudio estará conformada por videos de personas ejecutando sentadillas bilaterales, capturados mediante cámara convencional bajo condiciones definidas de registro. La unidad de análisis principal será el video procesable que contenga una ejecución observable del ejercicio y que permita extraer puntos anatómicos clave del cuerpo (landmarks), calcular variables biomecánicas y comparar los resultados del sistema con una referencia experta.

Como criterios de inclusión se considerarán videos de personas adultas capaces de ejecutar sentadillas bilaterales completas o suficientemente observables para identificar las fases de descenso y ascenso, con visibilidad del cuerpo completo o de los segmentos necesarios para el análisis del tronco, pelvis y miembros inferiores, capturados con cámara convencional en vista anterior dentro del plano frontal y con calidad visual suficiente para la detección estable de pose. La ejecución deberá realizarse sin carga externa, sobre una superficie plana, sin discos, cuñas u otros soportes colocados debajo de los talones y procurando mantener ambos talones en contacto con el suelo durante el movimiento. Como criterios de exclusión se contemplarán videos con oclusión significativa, iluminación deficiente, desenfoque excesivo, movimientos incompletos, registros fuera del plano frontal, carga externa, implementos que oculten segmentos relevantes, uso de soportes elevados debajo de los talones, elevación evidente o sostenida de estos o casos en los que el modelo de pose no detecte adecuadamente los puntos anatómicos requeridos. Una elevación breve y espontánea del talón será registrada como observación técnica y motivará la repetición del intento antes de determinar la exclusión del registro. Esta delimitación se apoya en Bae et al. \[24], Armitano-Lago et al. \[21], Ohmura et al. \[36] y Needham et al. \[45].

La exclusión por soportes externos o elevación evidente y sostenida de los talones será determinada manualmente por el investigador a partir del protocolo de captura y del Instrumento 1. No deberá describirse como una detección o decisión automática del sistema.

## 8.3 Muestra

La muestra estará constituida por 75 videos válidos de sentadilla bilateral. Se considerarán 15 videos positivos para cada uno de los cuatro patrones evaluados en el estudio —inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y asimetría bilateral observable— y 15 videos negativos en los que no se detecte ninguna compensación observable. Esta distribución permitirá asegurar la presencia de casos representativos para cada patrón y, al mismo tiempo, incorporar registros de contraste sin hallazgos. La unidad de análisis de la muestra será un video válido por caso, correspondiente a una ejecución de sentadilla bilateral, capturada en vista anterior dentro del plano frontal, que pueda ser procesada de manera completa por el sistema y revisada por los evaluadores expertos.

Dado que la población operativa del estudio está formada por registros audiovisuales seleccionados bajo criterios técnicos y no por una población estadística plenamente enumerada, no se plantea en esta etapa un cálculo muestral probabilístico clásico. En su lugar, se adopta un tamaño de muestra metodológicamente manejable y suficiente para sustentar pruebas de funcionamiento, detección y concordancia, sin perder coherencia con el alcance de la tesis.

## 8.4 Muestreo

El muestreo será no probabilístico e intencional. Esta estrategia se elige porque la selección de cada video dependerá del cumplimiento de condiciones específicas de calidad, visibilidad corporal, vista anterior dentro del plano frontal, ausencia de carga externa, ejecución sin soportes elevados debajo de los talones, apoyo plantar observable y posibilidad de estimación estable de pose. La verificación de las condiciones relacionadas con el apoyo de los talones será realizada manualmente por el investigador mediante el protocolo de captura y el Instrumento 1, y no constituirá una función automática del sistema. En este estudio, la prioridad no será la representatividad estadística poblacional en sentido estricto, sino la disponibilidad de registros válidos para diseñar, probar y evaluar el sistema propuesto.

La literatura metodológica del campo muestra que la calidad del protocolo de captura incide directamente sobre la validez del análisis del movimiento sin marcadores. Por ello, la elección de un muestreo intencional es coherente con antecedentes como Lopes et al. \[39], Kim et al. \[32], Ohmura et al. \[36] y Needham et al. \[45].

## 8.5 Técnicas e instrumentos

La técnica principal de recolección de datos será el análisis estructurado de video, complementado por registro técnico del procesamiento computacional y evaluación observacional experta. En coherencia con la matriz de operacionalización, los instrumentos se han reorganizado para que cada uno mida dimensiones e indicadores concretos del estudio, evitando presentar anexos como referencias conceptuales aisladas.

El primer instrumento será una ficha maestra de registro técnico, factibilidad analítica y disponibilidad de puntos anatómicos clave. Esta ficha integrará, en una sola hoja de trabajo, la identificación del video, fecha de registro, fuente, condiciones de captura, resolución, iluminación, visibilidad corporal, presencia de oclusiones, cumplimiento de la vista anterior dentro del plano frontal, validez del registro para procesamiento y disponibilidad observable de los puntos anatómicos clave relevantes. También permitirá registrar manualmente las condiciones de ejecución que puedan comprometer la comparabilidad del análisis, como el uso de discos, cuñas u otros soportes debajo de los talones, la elevación evidente o sostenida de estos y la pérdida de visibilidad de los segmentos corporales requeridos.

Para que un registro sea aceptado, la sentadilla deberá ejecutarse sobre una superficie plana, sin soportes externos debajo de los talones y procurando mantener el contacto de ambos talones con el suelo. Cuando el investigador identifique la presencia de soportes externos o una elevación evidente y sostenida de los talones, se solicitará repetir la grabación; si ello no fuera posible, el registro no será incorporado a la muestra analítica principal. De igual manera, los videos capturados fuera del plano frontal, que presenten baja calidad visual o que incumplan otras condiciones críticas del protocolo serán considerados no aptos para el análisis. Estas verificaciones serán realizadas mediante el protocolo de captura y el Instrumento 1, y no constituirán funcionalidades automáticas del sistema. De esta manera, se busca reducir la ambigüedad en la selección de casos y fortalecer la trazabilidad metodológica del proceso de inclusión y exclusión.

El segundo instrumento será una ficha de procesamiento computacional, variables biomecánicas y criterios interpretables. Esta ficha registrará, para cada video aceptado, el estado del procesamiento, cantidad de fotogramas, fotogramas válidos, porcentaje de fotogramas procesados correctamente, promedio de puntos anatómicos clave detectados por fotograma, valores de las variables biomecánicas observables y salidas interpretativas emitidas por el sistema. Para este indicador se considerarán 13 puntos seleccionados: nariz y referencias bilaterales de hombros, caderas, rodillas, tobillos, talones y puntas de los pies. Un punto será contabilizado como detectado cuando alcance una visibilidad igual o superior a 0,5; el resultado resumido corresponderá al promedio obtenido en todos los fotogramas procesados y se expresará como puntos detectados de un total de 13. Cada patrón será evaluado mediante un criterio independiente, por lo que un mismo video podrá presentar ninguna, una o varias compensaciones o asimetrías de manera simultánea. Cuando la evidencia obtenida sea insuficiente o se encuentre dentro de un margen de decisión ambiguo, se registrará que no fue posible establecer una clasificación definitiva para el patrón correspondiente. De esta forma, el instrumento permitirá conservar la relación entre el valor calculado, el criterio aplicado y el resultado interpretativo obtenido.

El tercer instrumento será una ficha comparativa de evaluación experta y sistema. En ella se registrará, por cada video, la clasificación emitida por dos evaluadores expertos y por el sistema computacional respecto de inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y asimetría bilateral observable. Estos patrones serán valorados de manera independiente, de modo que la identificación de uno no excluirá la presencia simultánea de otros. Por ejemplo, un mismo video podrá presentar desplazamiento lateral de pelvis, valgo dinámico visible y asimetría bilateral. Si durante el desarrollo del estudio se incorpora un tercer evaluador, la misma estructura permitirá integrar su valoración para fortalecer la referencia final.

De manera complementaria, los instrumentos serán sometidos a validación por dos o tres expertos vinculados con visión por computadora, ingeniería aplicada o análisis del movimiento, utilizando la ficha institucional de validación por juicio de expertos proporcionada por la universidad. Esta validación revisará claridad, pertinencia, coherencia con dimensiones e indicadores y suficiencia de las cabeceras planteadas. El producto esperado será la aprobación formal de los instrumentos antes de su uso definitivo, con observaciones y firma de los expertos validadores. Su función no será registrar videos ni clasificaciones del movimiento, sino asegurar previamente la calidad metodológica de las fichas que serán aplicadas en el estudio.

Como parte del análisis de datos, el investigador construirá una base consolidada interna derivada de la información registrada en el Instrumento 3. Esta base se utilizará exclusivamente para comparar la referencia experta final con la salida del sistema, dejando trazabilidad de coincidencias, discrepancias y observaciones analíticas, sin considerarse un instrumento adicional de recolección de datos. Debido a que un mismo video puede presentar más de un patrón, cada patrón evaluado dentro de cada video constituirá un registro independiente para el análisis. Esta organización permitirá calcular métricas de desempeño específicas para tronco, pelvis, valgo y asimetría bilateral, evitando que el acierto en una categoría compense una clasificación incorrecta en otra.

La referencia experta se construirá inicialmente con dos evaluadores con perfil de entrenador con experiencia en análisis del movimiento. Cada uno revisará de manera independiente los videos mediante la ficha comparativa y, cuando corresponda, se establecerá una referencia final por coincidencia directa, consenso o criterio de mayoría si se incorpora un tercer evaluador. Este procedimiento es consistente con Falk et al. \[10], Gomes et al. \[11], Ressman et al. \[12], Whatman et al. \[44] y Nutarelli et al. \[13], quienes muestran que la observación humana mejora cuando se apoya en criterios definidos y revisión audiovisual estructurada.

Desde el punto de vista procedimental, el Instrumento 1 operará durante la selección y aceptación de videos; el Instrumento 2 durante la ejecución y registro del sistema; y el Instrumento 3 durante la evaluación comparativa entre expertos y software. La ficha institucional de validación por juicio de expertos operará antes de la aplicación definitiva, como mecanismo de aseguramiento metodológico externo. Posteriormente, el investigador integrará la información resultante en una base consolidada interna para la fase de análisis y cálculo de métricas. Esta organización vincula de manera directa los instrumentos con las dimensiones del estudio y responde a la necesidad de que los anexos metodológicos funcionen realmente como herramientas de medición.

## 8.6 Análisis de datos

El análisis de datos combinará técnicas descriptivas con métricas de evaluación del desempeño del sistema. Para ello, se construirá primero una base consolidada a partir de los instrumentos aplicados. Del Instrumento 1 se obtendrá la caracterización técnica de los videos y la trazabilidad de inclusión o exclusión de registros; del Instrumento 2 se obtendrá la información de procesamiento, cobertura de puntos anatómicos clave y variables biomecánicas calculadas; y del Instrumento 3 se obtendrá la comparación entre expertos y sistema para cada patrón analizado. Esta integración permitirá construir una matriz final de análisis por video y por criterio evaluado.

En una primera etapa se realizará un análisis descriptivo de la base de videos, considerando cantidad de registros aceptados, registros descartados, motivos de exclusión, condiciones de captura, disponibilidad de puntos anatómicos clave y frecuencia de procesamiento exitoso. En una segunda etapa se resumirá el comportamiento técnico del sistema mediante indicadores como porcentaje de fotogramas válidos, porcentaje de fotogramas procesados correctamente, promedio de puntos anatómicos clave detectados por fotograma y distribución de las salidas interpretativas emitidas por el prototipo. El promedio de puntos detectados se calculará sobre los 13 puntos seleccionados para el análisis y sobre la totalidad de los fotogramas procesados.

En una tercera etapa se analizarán descriptivamente las variables biomecánicas observables obtenidas por el sistema, utilizando medidas como promedio, máximo, mínimo, rango y desviación estándar, cuando la naturaleza del dato lo permita. Cuando dichas variables sean transformadas en categorías interpretables para la detección de compensaciones o asimetrías, se calcularán también las frecuencias de cada categoría emitida.

En una cuarta etapa se establecerá la referencia final experta. Cuando los dos evaluadores coincidan, esa clasificación se asumirá como referencia directa; cuando discrepen, se utilizará revisión por consenso y, si se incorpora un tercer evaluador, podrá utilizarse criterio de mayoría. Una vez consolidada esta referencia, la información se integrará en una base de análisis construida por el investigador, desde la cual se elaborarán matrices de confusión para comparar la salida del sistema con la referencia humana estructurada.

A partir de dichas matrices se calcularán métricas de desempeño como exactitud, precisión, sensibilidad, especificidad y puntaje F1 (F1-score). Asimismo, se estimará la concordancia entre evaluadores mediante índice Kappa de Cohen, y si participa un tercer evaluador podrá incorporarse Kappa de Fleiss. Los casos no concluyentes o con evidencia insuficiente se registrarán explícitamente para no distorsionar la interpretación del desempeño. Este esquema es coherente con Kim y Park \[42], Bae et al. \[24], Ressman et al. \[12], Whatman et al. \[44] y Nutarelli et al. \[13].

## 8.7 Aspectos éticos

Previamente al inicio del recojo de datos, se gestionará la obtención del dictamen favorable del Comité de Ética en Investigación (CEI) de la Universidad Tecnológica del Perú (UTP), conforme a los lineamientos institucionales. Una vez obtenido dicho dictamen, se procederá a solicitar la autorización correspondiente al gimnasio comercial ubicado en Lima Sur donde se llevará a cabo la grabación de los videos. Esta autorización será gestionada de manera presencial con el administrador o responsable del establecimiento, y se formalizará mediante un documento escrito que acredite el consentimiento para el uso de sus instalaciones. Recién después de contar con ambas autorizaciones —la del CEI-UTP y la del establecimiento— se dará inicio al proceso de captura de videos y recojo de datos para la ejecución del estudio.

La investigación se desarrollará respetando los principios éticos aplicables al uso de videos y datos personales. Si se utilizan registros capturados específicamente para la tesis, se solicitará consentimiento informado a las personas participantes, explicando el propósito académico del estudio, el tratamiento de los datos y el alcance no clínico del sistema. Se resguardará la identidad de los participantes mediante codificación o anonimización, y los videos no serán utilizados con fines distintos a los establecidos en la investigación.

Como medida adicional de resguardo, el sistema podrá incorporar una función de anonimización visual para pixelear o difuminar el rostro completo, o en su defecto regiones faciales sensibles como ojos y boca, en las copias destinadas a revisión, almacenamiento secundario, difusión académica o anexos del informe. Esta medida no altera el análisis biomecánico principal en el plano frontal, porque la detección propuesta se concentra en tronco, pelvis y miembros inferiores. Los archivos originales, cuando sean estrictamente necesarios, deberán mantenerse bajo acceso restringido del investigador y únicamente para fines metodológicos del estudio.

Asimismo, se dejará explícito que el sistema propuesto no tiene finalidad diagnóstica clínica, sino que constituye una herramienta de apoyo para el análisis preliminar del movimiento. También se declarará el uso responsable de herramientas computacionales e inteligencia artificial dentro del proceso de desarrollo y redacción, en concordancia con los lineamientos institucionales y con principios de integridad académica.

# 9. CRONOGRAMA DE TRABAJO

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Descripción de objetivos y actividades** | **Descripción** | **Responsable de la actividad** | **Semana** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | **Indicar el objetivo a alcanzar con esta actividad** |
|  |  |  | **1** | **2** | **3** | **4** | **5** | **6** | **7** | **8** | **9** | **10** | **11** | **12** | **13** | **14** | **15** | **16** | **17** | **18** | **19** | **20** | **21** | **22** |  |
| Delimitación del problema y revisión preliminar de literatura | Búsqueda, selección y organización inicial de antecedentes científicos; ajuste del enfoque del estudio y validación de viabilidad. | Tesista y asesor | **X** | **X** | **X** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Delimitar el problema de investigación y establecer una base bibliográfica inicial pertinente. |
| Redacción del estado del arte y marco teórico | Desarrollo del estado del arte, marco teórico y sustento conceptual de variables, dimensiones e indicadores. | Tesista |  |  | **X** | **X** | **X** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Construir el sustento teórico y científico que respalda la investigación. |
| Formulación del problema, objetivos, hipótesis y justificación | Redacción y articulación del planteamiento del problema, objetivos, hipótesis y justificación. | Tesista y asesor |  |  |  | **X** | **X** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Definir con coherencia el planteamiento de la investigación. |
| Diseño metodológico | Definición del enfoque, alcance, diseño, muestra, muestreo, técnicas, instrumentos y estrategia de análisis de datos. | Tesista y asesor |  |  |  |  |  | **X** | **X** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Establecer una metodología viable y alineada con los objetivos específicos. |
| Diseño y validación de instrumentos | Construcción de fichas, matrices e instrumentos metodológicos; revisión ética y validación por juicio de expertos. | Tesista y expertos |  |  |  |  |  |  | **X** | **X** |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Contar con instrumentos consistentes y metodológicamente validados. |
| Entrega del plan de tesis | Ajuste final y presentación del plan de tesis para la evaluación de la semana 8. | Tesista |  |  |  |  |  |  |  | **X** |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Presentar el plan de tesis completo y formalmente estructurado. |
| Preparación operativa de la metodología | Ajuste final de protocolos, estructura de datos, criterios de inclusión y preparación del entorno de trabajo. | Tesista |  |  |  |  |  |  |  |  | **X** | **X** |  |  |  |  |  |  |  |  |  |  |  |  | Dejar lista la base operativa para ejecutar la metodología. |
| Recopilación y depuración de videos | Captura, codificación, revisión técnica y aceptación de videos de sentadilla bilateral según criterios establecidos. | Tesista |  |  |  |  |  |  |  |  |  | **X** | **X** | **X** |  |  |  |  |  |  |  |  |  |  | Obtener una muestra válida de videos para el estudio. |
| Implementación del prototipo computacional | Desarrollo del flujo de análisis por video, estimación de pose 2D, cálculo de variables biomecánicas y criterios interpretables. | Tesista |  |  |  |  |  |  |  |  |  | **X** | **X** | **X** | **X** |  |  |  |  |  |  |  |  |  | Implementar el prototipo funcional de análisis computacional. |
| Procesamiento de videos y registro computacional | Ejecución del sistema sobre los videos válidos y registro de resultados en el Instrumento 2. | Tesista |  |  |  |  |  |  |  |  |  |  |  | **X** | **X** | **X** |  |  |  |  |  |  |  |  | Sistematizar la salida técnica del sistema para cada caso analizado. |
| Evaluación experta y consolidación comparativa | Aplicación del Instrumento 3 por expertos, definición de referencia final y construcción de la matriz complementaria de análisis. | Tesista y expertos |  |  |  |  |  |  |  |  |  |  |  | **X** | **X** | **X** |  |  |  |  |  |  |  |  | Comparar la salida del sistema con la referencia experta de manera estructurada. |
| Sistematización de resultados metodológicos | Organización final de la base consolidada y preparación de la entrega de implementación metodológica. | Tesista |  |  |  |  |  |  |  |  |  |  |  |  |  | **X** |  |  |  |  |  |  |  |  | Presentar resultados sistematizados de la ejecución metodológica. |
| Análisis de resultados | Cálculo de métricas de desempeño técnico, elaboración de matrices de confusión e interpretación inicial de hallazgos. | Tesista |  |  |  |  |  |  |  |  |  |  |  |  |  |  | **X** | **X** |  |  |  |  |  |  | Analizar cuantitativamente el desempeño del sistema propuesto. |
| Tablas, figuras y apoyo visual | Elaboración de tablas, figuras y recursos gráficos para la presentación de resultados. | Tesista |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | **X** |  |  |  |  |  |  | Representar visualmente los resultados de forma clara y académica. |
| Discusión de resultados | Contraste de hallazgos con antecedentes, vacíos identificados y limitaciones del estudio. | Tesista |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | **X** |  |  |  |  |  | Interpretar críticamente los resultados de la investigación. |
| Conclusiones y recomendaciones | Redacción de conclusiones, recomendaciones y cierre argumentativo del estudio. | Tesista |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | **X** |  |  |  |  | Sintetizar los aportes y alcances finales de la tesis. |
| Título, resumen y versión preliminar integral | Ajuste del título, resumen y ensamblaje de la versión preliminar completa del informe de tesis. | Tesista |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | **X** |  |  |  | Preparar una versión integral preliminar del informe. |
| Entrega de versión íntegra de la tesis | Presentación de la versión íntegra para revisión final del asesor y evaluación de la semana 20. | Tesista |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | **X** |  |  | Presentar el informe completo para su revisión académica final. |
| Levantamiento de observaciones | Subsanación de observaciones metodológicas, formales y de redacción realizadas por el asesor. | Tesista y asesor |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | **X** |  | Corregir integralmente el informe antes de la entrega final. |
| Entrega final del informe de tesis | Presentación de la versión final corregida del informe de tesis. | Tesista |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | **X** | Entregar la versión final del informe de tesis. |

# 10. PRESUPUESTO

| Item | Actividad | Recurso | Cantidad | Costo unitario (S/) | Costo total (S/) | Justificación |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Revisión bibliográfica y formulación metodológica | Laptop, conexión a internet y energía eléctrica | 1 | 0 | 0 | Permite realizar búsqueda científica, análisis documental y redacción del proyecto de tesis. |
| 2 | Recopilación y organización de videos | Smartphone o cámara convencional, almacenamiento local y acceso a internet | 1 | 0 | 0 | Se requiere para capturar, transferir, depurar y resguardar los registros audiovisuales del estudio. |
| 3 | Desarrollo del prototipo computacional | Laptop, software libre, entorno de programación e internet | 1 | 0 | 0 | Hace posible implementar el sistema de visión por computadora y ejecutar pruebas técnicas. |
| 4 | Validación de instrumentos y evaluación experta | Servicio de expertos en análisis del movimiento o áreas afines | 3 | 80 | 240 | Se considera para la revisión de instrumentos y la comparación estructurada entre criterio experto y sistema. |
| 5 | Procesamiento estadístico y análisis de resultados | Laptop, internet y software libre de análisis (Python o R) | 1 | 0 | 0 | Permite calcular métricas como exactitud, precisión, sensibilidad, puntaje F1 e índice Kappa. |
| 6 | Elaboración y presentación del informe final | Impresiones, anillado y materiales de oficina | 1 | 50 | 50 | Cubre la preparación física o documental de la versión final requerida por el programa de titulación. |
| Total |  |  |  |  | 290 |  |

Nota: El financiamiento para el desarrollo del presente proyecto de tesis será asumido íntegramente con recursos propios del tesista, por lo que no existe aporte económico externo ni conflicto de interés derivado de financiamiento institucional o empresarial.

# 11. BIBLIOGRAFÍA

\[1] El-Kotob et al., "Resistance training and health in adults: an overview of systematic reviews," PubMed / Appl Physiol Nutr Metab, 2020. doi: 10.1139/apnm-2020-0245. Disponible en: https://pubmed.ncbi.nlm.nih.gov/33054335/

\[2] Serafim et al., "Which resistance training is safest to practice? A systematic review," PMC / Journal of Orthopaedic Surgery and Research, 2023. doi: 10.1186/s13018-023-03781-x. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC10099898/

\[3] Bonilla et al., "Exercise Selection and Common Injuries in Fitness Centers: A Systematic Integrative Review and Practical Recommendations," IJERPH / MDPI / PMC, 2022. doi: 10.3390/ijerph191912710. Disponible en: https://www.mdpi.com/1660-4601/19/19/12710

\[4] Straub y Powers, "A Biomechanical Review of the Squat Exercise: Implications for Clinical Practice," Int J Sports Phys Ther / PMC, 2024. doi: 10.26603/001c.94600. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC10987311/

\[5] Graber et al., "The effect of trunk and shank position on the hip-to-knee moment ratio in a bilateral squat," Physical Therapy in Sport / PubMed, 2023. doi: 10.1016/j.ptsp.2023.03.005. Disponible en: https://pubmed.ncbi.nlm.nih.gov/37001335/

\[6] Erdman et al., "A 2D video-based assessment is associated with 3D biomechanical contributors to dynamic knee valgus in the coronal plane," Frontiers in Sports and Active Living / PMC, 2024. doi: 10.3389/fspor.2024.1352286. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC10978775/

\[7] Forman et al., "The Use of Elastic Resistance Bands to Reduce Dynamic Knee Valgus in Squat-Based Movements: A Narrative Review," Int J Sports Phys Ther / PMC, 2023. doi: 10.26603/001c.87764. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC10547095/

\[8] Liu et al., "Effects of Barbell Squats with Asymmetric Loading on the Joint Moment and Muscle Activity of Lower Limbs," J Hum Kinet / PubMed / PMC, 2025/2026. doi: 10.5114/jhk/202020. Disponible en: https://pubmed.ncbi.nlm.nih.gov/41766814/

\[9] Pellicciari et al., "Associations Between Anthropometric Characteristics, Self-Reported Musculoskeletal and Visceral Symptoms, and Squat Movement Quality: A Cross-Section Study," J Funct Morphol Kinesiol / PMC, 2026. doi: 10.3390/jfmk11010086. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC13028339/

\[10] Falk et al., "How accurate are visual assessments by physical therapists of lumbo-pelvic movements during the squat and deadlift?," Physical Therapy in Sport / ScienceDirect, 2021. doi: 10.1016/j.ptsp.2021.05.011. Disponible en: https://www.sciencedirect.com/science/article/pii/S1466853X21000924

\[11] Gomes et al., "Are visual assessments of the single-leg squat valid to be used in clinical practice? A systematic review of measurement properties based on the COSMIN guideline," PubMed / Physical Therapy in Sport, 2023. doi: 10.1016/j.ptsp.2023.07.009. Disponible en: https://pubmed.ncbi.nlm.nih.gov/37549590/

\[12] Ressman et al., "Visual assessment of movement quality in the single leg squat test: a review and meta-analysis of inter-rater and intrarater reliability," PMC / BMJ Open Sport Exerc Med, 2019. doi: 10.1136/bmjsem-2019-000541. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC6579566/

\[13] Nutarelli et al., "Inter-rater reliability of real-time compared to recorded single-leg squat assessment with the qualitative analysis of single leg loading assessment tool (QASLS) in healthy individuals," Musculoskeletal Science and Practice / ScienceDirect, 2026. doi: 10.1016/j.msksp.2025.103445. Disponible en: https://www.sciencedirect.com/science/article/pii/S2468781225001936

\[14] Ota et al., "Verification of reliability and validity of motion analysis systems during bilateral squat using human pose tracking algorithm," Gait & Posture / ScienceDirect, 2020. doi: 10.1016/j.gaitpost.2020.05.027. Disponible en: https://www.sciencedirect.com/science/article/pii/S0966636220301776

\[15] Mercadal-Baudart et al., "Exercise quantification from single camera view markerless 3D pose estimation," Heliyon / ScienceDirect, 2024. doi: 10.1016/j.heliyon.2024.e27596. Disponible en: https://www.sciencedirect.com/science/article/pii/S2405844024036272

\[16] Pereira et al., "Markerless Pixel-Based Pipeline for Quantifying 2D Lower Limb Kinematics During Squatting: A Preliminary Validation Study," Biomechanics / MDPI, 2026. doi: 10.3390/biomechanics6010001. Disponible en: https://www.mdpi.com/2673-7078/6/1/1

\[17] Lima et al., "Validity and reliability of trunk and lower-limb kinematics during squatting, hopping, jumping and side-stepping using OpenCap markerless motion capture application," J Sports Sci / PubMed, 2024. doi: 10.1080/02640414.2024.2415233. Disponible en: https://pubmed.ncbi.nlm.nih.gov/39444219/

\[18] Powell et al., "Validation of OpenCap on lower extremity kinematics during functional tasks," Journal of Biomechanics / ScienceDirect, 2025. doi: 10.1016/j.jbiomech.2025.112602. Disponible en: https://www.sciencedirect.com/science/article/pii/S0021929025001137

\[19] Kanko et al., "Markerless motion capture estimates of lower extremity kinematics and kinetics are comparable to marker-based across 8 movements," J Sports Sci / PubMed, 2023. doi: 10.1080/02640414.2023.2231987. Disponible en: https://pubmed.ncbi.nlm.nih.gov/37552921/

\[20] Yoma et al., "Reliability and validity of lower extremity and trunk kinematics measured with markerless motion capture during sports-related and functional tasks: A systematic review," Journal of Sports Sciences / Taylor & Francis, 2025. doi: 10.1080/02640414.2025.2518359. Disponible en: https://www.tandfonline.com/doi/full/10.1080/02640414.2025.2518359

\[21] Armitano-Lago et al., "A SWOT Analysis of Portable and Low-Cost Markerless Motion Capture Systems to Assess Lower-Limb Musculoskeletal Kinematics in Sport," Frontiers in Sports and Active Living / PubMed / PMC, 2022. doi: 10.3389/fspor.2021.809898. Disponible en: https://pubmed.ncbi.nlm.nih.gov/35146425/

\[22] Ogura et al., "Are we there yet? A systematic review and meta-analysis of the validity and reliability of automated markerless motion capture systems during jumping tasks," J Sports Sci / PubMed, 2025. doi: 10.1080/02640414.2025.2589689. Disponible en: https://pubmed.ncbi.nlm.nih.gov/41293872/

\[23] Shen et al., "Markerless vision-based functional movement screening movements evaluation with deep neural networks," iScience / ScienceDirect, 2024. doi: 10.1016/j.isci.2023.108705. Disponible en: https://www.sciencedirect.com/science/article/pii/S2589004223027827

\[24] Bae et al., "Concurrent validity and test reliability of the deep learning markerless motion capture system during the overhead squat," Scientific Reports / Nature / PMC, 2024. doi: 10.1038/s41598-024-79707-2. Disponible en: https://www.nature.com/articles/s41598-024-79707-2

\[25] Sadeghi et al., "Squat errors classification based on National Academy of Sports Medicine guidelines using IMU and deep learning algorithms," Computers in Biology and Medicine / ScienceDirect, 2025. doi: 10.1016/j.compbiomed.2025.110962. Disponible en: https://www.sciencedirect.com/science/article/pii/S0010482525013149

\[26] Noël et al., "A conceptual framework and review of multi-method approaches for 3D markerless motion capture in sports and exercise," J Sports Sci / PubMed, 2025. doi: 10.1080/02640414.2025.2544667. Disponible en: https://pubmed.ncbi.nlm.nih.gov/40198152/

\[27] Bazarevsky et al., "BlazePose: On-device Real-time Body Pose tracking," arXiv / CVPR Workshop, 2020. doi: 10.48550/arXiv.2006.10204. Disponible en: https://arxiv.org/abs/2006.10204

\[28] Stenum et al., "Applications of Pose Estimation in Human Health and Performance across the Lifespan," Sensors / MDPI, 2021. doi: 10.3390/s21217315. Disponible en: https://www.mdpi.com/1424-8220/21/21/7315

\[29] Rode et al., "Assessment of monocular human pose estimation models for clinical movement analysis," Scientific Reports / Nature / PMC, 2025. doi: 10.1038/s41598-025-22626-7. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC12589393/

\[30] Hofer et al., "Human Movement Quality Assessment Using Sensor Technologies in Recreational and Professional Sports: A Scoping Review," Sensors / PMC, 2022. doi: 10.3390/s22134786. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC9269395/

\[31] Straub y Powers, "Utility of 2D Video Analysis for Assessing Frontal Plane Trunk and Pelvis Motion during Stepping, Landing, and Change in Direction Tasks: A Validity Study," Int J Sports Phys Ther / PMC, 2022. doi: 10.26603/001c.30994. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC8805121/

\[32] Kim et al., "Verification of Markerless Gait Analysis: Multi-Camera and Single-Camera Approaches in Comparison to Marker-Based Gait Analysis," Medicina / MDPI, 2026. doi: 10.3390/medicina62020418. Disponible en: https://www.mdpi.com/1648-9144/62/2/418

\[33] Edwards et al., "The Validity and Usability of Markerless Motion Capture and Inertial Measurement Units for Quantifying Dynamic Movements," Med Sci Sports Exerc / PubMed, 2025. doi: 10.1249/MSS.0000000000003579. Disponible en: https://pubmed.ncbi.nlm.nih.gov/39733226/

\[34] Ino et al., "Validity of AI-Based Gait Analysis for Simultaneous Measurement of Bilateral Lower Limb Kinematics Using a Single Video Camera," Sensors / PubMed / PMC, 2023. doi: 10.3390/s23249799. Disponible en: https://pubmed.ncbi.nlm.nih.gov/38139644/

\[35] Usami et al., "Gait Analysis Using an Artificial Intelligence-Based Motion Capture System With a Single Smartphone Camera," Cureus / PubMed / PMC, 2025. doi: 10.7759/cureus.87837. Disponible en: https://pubmed.ncbi.nlm.nih.gov/40809664/

\[36] Ohmura et al., "Assessing the Validity and Reliability of a Markerless Motion Capture System for Sagittal-Plane Gait Range of Motion," Cureus / PubMed / PMC, 2025. doi: 10.7759/cureus.99875. Disponible en: https://pubmed.ncbi.nlm.nih.gov/41583137/

\[37] Uhlrich et al., "OpenCap: Human movement dynamics from smartphone videos," PLoS Comput Biol / PubMed, 2023. doi: 10.1371/journal.pcbi.1011462. Disponible en: https://pubmed.ncbi.nlm.nih.gov/37856442/

\[38] Schmitz et al., "The measurement of in vivo joint angles during a squat using a single camera markerless motion capture system as compared to a marker based system," Gait & Posture / ScienceDirect, 2015. doi: 10.1016/j.gaitpost.2015.01.028. Disponible en: https://www.sciencedirect.com/science/article/pii/S0966636215000314

\[39] Lopes et al., "Reliability and Validity of Frontal Plane Kinematics of the Trunk and Lower Extremity Measured With 2-Dimensional Cameras During Athletic Tasks: A Systematic Review With Meta-analysis," J Orthop Sports Phys Ther / PubMed, 2018. doi: 10.2519/jospt.2018.8006. Disponible en: https://pubmed.ncbi.nlm.nih.gov/29895235/

\[40] Curnow et al., "Lower limb biomechanics in femoroacetabular impingement syndrome, asymptomatic cam morphology, and controls during bilateral and single-leg squatting," Gait & Posture / ScienceDirect, 2026. doi: 10.1016/j.gaitpost.2026.110131. Disponible en: https://www.sciencedirect.com/science/article/pii/S0966636226000391

\[41] Dajime, Smith y Zhang, "Automated classification of movement quality using the Microsoft Kinect V2 sensor," Computers in Biology and Medicine / ScienceDirect, 2020. doi: 10.1016/j.compbiomed.2020.104021. Disponible en: https://www.sciencedirect.com/science/article/pii/S0010482520303528

\[42] Kim y Park, "Smartphone-Based Interpretable Machine Learning for Classifying Single-Leg Squat Performance Using Trunk, Pelvic, and Knee Kinematics: Cross-Sectional Study," JMIR mHealth and uHealth / PubMed / ScienceDirect, 2026. doi: 10.2196/85126. Disponible en: https://pubmed.ncbi.nlm.nih.gov/41818471/

\[43] Kianifar et al., "Automated Assessment of Dynamic Knee Valgus and Risk of Knee Injury During the Single Leg Squat," IEEE J Transl Eng Health Med / PMC, 2017. doi: 10.1109/JTEHM.2017.2736559. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC5706595/

\[44] Whatman et al., "Classification of Lower Extremity Movement Patterns Based on Visual Assessment: Reliability and Correlation With 2-Dimensional Video Analysis," J Athl Train / PMC, 2014. doi: 10.4085/1062-6050-49.3.17. Disponible en: https://pmc.ncbi.nlm.nih.gov/articles/PMC4080603/

\[45] Ruder et al., "Evaluating the Agreement of Markerless Motion Capture for Joint Angle Estimation in a Constrained Hallway Setting Compared With a Traditional Laboratory Setting," J Appl Biomech / PubMed, 2026. doi: 10.1123/jab.2025-0265. Disponible en: https://pubmed.ncbi.nlm.nih.gov/41679295

# 12. ANEXOS

## Anexo 1

**Matriz de operacionalización de variables**

| **Variables** | **Definición conceptual** | **Definición operacional** | **Dimensiones** | **Indicadores** | **Unidad de medida** | **Técnicas/Instrumentos** |
| --- | --- | --- | --- | --- | --- | --- |
| Variable 1: Sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables | Sistema computacional que procesa videos de sentadilla bilateral para estimar la postura corporal, extraer información geométrica, calcular variables biomecánicas observables y aplicar criterios interpretables. | Se evaluará mediante la identificación de puntos anatómicos clave, el cálculo de variables biomecánicas observables, la aplicación de criterios biomecánicos y la generación de resultados por prototipo funcional. | 1) Estimación de pose 2D | Promedio de puntos anatómicos clave detectados por fotograma; porcentaje de fotogramas válidos; porcentaje de fotogramas procesados correctamente. | Puntos por fotograma, de un máximo de 13 / porcentaje | Técnica: análisis estructurado de video. Instrumentos: Instrumento 1. Ficha maestra de registro técnico, factibilidad analítica y disponibilidad de landmarks; e Instrumento 2. Ficha de procesamiento computacional, variables biomecánicas y criterios interpretables. |
|  |  |  | 2) Extracción y cálculo de variables biomecánicas observables | Inclinación del tronco; desplazamiento lateral de pelvis; alineación rodilla-cadera-tobillo; diferencias bilaterales. | Grados / valor normalizado / porcentaje | Técnica: análisis estructurado de video. Instrumentos: Instrumento 2. Ficha de procesamiento computacional, variables biomecánicas y criterios interpretables. |
|  |  |  | 3) Aplicación de criterios biomecánicos interpretables | Número de criterios implementados; tipo de compensación detectada; umbrales definidos. | Nominal / razón | Técnica: análisis estructurado de video. Instrumentos: Instrumento 2. Ficha de procesamiento computacional, variables biomecánicas y criterios interpretables. |
|  |  |  | 4) Procesamiento y generación de resultados | Carga de video; procesamiento completo; generación de reporte; visualización de resultados. | Cumple / no cumple; porcentaje | Técnica: análisis estructurado de video. Instrumentos: Instrumento 2. Ficha de procesamiento computacional, variables biomecánicas y criterios interpretables. |
| Variable 2: Desempeño técnico del sistema en la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral | Rendimiento del sistema en la identificación de patrones observables del movimiento, evaluado mediante comparación con una referencia basada en evaluación experta. | Se evaluará mediante detección de compensaciones posturales, detección de asimetrías cinemáticas y métricas de desempeño técnico y concordancia. | 1) Detección de compensaciones posturales | Inclinación lateral del tronco; desplazamiento lateral de pelvis; valgo dinámico visible. | Nominal / ordinal | Técnica: observación experta comparativa y análisis de concordancia. Instrumentos: Instrumento 3. Ficha comparativa de evaluación experta y sistema. |
|  |  |  | 2) Detección de asimetrías cinemáticas | Diferencia entre lado derecho e izquierdo en alineación corporal; diferencia entre lados en desplazamiento; diferencia entre lados en trayectoria relativa. | Diferencia angular / porcentaje / valor normalizado | Técnica: observación experta comparativa y análisis de concordancia. Instrumentos: Instrumento 3. Ficha comparativa de evaluación experta y sistema. |
|  |  |  | 3) Desempeño técnico de la detección | Exactitud; precisión; sensibilidad; especificidad; puntaje F1; índice Kappa. | Porcentaje / índice | Técnica: observación experta comparativa y análisis de concordancia. Instrumentos: Instrumento 3. Ficha comparativa de evaluación experta y sistema. |

## Anexo 2

**Instrumento 1. Ficha maestra de registro técnico, factibilidad analítica y disponibilidad de puntos anatómicos clave detectados**

Uso: registro inicial de videos, evaluación de factibilidad de procesamiento y disponibilidad de puntos anatómicos clave visibles o detectables.

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Identificación** |  |  |  |  | **Datos del caso** |  | **Condiciones técnicas** |  |  |  |  |  |  |  |
| **Número** | **Código del video** | **Fecha de registro** | **Fuente del video** | **Link o ruta del video** | **Edad del participante** | **Sexo del participante** | **Vista de captura** | **Dispositivo de captura** | **Resolución** | **Frecuencia de video** | **Iluminación** | **Fondo visual** | **Visibilidad corporal** | **Oclusiones** |
| 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 9 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 10 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Control manual de la condición de apoyo** |  |  |  |  | **Factibilidad** |  |  |
| **Superficie de ejecución** | **Soporte externo debajo de los talones** | **Contacto aparente de ambos talones con el suelo** | **Cumplimiento de la condición de apoyo** | **Observación sobre el apoyo plantar** | **Sentadilla observable completa** | **Video válido para procesamiento** | **Motivo de exclusión** |

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| **Puntos anatómicos clave** |  |  |  |  |  |  |
| **Hombro** | **Cadera** | **Rodilla** | **Tobillo** | **Talón** | **Punta del pie** | **Nariz o centro facial** |

| Código sugerido | Significado operativo |
| --- | --- |
| B | Se observan de forma suficiente ambos lados del punto anatómico clave detectado par para un análisis confiable. |
| I | Solo el lado izquierdo es visible o detectable con suficiente claridad. |
| D | Solo el lado derecho es visible o detectable con suficiente claridad. |
| O | El punto anatómico clave detectado aparece con oclusión, intermitencia o evidencia insuficiente para uso estable. |
| N | El punto anatómico clave detectado no es visible o no sería razonable esperar su detección. |
| C | Aplicable a nariz o centro facial cuando el punto central se observa con claridad. |

|  |  |  |
| --- | --- | --- |
| **Escalas técnicas** |  |  |
| **Campo** | **Nivel** | **Definición breve** |
| Iluminación | Adecuada | Distingue con claridad tronco, pelvis y miembros inferiores |
| Iluminación | Regular | Limitación leve, pero el cuerpo sigue siendo analizable |
| Iluminación | Deficiente | Compromete la observación de segmentos o puntos anatómicos clave detectados |
| Fondo visual | Adecuado | Existe contraste suficiente entre participante y fondo |
| Fondo visual | Regular | Hay dificultad leve, pero el cuerpo sigue siendo identificable |
| Fondo visual | Deficiente | Dificulta claramente la lectura corporal |
| Visibilidad corporal | Completa | Se observan tronco, pelvis y ambos miembros inferiores |
| Visibilidad corporal | Parcial utilizable | Hay recorte menor no crítico |
| Visibilidad corporal | Insuficiente | Faltan segmentos críticos para el análisis |
| Oclusiones | Ninguna | Sin interferencia |
| Oclusiones | Leve | No afecta sustancialmente el análisis |
| Oclusiones | Moderada | Limita parcialmente algunas mediciones |
| Oclusiones | Severa | Impide observación confiable |

|  |  |  |  |
| --- | --- | --- | --- |
| **Criterio de aceptación** |  |  |  |
| **Campo** | **Regla** | **Valor esperado** | **Observación** |
| Vista de captura | Corresponde al protocolo | Sí | Según el estudio |
| Sentadilla observable completa | Se observa secuencia completa | Sí | Posición inicial, descenso y ascenso |
| Iluminación | Escala aceptable | Adecuada o Regular | Deficiente excluye |
| Fondo visual | Escala aceptable | Adecuado o Regular | Deficiente excluye |
| Visibilidad corporal | Escala aceptable | Completa o Parcial utilizable | Insuficiente excluye |
| Oclusiones | Escala aceptable | Ninguna, Leve o Moderada | Severa excluye |
| Puntos anatómicos clave detectados críticos | Disponibilidad suficiente | Cadera=B; Rodilla=B; Tobillo=B; pie distal suficiente | Si no cumple, excluir |
| Video válido para procesamiento | Decisión final | Sí / No | Se define con base en todas las reglas |

|  |  |  |  |
| --- | --- | --- | --- |
| **Control manual de la condición de apoyo** |  |  |  |
| **Campo** | **Opciones** | **Valor esperado** | **Acción** |
| Superficie de ejecución | Plana / No plana / No verificable | Plana | Repetir si no cumple |
| Soporte externo debajo de los talones | No / Sí / No verificable | No | Repetir si no cumple |
| Contacto aparente de ambos talones | Continuo / Elevación breve / Elevación evidente o sostenida / No verificable | Continuo | Repetir ante incidencia |
| Cumplimiento de la condición de apoyo | Sí / No | Sí | Decisión manual |
| Observación sobre el apoyo plantar | Texto breve | Según corresponda | Justificar incidencia |

## Anexo 3

**Instrumento 2. Ficha de procesamiento computacional, variables biomecánicas y criterios interpretables**

Uso: registrar la salida del sistema para cada video válido.

Esta hoja debe ser llenada por el investigador a partir de la salida automática del software. No corresponde al juicio del evaluador experto.

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Identificación |  | Procesamiento |  |  |  |  |  |  | Variables biomecánicas |  |  |  | Criterios interpretables |  |  | Salida final |  |
| Número | Código del video | Estado de procesamiento | Cantidad total de frames | Frames válidos para análisis | % de frames válidos | Frames procesados correctamente | % frames procesados correctamente | Promedio de puntos anatómicos clave detectados por fotograma | Inclinación del tronco | Desplazamiento lateral de pelvis | Alineación rodilla-cadera-tobillo | Diferencias bilaterales | N° de criterios implementados | Tipo de compensación detectada | Umbral aplicado | Generación de reporte | Visualización de resultados |
| 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 9 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 10 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

| Campo | Codificación sugerida |
| --- | --- |
| Estado de procesamiento | Exitoso / parcial / fallido |
| Inclinación del tronco | Valor numérico y/o categoría derivada del eje troncal, por ejemplo 4.6° o derecha leve |
| Desplazamiento lateral de pelvis | Valor numérico y/o categoría lateral, por ejemplo 2.1 cm o izquierda |
| Alineación rodilla-cadera-tobillo | Valor angular, distancia relativa o índice observacional vinculado al valgo visible |
| Diferencias bilaterales | Diferencia absoluta, porcentual o índice de simetría entre lado derecho e izquierdo |
| Tipo de compensación detectada | Tronco / pelvis / valgo / asimetría |
| Umbral aplicado | Regla o límite usado para transformar la variable biomecánica en hallazgo interpretable |
| Generación de reporte | Sí / no |
| Visualización de resultados | Sí / no |

|  |  |
| --- | --- |
| **Definición operacional del promedio de puntos detectados** |  |
| **Elemento** | **Definición** |
| Indicador | Promedio de puntos anatómicos clave detectados por fotograma |
| Conjunto evaluado | 13 puntos: nariz y referencias bilaterales de hombros, caderas, rodillas, tobillos, talones y puntas de los pies |
| Criterio de detección | Visibilidad igual o superior a 0,5 por punto y fotograma |
| Unidad | Puntos por fotograma, de un máximo de 13 |
| Fórmula | Suma de puntos detectados en todos los fotogramas / número de fotogramas procesados |
| Fuente | frame_quality.csv y pose_summary.json |
| Aclaración | Describe cobertura; la validez depende de la disponibilidad de las referencias críticas requeridas |

## Anexo 4

**Instrumento 3. Ficha comparativa de evaluación experta y sistema**

Uso: comparar, por video, las clasificaciones de los evaluadores expertos frente al sistema.

Los expertos solo deben llenar sus columnas de evaluación. Las columnas del sistema y de consolidación serán completadas por el investigador.

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Identificación |  | Evaluador 1 |  |  |  | Evaluador 2 |  |  |  | Evaluador 3 |  |  |  | Sistema computacional |  |  |  | Consolidación |  |  |  |
| Número | Código del video | Tronco | Pelvis | Valgo | Asimetría bilateral | Tronco | Pelvis | Valgo | Asimetría bilateral | Tronco | Pelvis | Valgo | Asimetría bilateral | Tronco | Pelvis | Valgo | Asimetría bilateral | Ref. final tronco | Ref. final pelvis | Ref. final valgo | Ref. final asimetría |
| 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 9 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

| Patrón | Codificación sugerida |
| --- | --- |
| Tronco | Ausente / izquierda / derecha / no concluyente |
| Pelvis | Ausente / izquierda / derecha / no concluyente |
| Valgo | Ausente / izquierdo / derecho / bilateral / no concluyente |
| Asimetría bilateral | Ausente / presente / no concluyente |

Regla de consolidación: la referencia final (Ref. final) será completada por el investigador. Con dos evaluadores se definirá por coincidencia directa o consenso posterior. Si participa un tercer evaluador, se aplicará mayoría absoluta; en caso de discrepancia total, se recurrirá a consenso guiado y se dejará constancia en observaciones.
