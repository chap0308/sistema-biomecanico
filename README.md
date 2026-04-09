# PhysioChat

PhysioChat es una aplicación de apoyo clínico multimodal para fisioterapia y biomecánica. Su objetivo es combinar:

- análisis postural a partir de imágenes
- chat clínico con historial
- recuperación semántica sobre una base de conocimiento vectorial
- orientación funcional con diagnóstico orientativo, tratamiento sugerido y ejercicios descriptivos

En lugar de depender solo del conocimiento “interno” de un modelo, PhysioChat consulta una base de conocimiento construida a partir de contenido biomecánico real y responde con contexto recuperado.

## Demo

<video controls width="100%" src="https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/chat-media/demo_v1/demo_physio_chat_v1.mp4">
  Tu visor no soporta reproducción embebida. Abre el demo aquí:
  https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/chat-media/demo_v1/demo_physio_chat_v1.mp4
</video>

Enlace directo:

- [Ver demo de PhysioChat](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/chat-media/demo_v1/demo_physio_chat_v1.mp4)

## Qué hace hoy

El MVP actual permite:

- iniciar sesión y conservar historial de conversaciones
- enviar consultas clínicas en lenguaje natural
- adjuntar imágenes para análisis postural estático
- derivar `findings` y `deficiencies` por vista
- combinar esas deficiencias con el mensaje del usuario
- consultar la base de conocimiento indexada en Qdrant
- responder con orientación funcional, puntos clave, ejercicios sugeridos, advertencias y fuentes relacionadas

## Base de conocimiento actual

La base de conocimiento actual está construida principalmente a partir del contenido educativo de **Conor Harris**, con foco especial en sus YouTube Shorts:

