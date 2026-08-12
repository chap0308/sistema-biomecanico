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

[Variable 2: Desempeño técnico del sistema en la clasificación de patrones observables durante la sentadilla bilateral. 18](#variable-2-desempeño-técnico-del-sistema-en-la-clasificación-de-patrones-observables-durante-la-sentadilla-bilateral)

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

La investigación se delimita al análisis bidimensional monocular de una sentadilla bilateral sin carga externa, observada desde una vista anterior dentro del plano frontal y registrada bajo condiciones controladas o semicontroladas en Lima Sur durante 2026. El sistema analizará cuatro patrones observables: inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y diferencia bilateral de alineación de rodillas. No pretende reconstruir la biomecánica tridimensional, inferir causas anatómicas, evaluar patologías, sustituir el juicio profesional ni emitir diagnósticos clínicos. Para la evaluación formal frente a expertos, cada video contendrá una sola repetición completa elegible; la capacidad tecnológica de procesar varias repeticiones se considerará una funcionalidad del prototipo y no modificará la unidad de análisis de la tesis.

# 2. PREGUNTA GENERAL Y ESPECÍFICAS

## 2.1 Pregunta general

¿Cuál es el desempeño técnico del sistema de visión por computadora propuesto para detectar compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral, en comparación con un criterio de referencia basado en evaluación experta en Lima Sur, 2026?

## 2.2 Preguntas específicas

- a. ¿Qué puntos anatómicos clave del cuerpo (landmarks) en 2D son relevantes para el análisis biomecánico observable de la sentadilla bilateral mediante visión por computadora?
- b. ¿Qué procedimiento de segmentación temporal permite delimitar repeticiones completas y localizar el fotograma de máxima profundidad de la sentadilla bilateral?
- c. ¿Qué variables biomecánicas observables pueden calcularse a partir de los puntos anatómicos clave del cuerpo (landmarks) en 2D y del fotograma de máxima profundidad para representar los patrones estudiados?
- d. ¿Qué criterios biomecánicos interpretables pueden diseñarse para detectar inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y diferencia bilateral de alineación de rodillas?
- e. ¿Cómo implementar un prototipo funcional que integre el registro del caso, procesamiento del video, segmentación, cálculo biomecánico, clasificación interpretable, visualización y generación de reportes?
- f. ¿Cuál es el desempeño técnico del sistema propuesto en la detección de los patrones estudiados, en comparación con un criterio de referencia basado en evaluación experta?

# 3. OBJETIVO GENERAL Y ESPECÍFICOS

## 3.1 Objetivo General

Diseñar e implementar un sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables para detectar compensaciones posturales y asimetrías cinemáticas durante la ejecución de sentadillas bilaterales en Lima Sur, 2026.

## 3.2 Objetivos Específicos

- a. Identificar los puntos anatómicos clave del cuerpo (landmarks) en 2D relevantes para el análisis biomecánico observable de la sentadilla bilateral a partir de videos capturados con cámara convencional.
- b. Establecer un procedimiento de segmentación temporal basado en la trayectoria vertical del punto medio de las caderas para delimitar repeticiones completas y localizar el fotograma de máxima profundidad de la sentadilla bilateral.
- c. Definir y calcular variables biomecánicas observables derivadas de los puntos anatómicos clave del cuerpo (landmarks) en 2D y de los eventos temporales de la sentadilla bilateral.
- d. Diseñar criterios biomecánicos interpretables para detectar inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y diferencia bilateral de alineación de rodillas.
- e. Implementar un prototipo funcional que integre el registro del caso, procesamiento del video, estimación de pose 2D, segmentación temporal, cálculo biomecánico, clasificación interpretable, visualización y generación de reportes.
- f. Evaluar el desempeño técnico del sistema propuesto mediante métricas de clasificación y concordancia frente a un criterio de referencia basado en evaluación experta.

# 4. JUSTIFICACIÓN

## 4.1 Justificación teórica

Desde el punto de vista teórico, la investigación aporta a la integración entre visión por computadora, estimación de pose humana, procesamiento de señales y biomecánica observacional aplicada al análisis de ejercicios funcionales. Su relevancia radica en organizar una base conceptual que permita transformar puntos anatómicos clave del cuerpo (landmarks) en dos dimensiones en una señal temporal de la ejecución, eventos biomecánicos delimitados, variables observables y criterios interpretables. Asimismo, contribuye a precisar el alcance de cuatro patrones: inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y diferencia bilateral de alineación de rodillas. Esta articulación se sostiene en antecedentes que van desde la estimación general de pose, desarrollada por Bazarevsky et al. \[27], Stenum et al. \[28] y Rode et al. \[29], hasta estudios específicos sobre sentadilla, análisis del movimiento sin marcadores y evaluación de la calidad del movimiento, como los de Ota et al. \[14], Pereira et al. \[16], Hofer et al. \[30] y Noël et al. \[26].

## 4.2 Justificación metodológica

Metodológicamente, la propuesta es pertinente porque establece un procedimiento sistemático para la captura y registro de videos, decodificación de fotogramas, estimación de pose 2D, control de calidad, segmentación temporal de cada ejecución, cálculo de variables en máxima profundidad, aplicación de criterios interpretables y evaluación frente a expertos. Cada etapa genera evidencia visual, tabular o numérica que puede conservarse y auditarse. La integración mediante una interfaz web y una API permite aplicar el mismo flujo a todos los casos, separar los roles del investigador y de los evaluadores, ocultar los resultados automáticos durante la evaluación ciega y conservar la trazabilidad de clasificaciones, reportes y métricas. La pertinencia del método se refuerza con literatura que muestra tanto las capacidades como las limitaciones del análisis del movimiento sin marcadores, ya sea en soluciones monoculares o multicámara. Entre estos antecedentes destacan Straub y Powers \[31], Bae et al. \[24], Halilaj et al. \[20], Armitano-Lago et al. \[21], Kim et al. \[32] y Kanko et al. \[33].

## 4.3 Justificación práctica

En el plano práctico, la investigación busca generar una herramienta de apoyo para el análisis preliminar de la sentadilla bilateral en contextos de entrenamiento, evaluación funcional y seguimiento corporal. El sistema propuesto no pretende reemplazar la evaluación especializada, sino facilitar una detección inicial de compensaciones y asimetrías de forma más accesible y consistente. Esto puede resultar útil en escenarios donde no se cuenta con equipamiento biomecánico avanzado, pero sí con cámaras convencionales y necesidad de observación estructurada del movimiento. En ese sentido, el aporte del sistema no radica en negar que algunas compensaciones visibles puedan identificarse a simple vista, sino en transformar esa observación en un procedimiento técnico estandarizado, interpretable, reproducible y evaluable frente a expertos, con trazabilidad de variables, reglas de decisión y resultados.

El prototipo organizará esta utilidad mediante roles diferenciados. El investigador administrará casos, resultados y evaluaciones; los expertos clasificarán de forma ciega los casos asignados; y, como extensión funcional posterior a la evaluación formal, un usuario final podrá registrarse, consultar la guía de captura, cargar su propio video y recibir resultados automáticos con orientaciones generales. Esta última salida tendrá carácter educativo y preventivo, no diagnóstico, y deberá comunicar de forma explícita las condiciones de captura, la incertidumbre y la recomendación de acudir a un profesional cuando corresponda.

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

Definición conceptual. La primera variable corresponde al sistema computacional que procesa videos de sentadilla bilateral para estimar la postura corporal, controlar la calidad de la evidencia, segmentar temporalmente cada ejecución, extraer información geométrica, calcular variables biomecánicas observables y aplicar reglas interpretables. Conceptualmente, esta variable se apoya en la visión por computadora como campo capaz de transformar imágenes y videos en información estructurada, en la estimación de pose humana como técnica que representa el cuerpo mediante puntos anatómicos clave del cuerpo (landmarks) y en el procesamiento de señales como medio para localizar eventos temporales del movimiento. Bazarevsky et al. \[27], Stenum et al. \[28] y Rode et al. \[29] sustentan la representación corporal mediante estimación de pose, mientras que Ota et al. \[14], Lima et al. \[17] y Kanko et al. \[19] muestran su aplicación en el análisis funcional del movimiento bajo condiciones de captura delimitadas.

Dimensión 1: estimación de pose 2D. Esta dimensión representa la capacidad del sistema para detectar y seguir puntos anatómicos clave corporales en un plano bidimensional a partir de una sola cámara convencional. Su relevancia teórica proviene de que la estimación de pose 2D constituye la base computacional sobre la cual se construyen las mediciones posteriores del sistema, especialmente en escenarios donde se prioriza accesibilidad y viabilidad frente a esquemas multicámara más complejos, como plantean Bazarevsky et al. \[27], Rode et al. \[29] y Lopes et al. \[39]. Diversos antecedentes muestran que el rendimiento de esta dimensión depende de variables como el protocolo de captura, la oclusión, la calidad visual y la tarea motriz observada, tal como discuten Kim et al. \[32], Ohmura et al. \[36] y Needham et al. \[45].

- Indicador 1.1: promedio de puntos anatómicos clave detectados por fotograma. Expresa la cobertura media de las referencias seleccionadas durante el procesamiento. Se consideran 13 puntos: nariz y referencias bilaterales de hombros, caderas, rodillas, tobillos, talones y puntas de los pies. Un punto se contabiliza cuando posee coordenadas 2D finitas y visibilidad igual o superior a 0,5. Se calcula como `K̄ = (1 / F_dec) × Σ K_f`, donde `F_dec` es el número de fotogramas decodificados y `K_f` la cantidad de puntos utilizables en el fotograma `f`. Su unidad es puntos por fotograma, con máximo de 13. La selección y el umbral son decisiones operativas, no valores clínicos universales. El promedio describe cobertura, pero no determina por sí solo la validez analítica.

- Indicador 1.2: porcentaje de fotogramas válidos. Representa la proporción de fotogramas decodificados que contienen evidencia suficiente para el análisis: ambos hombros, caderas, rodillas y tobillos utilizables, además de al menos una referencia distal utilizable por cada pie, que puede ser talón o punta del pie. Se calcula como `P_valid = 100 × Σ valid_for_analysis(f) / F_dec`, donde `valid_for_analysis(f)` vale 1 cuando se cumple la regla y 0 en caso contrario. La visibilidad crítica mínima es el menor valor entre los ocho puntos centrales y no constituye un promedio. Lopes et al. \[39], Ohmura et al. \[36] y Needham et al. \[45] respaldan la necesidad de controlar oclusión, visibilidad y estabilidad en soluciones monoculares.

- Indicador 1.3: porcentaje de fotogramas procesados correctamente. Representa la proporción de fotogramas declarados por el archivo que OpenCV logra decodificar y entregar al flujo. Se calcula como `P_proc = 100 × F_dec / F_decl`, donde `F_dec` es la cantidad de fotogramas decodificados y `F_decl` la cantidad declarada en las propiedades del video. Se diferencia del porcentaje de fotogramas válidos porque mide continuidad técnica de lectura, no suficiencia anatómica. Su uso es coherente con enfoques que consideran la estabilidad del procesamiento como parte del desempeño del sistema, como muestran Ota et al. \[14], Lima et al. \[17] y Kanko et al. \[19].

Dimensión 2: segmentación temporal de la sentadilla. Esta dimensión representa la capacidad del sistema para transformar las coordenadas por fotograma en repeticiones completas y eventos temporales interpretables. La señal empleada es la posición vertical normalizada del punto medio de ambas caderas, `h_y(f) = (y_cadera_izquierda(f) + y_cadera_derecha(f)) / 2`. Debido a que el eje vertical de la imagen aumenta hacia abajo, los máximos de esta señal representan mayor profundidad. La señal se interpola únicamente para conservar continuidad temporal, se suaviza mediante mediana y promedio móviles centrados y se analiza mediante máximos locales, prominencia y recuperación. Este procedimiento no crea evidencia biomecánica en fotogramas inválidos: la puerta de calidad conserva la validez original de cada fotograma. El uso de señales verticales y detección de picos para delimitar repeticiones posee antecedentes en el análisis automatizado de tareas funcionales \[46].

- Indicador 2.1: repeticiones completas detectadas. Corresponde al número de ciclos con inicio, descenso, máxima profundidad, ascenso y cierre delimitados. Los máximos candidatos deben superar una prominencia mínima adaptativa: `p_min = max(0,03; 0,18 × (P95 - P05))`. La prominencia local se calcula como `p(P) = P - max(B_I, B_D)`, con bases buscadas dentro de una ventana temporal acotada. La separación mínima entre máximos y la validación de recuperación evitan contar como repeticiones distintas las oscilaciones producidas durante una pausa profunda. Estos parámetros son heurísticas versionadas del prototipo y deberán evaluarse con los casos de la muestra; no son puntos de corte clínicos.

- Indicador 2.2: porcentaje de fotogramas válidos por repetición. Se calcula como `P_valid_rep = 100 × Σ valid_for_analysis(f) / F_rep` dentro del intervalo de cada repetición. La política técnica exige al menos 80 % para aceptar la repetición y utiliza 90 % como nivel recomendado de calidad.

- Indicador 2.3: validez del fotograma de máxima profundidad. Indica si el fotograma utilizado para calcular las variables contiene todas las referencias críticas requeridas. Se expresa como válido o no válido; una repetición cuyo fotograma de máxima profundidad sea inválido se excluye del cálculo biomecánico formal.

- Indicador 2.4: duración temporal de la repetición. Comprende duración de descenso, ascenso y ciclo completo, expresadas en segundos. Estos valores describen y permiten auditar la segmentación, pero no constituyen por sí mismos compensaciones biomecánicas.

Dimensión 3: extracción y cálculo de variables biomecánicas observables. Esta dimensión alude a la transformación de puntos anatómicos clave 2D en medidas geométricas que representen patrones observables del movimiento. Las series se calculan en los fotogramas válidos, pero el valor que ingresa a las reglas corresponde al fotograma de máxima profundidad de cada repetición elegible. La visión por computadora por sí sola no produce interpretación biomecánica; esta surge cuando las coordenadas se convierten en variables funcionalmente significativas, como sostienen Straub y Powers \[31], Straub y Powers \[4] y Graber et al. \[5].

- Indicador 3.1: inclinación lateral del tronco. Representa el ángulo entre el eje formado por el centro de pelvis y el centro de hombros y la vertical de referencia: `θ = atan2(Sx - Px, Py - Sy)`. Se expresa en grados. La magnitud se compara con los umbrales y el signo determina la dirección anatómica. Straub y Powers \[31], Straub y Powers \[4] y Graber et al. \[5] respaldan la pertinencia del control frontal del tronco.

- Indicador 3.2: desplazamiento lateral de pelvis. Expresa el cambio horizontal del centro pélvico respecto del centro de tobillos, corregido por el valor inicial y normalizado mediante el ancho inicial de hombros `W0`: `Pelvis_% = 100 × (offset_pelvis(f_pico) - offset_pelvis,inicial) / W0`. `W0` es la mediana de la distancia horizontal entre hombros en fotogramas válidos del reposo inicial. La unidad es porcentaje de `W0`; la magnitud se compara con los umbrales y el signo informa la dirección anatómica. Su interés biomecánico se relaciona con el control frontal de pelvis \[31], \[6].

- Indicador 3.3: desviación medial de rodilla respecto de la alineación cadera-rodilla-tobillo. Para cada lado se estima mediante interpolación lineal la posición horizontal esperada de la rodilla sobre el eje cadera-tobillo: `t = (Ky - Hy) / (Ay - Hy)` y `Kx_esperado = Hx + t(Ax - Hx)`. La desviación se calcula como `D_rodilla = 100 × s_medial × (Kx_real - Kx_esperado) / W0`. Se expresa como porcentaje de `W0`; un valor positivo representa desviación medial y un valor negativo desviación lateral. Cada rodilla se evalúa por separado para clasificar valgo izquierdo, derecho o bilateral. Erdman et al. \[6], Forman et al. \[7] y Kianifar et al. \[43] sustentan la pertinencia del valgo dinámico observable en tareas de sentadilla.

- Indicador 3.4: diferencia bilateral de alineación de rodillas. Representa la diferencia absoluta entre las desviaciones mediales normalizadas de ambas rodillas: `D_bilateral = |D_izquierda - D_derecha|`. Se expresa como porcentaje de `W0`. El lado con mayor desviación medial firmada puede describirse como predominio izquierdo o derecho. Este indicador no representa una asimetría corporal general, no evalúa trayectorias completas y no constituye diagnóstico. Mercadal-Baudart et al. \[15] y Liu et al. \[8] respaldan la necesidad de interpretar con prudencia las diferencias laterales.

Dimensión 4: aplicación de criterios biomecánicos interpretables. Esta dimensión se refiere al conjunto de reglas explícitas mediante las cuales el sistema traduce variables geométricas en patrones comprensibles. La tesis no propone una salida de caja negra: cada clasificación conserva la variable, valor, unidad, umbral, estado y dirección que la originaron. Este enfoque se aproxima a estrategias interpretables en las que la salida puede justificarse a partir de variables identificables \[42], \[23], \[30].

- Indicador 4.1: estado de clasificación por patrón. Cada patrón se evalúa de forma independiente como ausente, no concluyente o presente. La banda no concluyente evita forzar una decisión cuando el valor se encuentra entre el máximo de ausencia y el mínimo de presencia.

- Indicador 4.2: lateralidad o predominio del patrón. Registra izquierda, derecha o bilateralidad para los patrones que lo permiten, y predominio izquierdo, derecho o sin predominio claro para la diferencia bilateral de alineación. La dirección describe la geometría observable y no una causa anatómica.

- Indicador 4.3: umbral aplicado y trazabilidad del resultado. Registra el valor de decisión utilizado para cada variable y la relación entre evidencia, regla y salida. Los umbrales iniciales son provisionales, no clínicos y deberán evaluarse frente a la referencia experta antes de considerarse estables.

Dimensión 5: procesamiento y generación de resultados. Esta dimensión corresponde a la capacidad del prototipo para ejecutar de manera integrada el registro, almacenamiento, análisis, visualización y entrega de resultados. La utilidad técnica depende de que el flujo completo opere de forma estable, reproducible y trazable \[14], \[37], \[17].

- Indicador 5.1: registro y carga del caso. Expresa la capacidad del prototipo para recibir los datos requeridos, almacenar el video de forma trazable y abrir un archivo audiovisual compatible. Se expresa como cumplimiento o no cumplimiento.

- Indicador 5.2: procesamiento completo. Se refiere a la capacidad del sistema para completar las etapas previstas sin interrupciones críticas y generar un estado técnico explícito. Se diferencia del procesamiento por fotograma porque aquí la unidad es el caso completo. Se expresa como cumple/no cumple o porcentaje de casos completados.

- Indicador 5.3: generación de reporte. Representa la capacidad de producir una salida estructurada con calidad, segmentación, variables, reglas y hallazgos por repetición. El reporte permite conservar, revisar y comparar la evidencia con la referencia experta. Se expresa como sí/no.

- Indicador 5.4: visualización y recuperación de resultados. Alude a la presentación comprensible y persistente de tablas, gráficos, imágenes, videos superpuestos y archivos descargables. Se vincula con la trazabilidad y comunicabilidad del resultado y puede evaluarse como presencia o ausencia de las salidas previstas.

## Variable 2: Desempeño técnico del sistema en la clasificación de patrones observables durante la sentadilla bilateral.

Definición conceptual. La segunda variable corresponde al rendimiento del sistema al clasificar los cuatro patrones observables por repetición, evaluado mediante comparación con una referencia experta final. Se vincula con la literatura sobre validez, confiabilidad y utilidad de sistemas de análisis del movimiento, así como con estudios que comparan soluciones automáticas o semiautomáticas frente a juicio experto o referencias biomecánicas de mayor fidelidad \[14], \[42], \[24], \[12]. Esta variable no describe la existencia del sistema, sino la calidad y concordancia de sus clasificaciones.

Dimensión 1: desempeño de clasificación por patrón. Esta dimensión expresa la calidad con la que el sistema identifica la presencia o ausencia de inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y diferencia bilateral de alineación de rodillas. Cada patrón se analiza como una tarea binaria independiente después de excluir los pares no concluyentes. Su fundamento se encuentra en la evaluación funcional del plano frontal y en la comparación estructurada de sistemas automáticos frente a referencias humanas \[31], \[6], \[10], \[11], \[13].

- Indicador 1.1: exactitud. Proporción total de clasificaciones correctas respecto del total de pares concluyentes: `Exactitud = (VP + VN) / (VP + VN + FP + FN)`.

- Indicador 1.2: precisión. Proporción de clasificaciones positivas del sistema que coinciden con la referencia: `Precisión = VP / (VP + FP)`.

- Indicador 1.3: sensibilidad. Proporción de patrones positivos en la referencia detectados por el sistema: `Sensibilidad = VP / (VP + FN)`.

- Indicador 1.4: especificidad. Proporción de patrones negativos en la referencia reconocidos como ausentes por el sistema: `Especificidad = VN / (VN + FP)`.

- Indicador 1.5: puntaje F1 (F1-score). Media armónica entre precisión y sensibilidad: `F1 = 2 × (Precisión × Sensibilidad) / (Precisión + Sensibilidad)`. Se reportará por patrón y mediante un resumen macro, evitando que el desempeño de una categoría compense el de otra.

Dimensión 2: concordancia de las clasificaciones. Representa el acuerdo más allá del azar. La confiabilidad de la referencia humana y la concordancia sistema-referencia son análisis relacionados, pero diferentes \[12], \[44], \[13].

- Indicador 2.1: Kappa de Cohen. Cuantifica el acuerdo entre la salida binaria del sistema y la referencia experta final: `κ = (Po - Pe) / (1 - Pe)`, donde `Po` es el acuerdo observado y `Pe` el acuerdo esperado por azar.

- Indicador 2.2: Kappa de Fleiss. Se calculará cuando participen tres evaluadores para describir la concordancia entre ellos antes de consolidar la referencia final. No sustituye a Kappa de Cohen entre sistema y referencia experta.

# 7. HIPÓTESIS

## 7.1 Hipótesis general

El sistema de visión por computadora basado en estimación de pose 2D, segmentación temporal y criterios biomecánicos interpretables permite detectar patrones observables durante la sentadilla bilateral y obtener un desempeño técnico cuantificable frente a un criterio de referencia basado en evaluación experta en Lima Sur, 2026.

## 7.2 Hipótesis específicas

- a. La identificación de puntos anatómicos clave corporales 2D permite representar segmentos corporales relevantes para el análisis biomecánico observable de la sentadilla bilateral.
- b. La trayectoria vertical del punto medio de las caderas, después de su limpieza y análisis de prominencia, permite delimitar repeticiones completas y localizar el fotograma de máxima profundidad bajo las condiciones del protocolo.
- c. Las relaciones geométricas calculadas a partir de puntos anatómicos clave 2D y del fotograma de máxima profundidad permiten cuantificar la inclinación lateral del tronco, el desplazamiento lateral de pelvis, la desviación medial de cada rodilla y la diferencia bilateral de alineación de rodillas.
- d. Los criterios biomecánicos interpretables permiten clasificar de forma independiente la presencia, ausencia, lateralidad o indeterminación de los cuatro patrones observables.
- e. El prototipo funcional permite registrar casos, procesar videos, conservar evidencia, visualizar resultados y generar reportes interpretables y trazables.
- f. El sistema propuesto presenta un desempeño técnico cuantificable mediante métricas de clasificación y concordancia frente a la referencia experta final.

# 8. METODOLOGÍA

## 8.1 Tipo y diseño

La investigación será de enfoque cuantitativo y de tipo aplicada. Se adopta el enfoque cuantitativo porque se trabajará con variables observables derivadas de la estimación de pose 2D, se calcularán medidas geométricas y biomecánicas obtenidas a partir de videos de sentadilla bilateral y se evaluará el desempeño técnico del sistema mediante métricas numéricas de clasificación y concordancia. Será de tipo aplicada porque busca desarrollar una solución tecnológica orientada a un problema concreto: la detección de compensaciones posturales y asimetrías cinemáticas durante la sentadilla bilateral.

En cuanto al alcance, la investigación será descriptivo-propositiva. Será descriptiva porque identificará y organizará variables biomecánicas observables, patrones posturales y criterios de decisión asociados a la ejecución del ejercicio. Será propositiva porque, a partir de esa base, diseñará e implementará un sistema funcional capaz de detectar dichos patrones de manera estructurada e interpretable. El diseño será no experimental, transversal y tecnológico-evaluativo. Será no experimental porque no se manipularán deliberadamente las condiciones corporales de las personas registradas; transversal porque los videos se recopilarán y analizarán dentro de un periodo específico; y tecnológico-evaluativo porque culminará con el diseño, implementación, uso y evaluación técnica del prototipo funcional frente a una referencia basada en evaluación experta. Esta elección metodológica es congruente con estudios como Ota et al. \[14], Dajime et al. \[41], Bae et al. \[24], Uhlrich et al. \[37] y Lima et al. \[17].

## 8.2 Población

La población del estudio estará conformada por registros audiovisuales de personas adultas ejecutando sentadillas bilaterales, capturados mediante cámara convencional bajo condiciones definidas de registro. El video constituirá la unidad de registro y trazabilidad del caso, mientras que una repetición completa y técnicamente elegible constituirá la unidad biomecánica de cálculo y clasificación. Para la evaluación formal frente a expertos, cada video incorporado a la muestra contendrá una sola repetición; de esta manera, cada caso aportará una unidad independiente para comparar los cuatro patrones estudiados.

Como criterios de inclusión se considerarán videos de personas adultas capaces de ejecutar sentadillas bilaterales completas o suficientemente observables para identificar las fases de descenso y ascenso, con visibilidad del cuerpo completo o de los segmentos necesarios para el análisis del tronco, pelvis y miembros inferiores, capturados con cámara convencional en vista anterior dentro del plano frontal y con calidad visual suficiente para la detección estable de pose. La ejecución deberá realizarse sin carga externa, sobre una superficie plana, sin discos, cuñas u otros soportes colocados debajo de los talones y procurando mantener ambos talones en contacto con el suelo durante el movimiento. Como criterios de exclusión se contemplarán videos con oclusión significativa, iluminación deficiente, desenfoque excesivo, movimientos incompletos, registros fuera del plano frontal, carga externa, implementos que oculten segmentos relevantes, uso de soportes elevados debajo de los talones, elevación evidente o sostenida de estos o casos en los que el modelo de pose no detecte adecuadamente los puntos anatómicos requeridos. Una elevación breve y espontánea del talón será registrada como observación técnica y motivará la repetición del intento antes de determinar la exclusión del registro. Esta delimitación se apoya en Bae et al. \[24], Armitano-Lago et al. \[21], Ohmura et al. \[36] y Needham et al. \[45].

La exclusión por soportes externos o elevación evidente y sostenida de los talones será determinada manualmente por el investigador a partir del protocolo de captura y del Instrumento 1. No deberá describirse como una detección o decisión automática del sistema. La capacidad tecnológica de segmentar videos con varias repeticiones se conservará para el uso operativo del prototipo; sin embargo, dichos videos no integrarán la muestra formal de evaluación salvo que cada repetición sea tratada como un registro independiente, conserve un código trazable y cumpla por separado los criterios de calidad.

## 8.3 Muestra

La muestra estará constituida por 75 videos válidos de sentadilla bilateral, equivalentes a 75 repeticiones completas elegibles. Durante la captura controlada se planificarán 15 registros con intención de representar cada uno de los cuatro patrones evaluados —inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y diferencia bilateral de alineación de rodillas— y 15 registros de contraste sin un patrón intencional. Esta planificación asegura diversidad técnica, pero no asigna por anticipado la condición positiva o negativa: la etiqueta de referencia será establecida posteriormente por los evaluadores expertos. Dado que los patrones no son mutuamente excluyentes, una misma repetición podrá recibir más de una clasificación positiva en la referencia final.

Cada video formal contendrá una sola repetición completa, capturada en vista anterior dentro del plano frontal, procesable por el sistema y revisable por los evaluadores. En consecuencia, el análisis de cuatro patrones por repetición podrá generar hasta 300 pares repetición-patrón antes de excluir resultados no concluyentes o evidencia insuficiente. Los videos con varias repeticiones podrán emplearse en pruebas de funcionamiento del prototipo, pero no sustituirán la unidad formal definida para la evaluación de desempeño.

Dado que la población operativa del estudio está formada por registros audiovisuales seleccionados bajo criterios técnicos y no por una población estadística plenamente enumerada, no se plantea en esta etapa un cálculo muestral probabilístico clásico. En su lugar, se adopta un tamaño de muestra metodológicamente manejable y suficiente para sustentar pruebas de funcionamiento, detección y concordancia, sin perder coherencia con el alcance de la tesis.

## 8.4 Muestreo

El muestreo será no probabilístico e intencional. Esta estrategia se elige porque cada registro será seleccionado según el cumplimiento del protocolo, la necesidad de cubrir los cuatro patrones y los criterios técnicos de calidad, visibilidad corporal, vista anterior dentro del plano frontal, ausencia de carga externa, ejecución sin soportes elevados debajo de los talones, apoyo plantar observable y estimación estable de pose. Para la muestra formal se seleccionará una repetición completa por video. La verificación de las condiciones relacionadas con el apoyo de los talones será realizada manualmente por el investigador mediante el protocolo de captura y el Instrumento 1, y no constituirá una función automática del sistema. La prioridad no será la representatividad estadística poblacional, sino disponer de registros trazables y suficientemente diversos para diseñar, probar y evaluar el prototipo.

La literatura metodológica del campo muestra que la calidad del protocolo de captura incide directamente sobre la validez del análisis del movimiento sin marcadores. Por ello, la elección de un muestreo intencional es coherente con antecedentes como Lopes et al. \[39], Kim et al. \[32], Ohmura et al. \[36] y Needham et al. \[45].

## 8.5 Técnicas e instrumentos

La técnica principal de recolección de datos será el análisis estructurado de video, complementado por registro técnico del procesamiento computacional y evaluación observacional experta. En coherencia con la matriz de operacionalización, los instrumentos se han reorganizado para que cada uno mida dimensiones e indicadores concretos del estudio, evitando presentar anexos como referencias conceptuales aisladas.

El primer instrumento será una ficha maestra de registro técnico, factibilidad analítica y disponibilidad de puntos anatómicos clave. Esta ficha integrará, en una sola hoja de trabajo, la identificación del video, fecha de registro, fuente, condiciones de captura, resolución, iluminación, visibilidad corporal, presencia de oclusiones, cumplimiento de la vista anterior dentro del plano frontal, validez del registro para procesamiento y disponibilidad observable de los puntos anatómicos clave relevantes. También permitirá registrar manualmente las condiciones de ejecución que puedan comprometer la comparabilidad del análisis, como el uso de discos, cuñas u otros soportes debajo de los talones, la elevación evidente o sostenida de estos y la pérdida de visibilidad de los segmentos corporales requeridos.

Para que un registro sea aceptado, la sentadilla deberá ejecutarse sobre una superficie plana, sin soportes externos debajo de los talones y procurando mantener el contacto de ambos talones con el suelo. Cuando el investigador identifique la presencia de soportes externos o una elevación evidente y sostenida de los talones, se solicitará repetir la grabación; si ello no fuera posible, el registro no será incorporado a la muestra analítica principal. De igual manera, los videos capturados fuera del plano frontal, que presenten baja calidad visual o que incumplan otras condiciones críticas del protocolo serán considerados no aptos para el análisis. Estas verificaciones serán realizadas mediante el protocolo de captura y el Instrumento 1, y no constituirán funcionalidades automáticas del sistema. De esta manera, se busca reducir la ambigüedad en la selección de casos y fortalecer la trazabilidad metodológica del proceso de inclusión y exclusión.

El segundo instrumento será una ficha de procesamiento computacional, segmentación temporal, variables biomecánicas y criterios interpretables. Esta ficha registrará, para cada video aceptado, el estado del procesamiento, fotogramas declarados y decodificados, porcentaje de fotogramas procesados correctamente, fotogramas válidos, promedio de puntos anatómicos clave detectados por fotograma, repeticiones completas, eventos temporales, validez del fotograma de máxima profundidad, valores biomecánicos y salidas interpretativas. Para el indicador de cobertura se considerarán 13 puntos: nariz y referencias bilaterales de hombros, caderas, rodillas, tobillos, talones y puntas de los pies. Un punto será contabilizado cuando presente coordenadas 2D finitas y visibilidad igual o superior a 0,5. Cada patrón será evaluado mediante una regla independiente, por lo que una repetición podrá presentar ninguno, uno o varios patrones simultáneamente. Cuando la evidencia sea insuficiente o el valor se ubique en una banda ambigua, se registrará una clasificación no concluyente. Así, el instrumento conservará la relación entre calidad de entrada, evento temporal, valor calculado, regla aplicada y resultado.

El tercer instrumento será una ficha comparativa de evaluación experta y sistema. En ella se registrará, por cada video y repetición formal, la clasificación emitida por dos evaluadores expertos y por el sistema respecto de inclinación lateral del tronco, desplazamiento lateral de pelvis, valgo dinámico visible y diferencia bilateral de alineación de rodillas. Los patrones serán valorados de manera independiente; por ello, identificar uno no excluirá la presencia simultánea de otros. Si se incorpora un tercer evaluador, la misma estructura permitirá integrar su valoración y fortalecer la referencia final.

De manera complementaria, los instrumentos serán sometidos a validación por dos o tres expertos vinculados con visión por computadora, ingeniería aplicada o análisis del movimiento, utilizando la ficha institucional de validación por juicio de expertos proporcionada por la universidad. Esta validación revisará claridad, pertinencia, coherencia con dimensiones e indicadores y suficiencia de las cabeceras planteadas. El producto esperado será la aprobación formal de los instrumentos antes de su uso definitivo, con observaciones y firma de los expertos validadores. Su función no será registrar videos ni clasificaciones del movimiento, sino asegurar previamente la calidad metodológica de las fichas que serán aplicadas en el estudio.

Como parte del análisis de datos, el investigador construirá una base consolidada interna derivada del Instrumento 3. Esta base se utilizará exclusivamente para comparar la referencia experta final con la salida del sistema y dejar trazabilidad de coincidencias, discrepancias y observaciones; no se considerará un instrumento adicional de recolección. Cada patrón de cada repetición constituirá un registro analítico independiente. Esta organización permitirá calcular métricas específicas para tronco, pelvis, valgo y diferencia bilateral, evitando que el acierto en una categoría compense una clasificación incorrecta en otra.

La referencia experta se construirá inicialmente con dos evaluadores con perfil de entrenador o profesional con experiencia en análisis del movimiento. Cada uno revisará de manera independiente y ciega los videos. Si ambos coinciden, la clasificación se adoptará directamente; si discrepan, se realizará una revisión documentada o se incorporará un tercer evaluador. Cuando participen tres evaluadores, se aplicará mayoría absoluta. Si no fuera posible resolver una discrepancia, el par repetición-patrón quedará como no concluyente y no ingresará a las métricas binarias. Este procedimiento es consistente con Falk et al. \[10], Gomes et al. \[11], Ressman et al. \[12], Whatman et al. \[44] y Nutarelli et al. \[13].

### Procedimiento de aplicación

El procedimiento se desarrollará mediante las siguientes etapas secuenciales:

1. **Aprobación ética y preparación de la captura.** Antes de recolectar datos se obtendrán la aprobación ética, la autorización del establecimiento y el consentimiento informado. Se asignará un código anónimo al participante y al video. El investigador explicará la ejecución, comprobará la vista anterior dentro del plano frontal, la iluminación, la ausencia de carga externa y soportes bajo los talones, y registrará en el Instrumento 1 los datos técnicos y las incidencias observables. Para la muestra formal se grabará una sola repetición completa por video; si la ejecución o la captura incumplen el protocolo, se solicitará repetirla antes de aceptar el registro.

2. **Registro digital y almacenamiento del caso.** Mediante una cuenta con rol de investigador se registrarán los datos del caso y se cargará el video en el prototipo web. El sistema conservará códigos, metadatos, fecha, estado de procesamiento y archivos asociados en una base de datos y almacenamiento privado con control de acceso. El rostro se anonimizará en las copias destinadas a revisión o difusión. Esta etapa trasladará al sistema los campos del Instrumento 1 y mantendrá trazabilidad entre el video original, el caso y sus resultados.

3. **Decodificación y estimación de pose 2D.** El motor de análisis recibirá el video mediante una interfaz de programación de aplicaciones. OpenCV abrirá el archivo, leerá sus propiedades y decodificará los fotogramas; cada imagen se convertirá del orden de color BGR a RGB para su procesamiento mediante MediaPipe Pose. El modelo estimará los puntos corporales y el sistema conservará 13 referencias relevantes. Por fotograma se registrarán coordenadas normalizadas, visibilidad, puntos utilizables y estado de validez. Se distinguirá entre continuidad técnica de lectura, medida por fotogramas procesados correctamente, y suficiencia anatómica, medida por la disponibilidad de los puntos críticos.

4. **Control de calidad y segmentación temporal.** A partir del punto medio vertical de ambas caderas se construirá una señal temporal. Los huecos breves se interpolarán solo para mantener continuidad, sin modificar la validez original de los fotogramas; posteriormente se aplicarán una mediana móvil y un promedio móvil centrados para reducir valores atípicos y variaciones pequeñas. Las repeticiones se delimitarán mediante máximos locales, prominencia mínima adaptativa, separación temporal y validación de recuperación entre máximos. Para cada ciclo se identificarán inicio, descenso, máxima profundidad, ascenso y cierre. Una repetición será elegible cuando alcance la proporción mínima de fotogramas válidos y su fotograma de máxima profundidad contenga las referencias requeridas. Las repeticiones no elegibles se conservarán como evidencia técnica, pero no producirán clasificaciones formales.

5. **Cálculo biomecánico.** En el reposo inicial se estimará `W0`, definido como la mediana del ancho horizontal de hombros en fotogramas válidos. Durante la repetición se conservarán las series temporales y, en el fotograma de máxima profundidad, se calcularán la inclinación lateral del tronco, el desplazamiento lateral de pelvis, la desviación medial de cada rodilla y la diferencia bilateral de alineación de rodillas. Las medidas normalizadas por `W0` permitirán expresar desplazamientos relativos a una referencia corporal estable dentro del video.

6. **Aplicación de criterios interpretables.** Cada variable será comparada con umbrales provisionales versionados y clasificada de manera independiente como ausente, no concluyente o presente. Cuando corresponda, se conservará la dirección izquierda o derecha, la bilateralidad o el predominio. La salida no consistirá únicamente en una etiqueta: incluirá el valor firmado, la magnitud, la unidad, el umbral aplicado, el fotograma de referencia y la explicación geométrica. La presencia de un patrón no excluirá otros patrones en la misma repetición.

7. **Implementación y visualización del prototipo.** El motor de análisis en Python se expondrá mediante una API y se integrará con una interfaz web. El prototipo organizará el video original, videos e imágenes superpuestos, eventos temporales, gráficos interactivos, tablas normalizadas, reglas y reportes descargables. La persistencia de casos, cuentas y archivos permitirá revisar posteriormente el mismo resultado y mantener su trazabilidad. El detalle de bibliotecas o componentes de interfaz se documentará como arquitectura técnica del software; metodológicamente, lo relevante será que todas las unidades recorran el mismo flujo reproducible.

8. **Evaluación experta mediante roles diferenciados.** El investigador podrá registrar casos, consultar los resultados automáticos, asignar cada video a un máximo de tres expertos, consolidar la referencia final, cerrar el caso y exportar los instrumentos y reportes. Los expertos accederán con cuentas separadas y clasificarán de forma independiente los cuatro patrones sin visualizar previamente la salida del sistema. Para cada respuesta podrán registrar confianza y una observación. Una vez cerrada la referencia final, se habilitará la comparación entre el juicio humano y el sistema.

9. **Evaluación del desempeño y generación del informe.** Las clasificaciones concluyentes se integrarán en la base consolidada. Se construirán matrices de confusión por patrón y se calcularán exactitud, precisión, sensibilidad, especificidad y puntaje F1. Se estimará Kappa de Cohen entre el sistema y la referencia final, y Kappa de Fleiss entre tres expertos cuando corresponda. El prototipo generará un reporte trazable con resultados por repetición, coincidencias, discrepancias y métricas acumuladas.

10. **Extensión prevista para usuarios finales.** Como alcance funcional posterior del prototipo se implementará un tercer rol para usuarios no evaluadores. Estas personas podrán registrarse mediante correo electrónico o un proveedor de identidad, consultar la guía de grabación, cargar un video con una o varias repeticiones y recibir resultados automáticos acompañados de recomendaciones generales de carácter educativo. Este rol no formará parte de la construcción de la referencia experta ni de la evaluación formal de desempeño de la tesis. Sus resultados no constituirán diagnóstico, prescripción ni sustitución de una evaluación profesional, y su liberación requerirá controles de privacidad, consentimiento, calidad y comunicación de incertidumbre.

La ficha institucional de validación por juicio de expertos operará antes de la aplicación definitiva de los instrumentos. En conjunto, el Instrumento 1 medirá la admisibilidad y trazabilidad de la entrada; el Instrumento 2 documentará el procesamiento, la segmentación, los cálculos y las salidas; y el Instrumento 3 sustentará la comparación experta-sistema. Esta correspondencia vincula directamente el procedimiento con las dimensiones y objetivos del estudio.

## 8.6 Análisis de datos

El análisis de datos combinará técnicas descriptivas con métricas de evaluación del desempeño. Del Instrumento 1 se obtendrá la caracterización técnica y la trazabilidad de inclusión o exclusión; del Instrumento 2, la información de decodificación, calidad, segmentación, variables y reglas; y del Instrumento 3, las clasificaciones de expertos, sistema y referencia final. La base consolidada utilizará como unidad analítica cada par repetición-patrón, manteniendo el código del video para conservar trazabilidad.

En una primera etapa se describirán los registros aceptados y descartados, motivos de exclusión, condiciones de captura y procesamiento. En una segunda se resumirán el porcentaje de fotogramas procesados correctamente, porcentaje global de fotogramas válidos, promedio de puntos detectados, repeticiones delimitadas, porcentaje de fotogramas válidos por repetición, validez del fotograma de máxima profundidad y duración de las fases. El promedio de puntos se calculará sobre 13 referencias y todos los fotogramas decodificados, mientras que la puerta de validez dependerá de las referencias críticas definidas y no del promedio por sí solo.

En una tercera etapa se describirán las series biomecánicas y los valores obtenidos en máxima profundidad mediante promedio, mediana, mínimo, máximo, rango y desviación estándar cuando corresponda. Para la clasificación se utilizará exclusivamente el valor del fotograma de máxima profundidad de cada repetición elegible; las series completas se conservarán como evidencia y no se promediarán para decidir la presencia del patrón. Se calcularán frecuencias de estados y lateralidades, reconociendo que una repetición puede presentar varias salidas positivas.

En una cuarta etapa se establecerá la referencia final. La coincidencia entre dos evaluadores se adoptará directamente. Las discrepancias se resolverán mediante revisión documentada o incorporación de un tercer evaluador; con tres clasificaciones se aplicará mayoría absoluta. Si no existe resolución, el par será no concluyente. La evaluación ciega impedirá que los expertos conozcan la salida automática antes de enviar sus respuestas.

A partir de matrices binarias independientes para los cuatro patrones se calcularán exactitud, precisión, sensibilidad, especificidad y puntaje F1 por patrón, además de un resumen macro. Kappa de Cohen medirá la concordancia entre el sistema y la referencia final; Kappa de Fleiss describirá la concordancia entre tres expertos cuando corresponda. Los casos no concluyentes o con evidencia insuficiente se contabilizarán y excluirán del denominador de las métricas binarias, informando cuántos pares fueron retirados. Este esquema es coherente con Kim y Park \[42], Bae et al. \[24], Ressman et al. \[12], Whatman et al. \[44] y Nutarelli et al. \[13].

Los umbrales biomecánicos, las ventanas de suavizado, la prominencia mínima y las reglas de calidad se tratarán como parámetros técnicos versionados. Los valores iniciales son provisionales y deberán contrastarse con la muestra y la referencia experta; por ello, no se interpretarán como puntos de corte clínicos universales. Las conclusiones se restringirán a videos monoculares 2D, vista anterior frontal, sentadilla sin carga y condiciones de captura definidas. No se inferirán causas anatómicas, patologías, rotaciones tridimensionales, distribución real de cargas ni diagnósticos. El sistema tampoco verificará automáticamente el contacto efectivo de los talones con el suelo ni la presencia de soportes, condiciones controladas manualmente por el protocolo y el Instrumento 1.

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

\[46] A. Sobrino-Santos et al., "Non-Contact Platform for the Assessment of Physical Function in Older Adults: A Pilot Study," Technologies, vol. 13, no. 6, art. 225, 2025, doi: 10.3390/technologies13060225.

# 12. ANEXOS

## Anexo 1

**Matriz de operacionalización de variables**

| **Variables** | **Definición conceptual** | **Definición operacional** | **Dimensiones** | **Indicadores** | **Unidad de medida** | **Técnicas/Instrumentos** |
| --- | --- | --- | --- | --- | --- | --- |
| Variable 1: Sistema de visión por computadora basado en estimación de pose 2D y criterios biomecánicos interpretables | Sistema computacional que transforma videos de sentadilla bilateral en puntos 2D, eventos temporales, variables geométricas, clasificaciones interpretables y reportes trazables. | Se observará mediante el registro del caso, control de calidad, estimación de pose, segmentación temporal, cálculo biomecánico, aplicación de reglas y generación de resultados en el prototipo. | 1) Estimación de pose 2D | Promedio de puntos anatómicos clave detectados por fotograma; porcentaje de fotogramas válidos; porcentaje de fotogramas procesados correctamente. | Puntos por fotograma, máximo 13; porcentaje. | Técnica: análisis estructurado de video. Instrumentos 1 y 2. |
|  |  |  | 2) Segmentación temporal de la sentadilla | Repeticiones completas detectadas; porcentaje de fotogramas válidos por repetición; validez del fotograma de máxima profundidad; duración de descenso, ascenso y ciclo. | Conteo; porcentaje; sí/no; segundos. | Técnica: procesamiento de señales derivadas de video. Instrumento 2. |
|  |  |  | 3) Extracción y cálculo de variables biomecánicas observables | Inclinación lateral del tronco; desplazamiento lateral de pelvis; desviación medial de rodilla izquierda y derecha; diferencia bilateral de alineación de rodillas. | Grados; porcentaje de `W0`. | Técnica: análisis geométrico 2D. Instrumento 2. |
|  |  |  | 4) Aplicación de criterios biomecánicos interpretables | Estado por patrón; lateralidad o predominio; umbral aplicado y trazabilidad del resultado. | Nominal; grados o porcentaje según variable. | Técnica: reglas interpretables. Instrumento 2. |
|  |  |  | 5) Procesamiento y generación de resultados | Registro y carga del caso; procesamiento completo; generación de reporte; visualización y recuperación de resultados. | Cumple/no cumple; porcentaje. | Técnica: prueba funcional del prototipo. Instrumento 2. |
| Variable 2: Desempeño técnico del sistema en la clasificación de patrones observables durante la sentadilla bilateral | Rendimiento del sistema al clasificar cuatro patrones por repetición, comparado con una referencia experta final. | Se medirá mediante matrices de confusión independientes por patrón y análisis de concordancia, excluyendo y contabilizando los pares no concluyentes. | 1) Desempeño de clasificación por patrón | Exactitud; precisión; sensibilidad; especificidad; puntaje F1 por patrón y macro. | Proporción o porcentaje. | Técnica: observación experta comparativa. Instrumento 3 y base consolidada de análisis. |
|  |  |  | 2) Concordancia de las clasificaciones | Kappa de Cohen entre sistema y referencia final; Kappa de Fleiss entre tres expertos, cuando corresponda. | Índice de concordancia. | Técnica: análisis de concordancia. Instrumento 3 y base consolidada de análisis. |

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

