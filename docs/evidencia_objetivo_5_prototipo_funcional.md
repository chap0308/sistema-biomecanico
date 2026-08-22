# Evidencia del Objetivo Específico 5: prototipo funcional

## Objetivo vigente

**Implementar un prototipo funcional que integre el registro del caso, procesamiento del video, estimación de pose 2D, segmentación temporal, cálculo biomecánico, clasificación interpretable, visualización y generación de reportes.**

## Qué debe demostrarse

El objetivo no se prueba mostrando una función aislada. Debe existir un flujo ejecutable de entrada a salida que conserve el caso, procese el video, muestre cómo se obtuvo el resultado, permita la evaluación ciega y genere archivos recuperables.

## Arquitectura implementada

![Arquitectura del sistema](evidencias/fase6/arquitectura_drawio_validada.png)

```mermaid
flowchart LR
    U["Investigador o usuario"] --> W["Next.js"]
    W --> A["FastAPI"]
    A --> P["Pipeline Python"]
    P --> CV["OpenCV + MediaPipe"]
    P --> N["pandas + NumPy"]
    P --> R["Reglas interpretables"]
    A --> S["Supabase: Postgres + Storage + Auth"]
    P --> S
    S --> W
    W --> V["Videos, gráficas, tablas y reportes"]
```

## Flujo funcional por caso

```mermaid
flowchart TD
    A["Registrar y cargar video"] --> B["Persistir caso y archivo"]
    B --> C["Procesar de forma asíncrona"]
    C --> D["Pose 2D y anonimización"]
    D --> E["Segmentar repeticiones"]
    E --> F["Aplicar puerta de calidad"]
    F -->|"Sin repeticiones elegibles"| G["Conservar evidencia técnica y bloquear comparación"]
    F -->|"Con repeticiones elegibles"| H["Calcular variables"]
    H --> I["Clasificar patrones"]
    I --> J["Visualizar trazabilidad"]
    J --> K["Asignar expertos y consolidar referencia"]
    K --> L["Generar Excel y PDF"]
```

## Capacidades demostrables

| Área | Implementación observable |
|---|---|
| Registro | Código trazable, metadatos, carga de MP4 y revisión de protocolo. |
| Procesamiento | Ejecución del pipeline sin depender de que el navegador permanezca abierto. |
| Privacidad | Pixelado facial en artefactos de revisión y almacenamiento con control de acceso. |
| Explicabilidad | Dos overlays, eventos temporales, gráficas sincronizadas, geometría, fórmulas y reglas. |
| Calidad | Exclusión por caso o repetición, sin ocultar ejecuciones válidas restantes. |
| Roles | Investigador, evaluador experto y espacio personal de usuario final. |
| Evaluación ciega | El experto clasifica sin ver la salida automática hasta el cierre del caso. |
| Persistencia | Historial, asignaciones, evaluaciones, referencias y artefactos recuperables. |
| Reportes | Instrumentos Excel, reporte PDF y datos técnicos normalizados. |

## Evidencia visual del prototipo

![Resultados y trazabilidad en escritorio](evidencias/fase6/resultado_investigador_escritorio.png)

![Resultados y comparación en dispositivo móvil](evidencias/fase6/comparacion_investigador_movil.png)

## Recorridos automatizados verificables

- [Registro y análisis de un caso](evidencias/fase6/playwright/flujo_registro_analisis_caso.webm).
- [Evaluación ciega por experto](evidencias/fase6/playwright/flujo_evaluador_experto.webm).
- [Comparación y descargas](evidencias/fase6/playwright/flujo_comparacion_descargas.webm).

Estos recorridos de Playwright demuestran integración entre interfaz, API y persistencia. Las pruebas unitarias y de integración verifican fórmulas y estados; los recorridos verifican el uso completo en navegador.

## Relación con los instrumentos

- Instrumento 1: registro, captura, admisibilidad y disponibilidad observable.
- Instrumento 2: procesamiento, segmentación, variables, reglas y resultados automáticos.
- Instrumento 3: clasificación experta y comparación con el sistema.

La interfaz digitaliza y organiza estos datos, pero no convierte la base consolidada de análisis en un cuarto instrumento.

## Artefactos de arquitectura y flujo

Los archivos editables se conservan en `docs/diagramas/fase6/`, especialmente:

- `arquitectura_sistema_sentadilla.drawio`;
- `secuencia_procesamiento_video.drawio`;
- `flujo_investigador_sentadilla.drawio`;
- `flujo_experto_instrumento3.drawio`;
- `flujo_video_no_apto_sentadilla.drawio`.

## Criterio de cumplimiento y alcance

El OE5 está funcionalmente implementado y desplegado. La extensión para usuario final permite cargar videos y consultar resultados automáticos, pero no forma parte de la construcción de la referencia experta ni del desempeño formal. El prototipo es una herramienta de apoyo educativo y analítico, no un sistema diagnóstico.
