# RAG Analysis Levels And Tooling

## Objetivo

Definir cómo evoluciona la capa de análisis de video del proyecto y qué herramientas siguen vigentes en cada nivel.

La idea central es esta:

- no construir una capa demasiado compleja para todos los videos desde el inicio
- empezar con un pipeline simple y suficiente
- escalar a pipelines más ricos cuando el tipo de video lo justifique

## Respuesta corta

Sí, las herramientas base que ya habíamos definido siguen sirviendo.

Para la capa simple y para buena parte del MVP siguen siendo válidas:

- `fast-whisper`
- `Tesseract OCR`
- `PySceneDetect`
- modelos de embeddings
- keyframe extraction con `ffmpeg`

No estamos descartando ese stack. Lo seguimos usando como base.

## Niveles de análisis

## Nivel 1. Pipeline liviano

Es el pipeline por defecto para:

- Shorts educativos
- videos breves y relativamente directos
- lotes grandes donde importa costo y velocidad

### Objetivo

Extraer suficiente conocimiento para RAG sin pagar una complejidad innecesaria.

### Herramientas recomendadas

- `fast-whisper` para ASR
- `ffmpeg` para extracción de audio y keyframes
- `Tesseract` para OCR
- `PySceneDetect` para cortes iniciales
- embeddings locales o remotos según configuración

### Salida esperada

- transcript
- OCR
- keyframes
- segmentos cortos
- `retrieval_text`
- topics
- keywords
- cues básicos
- ejercicios mencionados
- tests o retests cuando aparezcan

### Cuándo alcanza

- un short tiene una sola idea principal
- hay uno o pocos ejercicios
- la descripción visual es útil pero no extremadamente compleja
- la mayor parte del valor está en lo dicho + una demostración simple

## Nivel 2. Pipeline enriquecido

Es una extensión del Nivel 1 para:

- videos de 5 a 30 minutos
- videos con varios subtemas
- videos con múltiples ejercicios o fases

### Objetivo

Mantener el mismo stack base, pero con más estructura temporal y semántica.

### Herramientas

Se mantienen las del Nivel 1 y se añade:

- mejor alineación entre transcript, escenas y OCR
- mejores reglas de segmentación
- agrupación por bloques temáticos
- enriquecimiento visual opcional
- análisis estructurado sobre la evidencia extraída

### Salida esperada

- segmentos más coherentes
- bloques temáticos
- mejor separación entre concepto, error común, test, ejercicio y retest
- conocimiento estructurado en JSON listo para persistencia y retrieval

### Cuándo usarlo

- el video ya no es un short simple
- hay varias demostraciones
- hay explicaciones largas entre ejercicios
- hace falta preservar mejor el contexto
- queremos aproximarnos a la calidad de Gemini sin depender de Gemini

## Nivel 3. Pipeline avanzado

Este nivel es para videos donde la estructura del procedimiento importa mucho o donde la evidencia visual pura aporta demasiado valor para conformarnos con la ruta estándar.

### Casos típicos

- tutoriales largos
- videos con varios pasos dependientes
- videos donde hay que reconstruir una especie de "skill"
- material que luego quieras convertir en protocolos detallados o assets más ricos
- videos donde la ejecución visual es más importante que la voz o el OCR

## Ruta futura: `Skill_Seekers`

`Skill_Seekers` no debería ser el pipeline base del sistema.

### Qué resuelve bien

- videos más largos
- estructura procedural
- timelines ricos
- transformación de video a artefacto tipo "skill"

### Por qué no es la mejor opción actual

- añade complejidad que hoy no necesitamos para Shorts y videos educativos relativamente directos
- está más orientado a convertir tutoriales en skills que a construir evidencia limpia para RAG
- no reemplaza la necesidad de trazabilidad por segmentos y evidencia base

### Cuándo lo usaríamos

- videos de 20 a 30 minutos o más
- material con capítulos o subprocesos muy definidos
- protocolos largos que queramos convertir en un artefacto procedural
- lotes pequeños donde valga la pena pagar más procesamiento por video

### Limitación en este proyecto