- [Conor Harris Shorts](https://www.youtube.com/@conorharris/shorts)

De esos videos se extrae y estructura conocimiento relacionado con:

- hombro y escápula
- pelvis y cadera
- pie y tobillo
- cuello y mandíbula
- respiración y caja torácica
- compensaciones posturales y patrones de movimiento

## Cómo se construye la base

El pipeline RAG es local-first y está organizado así:

1. ingestión de fuentes
2. extracción de artefactos
3. análisis y estructuración de conocimiento
4. persistencia de metadata
5. indexación vectorial
6. retrieval híbrido
7. answering grounded

### Fuentes soportadas

- YouTube Shorts
- videos locales
- URLs públicas
- páginas web

### Tecnologías usadas para extracción y enriquecimiento

Según la ruta de procesamiento, el sistema usa distintas herramientas para extraer señal útil de los videos:

- `yt-dlp` para descarga y staging de videos
- `ffmpeg` para audio, frames y recortes
- `OpenCV` para procesamiento visual y muestreo
- `Tesseract OCR` para texto en pantalla
- ASR local para transcript
- detección de escenas y enriquecimiento por segmentos
- Gemini como ruta premium opcional para análisis multimodal
- rutas locales y Hugging Face como fallback o capa estándar

## Arquitectura de almacenamiento

### Supabase

Supabase funciona como sistema de registro y trazabilidad. Guarda:

- fuentes
- drafts de conocimiento
- knowledge units
- segmentos
- intentos de análisis, errores y retries
- conversaciones, mensajes y adjuntos del chat
- buckets de Storage para imágenes originales y debug

### Qdrant

Qdrant funciona como motor de recuperación vectorial. Se usa para:

- indexar evidencia segmentada de video
- indexar conocimiento derivado
- hacer retrieval híbrido por similitud semántica y metadata

Colecciones principales:

- `video_segments_v1`
- `video_knowledge_units_v1`

## Modelos y answering

El proyecto separa dos problemas distintos:

- **análisis**
- **answering**

### Análisis

- `Gemini` se usa como ruta premium cuando hay cuota disponible
- la ruta local-first mantiene el sistema operativo sin depender siempre de un proveedor externo

### Answering

Para responder consultas sobre la base recuperada, hoy existen varios backends:

- `grounded`
- `huggingface`
- `ollama`
- `openai`

Actualmente, la opción más estable y útil para answering remoto en el proyecto quedó orientada a perfiles tipo:

- `HF Qwen3 32B (balanced)`
- `HF Qwen3 4B (cheap)`

## Stack principal

### Backend

- Python
- FastAPI
- Supabase
- Qdrant
- OpenCV
- Tesseract
- ffmpeg

### Frontend

- React
- Vite
- Tailwind CSS v4
- TanStack Query
- Supabase Auth
- componentes UI con Radix/shadcn-style

## Estado actual del producto

Hoy el sistema ya permite:

- construir y mantener una base de conocimiento vectorial
- consultar esa base desde una interfaz web
- combinar imágenes estáticas con contexto textual
- responder con una orientación razonable basada en retrieval

Todavía hay trabajo por hacer en:

- calidad de análisis para nuevas regiones corporales
- pulido de retrieval y reranking
- despliegue cloud completo
- incorporación de análisis dinámico por video
- mejor grounding clínico en casos complejos

## Análisis actual implementado

### `rest_phase1`

Es el flujo ya integrado en el chat. Actualmente:

- recibe 3 imágenes
- calcula variables por vista
- deriva hallazgos y deficiencias
- sube originales y debug a Storage
- envía las deficiencias al endpoint de consulta

## Análisis futuros a incorporar

Estos análisis ya tienen trabajo previo, prototipos o resultados parciales. No representan todavía una validación final ni un análisis clínico perfecto, pero sí muestran que ya existen cálculos, visualizaciones y comparativas útiles para iterar hacia una versión más robusta.

### Foot

En `foot` ya se trabajó sobre comparativas del pie izquierdo y derecho, altura del arco y visualizaciones anotadas para revisar diferencias entre ambos lados. La meta es detectar asimetrías relevantes y relacionarlas con dolor plantar, colapso medial o cambios del apoyo.

| Vista base | Resultado parcial |
| --- | --- |
| ![Foot frontal](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/foot/foot_front_annotated.jpg) | ![Foot comparación de arco](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/foot/arch_height_comparison.png) |
| ![Foot posterior](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/foot/foot_back_annotated.jpg) | El cálculo actual compara visual y métricamente ambos lados para ver si existe una diferencia relevante en la altura del arco o en la distribución general del apoyo. |

| Arco izquierdo | Arco derecho |
| --- | --- |
| ![Foot arco izquierdo](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/foot/foot_left_arch_annotated.jpg) | ![Foot arco derecho](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/foot/foot_right_arch_annotated.jpg) |

### ISA

En `isa` ya existen resultados preliminares para observar la caja torácica en estático y durante respiración. El foco de esta etapa es medir ángulos costales y excursión torácica para tener una lectura más objetiva del patrón respiratorio.

| Base de cálculo | Resultado parcial |
| --- | --- |
| ![ISA estático](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/isa/annotated_static.jpg) | ![ISA costal margin angles](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/isa/costal_margin_angles_plot.png) |
| ![ISA breathing preview](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/isa/annotated_breathing_preview.png) | ![ISA thoracic excursion](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/isa/thoracic_excursion_plot.png) |

Estos resultados intentan mostrar:

- comportamiento de los ángulos del margen costal
- excursión torácica durante el patrón respiratorio observado
- una base inicial para interpretar rigidez, expansión y estrategia respiratoria

### Scapula

En `scapula` ya se generaron ejemplos anotados para torso completo y cuerpo completo. El valor de esta etapa es que permite visualizar cómo podría quedar una futura detección más robusta de referencias escapulares con suficiente contexto corporal para interpretar mejor asimetrías y desplazamientos.

| Torso | Cuerpo completo |
| --- | --- |
| ![Scapula torso](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/scapula/nuevo_scapula_annotated_full_torso.jpg) | ![Scapula full body](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/scapula/scapula_annotated_full_fullbody.jpg) |

Lo que muestran estas pruebas:

- localización visual preliminar de referencias escapulares
- evaluación inicial de contexto torácico y escapular
- base para futuros cálculos sobre asimetría, winging y control escapular

### Shoulder abduction

En `shoulder_abduction` ya existen resultados preliminares sobre movimiento escapular durante la abducción del hombro. La meta aquí es comparar cómo se comporta la escápula durante el gesto y detectar compensaciones o patrones no deseados.

<video controls width="100%" src="https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/shoulder_abduction/v35_abduction_5.mp4">
  Tu visor no soporta reproducción embebida. Abre el video aquí:
  https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/shoulder_abduction/v35_abduction_5.mp4
</video>

| Métrica | Resultado |
| --- | --- |
| Protracción | ![Shoulder abduction protracción](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/shoulder_abduction/movement_protraction_plot.png) |
| Elevación escapular | ![Shoulder abduction elevación escapular](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/shoulder_abduction/movement_scapular_elevation_plot.png) |
| Ratio escapulohumeral | ![Shoulder abduction ratio escapulohumeral](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/shoulder_abduction/movement_scapulohumeral_ratio_plot.png) |
| Upward rotation | ![Shoulder abduction upward rotation](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/shoulder_abduction/movement_upward_rotation_plot.png) |
| Winging | ![Shoulder abduction winging](https://lpclraomqgffudcguyfb.supabase.co/storage/v1/object/public/analisis-futuros/shoulder_abduction/movement_winging_plot.png) |

Estos resultados parciales ya permiten comparar cómo cambia el comportamiento escapular a lo largo del gesto y sirven como base para una evaluación futura más interpretable a nivel clínico.

La idea es incorporar gradualmente estos cálculos al pipeline productivo para mejorar la calidad del análisis y la utilidad clínica del sistema.

## Documentación técnica relacionada

La documentación detallada de arquitectura, pipelines, storage y despliegue está en:

- [docs/RAG](docs/RAG)

Archivos particularmente útiles:

- [RAG local architecture](docs/RAG/RAG_LOCAL_ARCHITECTURE.md)
- [Supabase + Qdrant storage split](docs/RAG/RAG_STORAGE_SUPABASE_QDRANT.md)
- [Cloud deployment guide](docs/RAG/RAG_CLOUD_DEPLOYMENT_GUIDE.md)
- [Chat backend contract](docs/RAG/CHAT_APP_BACKEND_CONTRACT.md)
