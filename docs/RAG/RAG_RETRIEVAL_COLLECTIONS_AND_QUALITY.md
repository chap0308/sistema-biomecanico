# RAG Retrieval Collections And Quality

## Objetivo

Dejar claro:

- qué tipo de información vive en cada colección de Qdrant
- cómo se relaciona eso con Supabase
- cómo debería funcionar la consulta final del sistema
- qué significa consultar con calidad `low`, `medium` o `high`

Este documento responde a una duda clave del proyecto:

`ya tenemos videos procesados y conocimiento estructurado, ¿cómo se consulta eso de forma útil para síntomas, deficiencias y diagnósticos?`

## Idea central

Hoy el sistema ya produce dos capas distintas de información para retrieval:

1. evidencia extraída del video
2. conocimiento derivado del video

Las dos son útiles, pero no sirven exactamente para lo mismo.

## Colección `video_segments_v1`

Esta colección contiene la evidencia base proveniente del video.

Cada punto indexado representa un segmento temporal del contenido, por ejemplo:

- del segundo `0.0` al `12.5`
- transcript de ese tramo
- OCR de ese tramo
- topics
- keywords
- `retrieval_text`

### Qué representa

Representa lo que el video dijo, mostró o dejó escrito en un fragmento concreto.

### Para qué sirve mejor

- encontrar evidencia puntual
- recuperar frases o explicaciones del video
- ubicar timestamps
- respaldar una respuesta con base más fiel al contenido original

### Ejemplos de uso

- "¿en qué parte habla de pronación?"
- "¿qué decía sobre el contacto del talón?"
- "muéstrame la evidencia que relaciona este ejercicio con el arco del pie"

### Limitación

No está pensado para responder de forma directa con tratamiento estructurado.

Puede contener:

- ruido de ASR
- ruido de OCR
- repeticiones
- explicación cruda todavía no consolidada

## Colección `video_knowledge_units_v1`

Esta colección contiene conocimiento derivado y estructurado.

Cada punto indexado representa una unidad de conocimiento ya interpretada, por ejemplo:

- un ejercicio correctivo
- un patrón de compensación
- un punto educativo
- una advertencia
- una recomendación

### Qué representa

Representa una pieza de conocimiento útil para responder preguntas clínicas o educativas.

### Para qué sirve mejor

- responder con ejercicios o protocolos
- mapear un diagnóstico a tratamiento
- explicar una deficiencia en lenguaje más útil
- devolver recomendaciones más directas

### Ejemplos de uso

- "¿qué ejercicio puede ayudar con plantar fasciitis?"
- "¿qué protocolo hay para mejorar el contacto del pie?"
- "¿qué cues hay para este ejercicio?"

### Limitación

Depende de la calidad de la capa 2.

Si el análisis estructurado se equivoca, la unidad de conocimiento también arrastra ese error.

## Relación entre ambas colecciones

Las dos no compiten entre sí.

Cumplen roles distintos:

- `video_segments_v1` = evidencia
- `video_knowledge_units_v1` = conocimiento útil

La mejor arquitectura de consulta no es elegir solo una para siempre, sino decidir cuánto apoyo de evidencia queremos según el caso.

## Qué papel juega Supabase aquí

Supabase sigue siendo el sistema de registro.

Debe guardar:

- `rag_sources`
- `rag_assets`
- `rag_segments`
- `rag_knowledge_drafts`
- `rag_knowledge_units`

Qdrant no reemplaza eso.

Qdrant solo guarda lo necesario para recuperar rápido.

Cuando una respuesta necesita más contexto, trazabilidad o referencias, el flujo correcto es:

```text
pregunta
-> retrieval en Qdrant
-> obtener source_id / segment_id / draft_id
-> ampliar contexto desde Supabase
-> redactar respuesta final
```

## Tipos de consultas esperadas en este proyecto

### 1. Consulta por síntoma o limitación funcional

Ejemplos:

- "no puedo tomar mi omóplato contrario con mi brazo derecho"
- "no puedo elevar mi brazo derecho completamente"
- "siento que mi hombro se traba al subir el brazo"

Estas consultas suelen venir en lenguaje no técnico.

El sistema debe:

- traducir la descripción funcional a posibles patrones
- recuperar conocimiento relacionado
- responder sin asumir que el usuario conoce anatomía

### 2. Consulta por diagnóstico o etiqueta clínica

Ejemplos:

- "escápula alada"
- "Swayback"
- "inclinación pélvica anterior"
- "Pie plano funcional con colapso medial en el lado derecho"
- "Disquinesia Escapular Derecha Tipo II"

Estas consultas suelen venir de un fisioterapeuta o alguien con más conocimiento técnico.

El sistema debe:

- recuperar conocimiento más específico
- priorizar ejercicios, mecanismos y advertencias
- responder con mayor densidad técnica

## Calidad de respuesta

Sí conviene modelarlo como una variable explícita.

Una forma razonable es:

- `low`
- `medium`
- `high`

Esto no cambia la base de datos.

Cambia cuánta recuperación y validación hacemos antes de responder.

## Calidad `low`

### Qué consulta

- solo `video_knowledge_units_v1`

### Qué hace

- busca pocas unidades de conocimiento
- arma una respuesta directa
- mínima verificación con evidencia cruda

### Ventajas

- rápido
- barato
- útil para exploración o prototipos

### Desventajas

- menor respaldo
- más riesgo de responder con una unidad derivada que no esté bien validada

### Cuándo usarlo

- debugging
- prototipo interno
- consultas de baja importancia

### Recomendación

No lo pondría como modo principal para usuarios finales.

## Calidad `medium`

### Qué consulta

- primero `video_knowledge_units_v1`
- luego usa `video_segments_v1` solo para ampliar o verificar parcialmente

### Qué hace

- recupera conocimiento útil
- busca evidencia de apoyo cuando la respuesta lo necesita
- mantiene buen balance entre costo, velocidad y solidez

### Ventajas

- respuestas bastante útiles
- mejor respaldo que `low`
- menor costo que `high`

### Desventajas

- no siempre explora toda la evidencia disponible

### Cuándo usarlo

- modo general por defecto
- consultas de usuarios no técnicos
- respuestas educativas o de primera orientación

### Recomendación

Este debería ser el valor por defecto del sistema.

## Calidad `high`

### Qué consulta

- `video_knowledge_units_v1`
- `video_segments_v1`
- combinación o reranking de ambas

### Qué hace

- recupera conocimiento útil y evidencia cruda al mismo tiempo
- compara ambas capas
- prioriza respuestas con mayor trazabilidad
- prepara mejor soporte para citas y timestamps

### Ventajas

- mayor robustez
- mejor para casos ambiguos
- mejor para diagnósticos técnicos
- mejor para recomendaciones que necesitan respaldo

### Desventajas

- más lento
- más costoso
- mayor complejidad del prompt y del ensamblado de contexto

### Cuándo usarlo

- diagnósticos clínicos
- consultas de fisioterapeutas
- casos donde el síntoma es ambiguo
- cuando el sistema va a sugerir ejercicios concretos

### Recomendación

Usarlo cuando la consulta implique tratamiento, diagnóstico o necesidad fuerte de confianza.

## Recomendación práctica del proyecto

La recomendación actual es esta:

- `medium` como modo por defecto
- `high` para diagnósticos o tratamiento
- `low` solo como modo auxiliar o de depuración

En otras palabras:

- no ejecutarlo siempre en `high`
- pero tampoco dejarlo siempre en `low`

El equilibrio correcto hoy es:

```text
usuario general -> medium
fisioterapeuta / diagnóstico / tratamiento -> high
debug interno -> low
```

## Cómo debería funcionar una consulta real

El flujo esperado de `query/ask` debería ser:

```text
pregunta del usuario
-> detectar intención
-> elegir calidad de respuesta
-> retrieval según calidad
-> ampliar contexto en Supabase si hace falta
-> redactar respuesta con un modelo
-> devolver ejercicios, explicación y soporte
```

## Qué modelo usar en la consulta final

No tiene por qué ser el mismo modelo que generó el conocimiento estructurado.

Se pueden separar roles:

- modelo de análisis: construye el conocimiento
- modelo de respuesta: responde con el contexto recuperado

### Recomendación

- mantener un modelo fuerte para análisis estructurado
- permitir un modelo distinto para answering
- solo subir a un modelo más costoso si la calidad de respuesta lo necesita

## Decisión actual

La arquitectura de consulta debería construirse así:

1. `video_knowledge_units_v1` para recuperar conocimiento útil
2. `video_segments_v1` para recuperar respaldo y evidencia
3. `medium` como modo general
4. `high` como modo clínico o de mayor confianza

Esta es la forma más razonable de pasar de "videos analizados" a "respuestas útiles para síntomas, deficiencias y diagnósticos".