**Instrumento 2. Ficha de procesamiento computacional, segmentación temporal, variables biomecánicas y criterios interpretables**

Uso: registrar la salida del sistema para cada video válido.

Esta hoja debe ser llenada por el investigador a partir de la salida automática del software. No corresponde al juicio del evaluador experto.

| Identificación | Procesamiento y calidad | Segmentación temporal | Variables biomecánicas en máxima profundidad | Criterios interpretables | Salida final |
| --- | --- | --- | --- | --- | --- |
| Código de video y repetición | Estado; fotogramas declarados y decodificados; fotogramas procesados correctamente y porcentaje; fotogramas válidos y porcentaje; promedio de puntos detectados | Inicio, máxima profundidad y cierre; porcentaje válido de la repetición; validez del fotograma de máxima profundidad; duración | Inclinación lateral del tronco; desplazamiento lateral de pelvis; desviación medial de rodilla izquierda; desviación medial de rodilla derecha; diferencia bilateral de alineación | Estado, dirección o predominio y umbral aplicado para cada patrón | Reporte, gráficos, imágenes y videos superpuestos disponibles |
|  |  |  |  |  |  |

| Campo | Codificación sugerida |
| --- | --- |
| Estado de procesamiento | Exitoso / parcial / fallido |
| Repetición | Código trazable, por ejemplo `caso-01-repeticion-1`; para la muestra formal existirá una repetición por video |
| Inclinación lateral del tronco | Valor firmado en grados; la magnitud define el estado y el signo informa la dirección |
| Desplazamiento lateral de pelvis | Valor firmado como porcentaje de `W0`; la magnitud define el estado y el signo informa la dirección |
| Desviación medial de cada rodilla | Porcentaje de `W0`; positivo indica desviación medial y negativo desplazamiento lateral |
| Diferencia bilateral de alineación de rodillas | Diferencia absoluta entre las desviaciones de ambas rodillas, expresada como porcentaje de `W0` |
| Tipo de patrón detectado | Tronco / pelvis / valgo / diferencia bilateral; pueden coexistir varios patrones |
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
| Fuente | `landmarks.csv`, `frame_quality.csv` y `pose_summary.json` |
| Aclaración | Describe cobertura; la validez depende de la disponibilidad de las referencias críticas requeridas |