No está especialmente diseñado para biomecánica visual fina. Por eso no conviene adoptarlo como núcleo universal.

## Ruta futura: modelos de video directos

También existe una ruta futura distinta a `Skill_Seekers`:

- usar modelos multimodales o `video-text-to-text` directamente sobre el video
- pedirles el conocimiento estructurado final sin pasar por toda la extracción local

### Por qué no es la mejor opción actual

Hoy no conviene adoptarla como camino principal por estas razones:

- los videos del proyecto mezclan voz, texto en pantalla y demostración corporal
- muchos modelos de video todavía tienen una historia más madura para video que para audio + video bien integrados
- la extracción local actual ya recupera gran parte de la señal útil con menor costo
- separar `extracción -> análisis` nos da más trazabilidad, reindexación y control de calidad
- para RAG es mejor conservar transcript, OCR, keyframes y segmentos como evidencia explícita

### Qué haríamos si fuéramos directo al modelo

La ruta directa se parecería más a Gemini:

- `video crudo -> modelo multimodal -> JSON estructurado`

Eso es atractivo, pero hoy tiene varios tradeoffs:

- mayor costo computacional
- menor reproducibilidad local
- más dependencia de infraestructura externa
- menos control fino sobre qué parte del video originó cada pieza de conocimiento

### Cuándo sí tendría sentido

Podría activarse a futuro cuando:

- el transcript sea pobre o inexistente
- el valor del video esté principalmente en la demostración visual
- el ejercicio tenga varias fases difíciles de describir solo con transcript + OCR
- tengamos videos largos donde una segunda opinión multimodal mejore mucho la calidad

### Relación con Hugging Face

Esta ruta futura puede implementarse con modelos multimodales alojados o autoalojados desde Hugging Face.

No la descartamos.

Simplemente no la colocamos hoy como primera opción del proyecto.

## ¿Se cambia el stack base?

No.

La respuesta concreta es:

- `fast-whisper`: se mantiene
- `Tesseract`: se mantiene
- `PySceneDetect`: se mantiene
- modelos de embeddings: se mantienen

Lo que cambia no es el stack base, sino cuánta profundidad le pedimos al pipeline según el video.

## Embeddings

Los embeddings siguen siendo necesarios en todos los niveles porque el objetivo final sigue siendo RAG.

La decisión no es "usar o no embeddings", sino:

- qué texto alimentar al embedding
- cuán buenos son los segmentos
- cuánta metadata acompaña a cada segmento

## Regla de decisión

### Usar Nivel 1

Cuando el video:

- es corto
- tiene una idea central
- contiene pocos ejercicios
- se entiende razonablemente bien con transcript + keyframes + OCR

### Usar Nivel 2

Cuando el video:

- es más largo
- mezcla varios conceptos
- necesita mejor chunking
- necesita mejor separación de secciones
- necesita análisis estructurado más rico a partir de la evidencia

### Usar Nivel 3

Cuando el video:

- es largo y procedural
- necesita una estructura tipo skill
- requiere una extracción más rica del timeline
- depende demasiado de interpretación visual directa

## Recomendación actual del proyecto

La estrategia correcta hoy es:

1. mantener el stack base ya definido
2. implementar primero el Nivel 1
3. diseñar el código para crecer a Nivel 2
4. usar análisis estructurado sobre la evidencia extraída como camino principal del conocimiento
5. dejar `Skill_Seekers` y los modelos de video directos como rutas opcionales de Nivel 3

## Decisión final

No estamos reemplazando las herramientas ya elegidas para la capa simple.

Estamos haciendo algo mejor:

- conservar un pipeline base razonable
- permitir que el sistema escale a videos más largos
- usar herramientas más complejas solo cuando aporten valor real

La estrategia actual queda así:

1. `Nivel 1`: extracción local como camino base
2. `Nivel 2`: análisis estructurado sobre la evidencia extraída
3. `Nivel 3`: rutas avanzadas opcionales

Dentro del Nivel 3 entran:

- `Skill_Seekers`
- modelos de video directos
- Gemini u otra ruta premium multimodal