## Anexo 4

**Instrumento 3. Ficha comparativa de evaluación experta y sistema**

Uso: comparar, por video y repetición formal, las clasificaciones de los evaluadores expertos frente al sistema.

Cada experto completará únicamente la fila asociada a su cuenta. Las filas del sistema y de referencia final serán completadas automáticamente o por el investigador después del cierre de la evaluación ciega. El formato longitudinal evita duplicar cabeceras y permite relacionar cada respuesta con su autor y estado.

| Número | Código del video/repetición | Fuente de clasificación | Tronco | Pelvis | Valgo | Diferencia bilateral de alineación de rodillas |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  | Evaluador 1 |  |  |  |  |
| 1 |  | Evaluador 2 |  |  |  |  |
| 1 |  | Evaluador 3, si participa |  |  |  |  |
| 1 |  | Sistema computacional |  |  |  |  |
| 1 |  | Referencia experta final |  |  |  |  |

| Patrón | Codificación sugerida |
| --- | --- |
| Tronco | Ausente / izquierda / derecha / no concluyente |
| Pelvis | Ausente / izquierda / derecha / no concluyente |
| Valgo | Ausente / izquierdo / derecho / bilateral / no concluyente |
| Diferencia bilateral de alineación de rodillas | Ausente / predominio izquierdo / predominio derecho / presente sin predominio claro / no concluyente |

Regla de consolidación: la referencia final será completada por el investigador después de cerrar la evaluación ciega. Con dos evaluadores se adoptará la coincidencia directa; una discrepancia requerirá revisión documentada o incorporación de un tercer evaluador. Con tres evaluadores se aplicará mayoría absoluta. Si no se obtiene una referencia resoluble, el patrón se registrará como no concluyente y se excluirá de las métricas binarias.
