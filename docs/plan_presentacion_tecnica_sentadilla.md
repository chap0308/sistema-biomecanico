# Plan de presentación técnica del sistema de sentadilla bilateral

## 1. Decisión recomendada

La presentación principal debe elaborarse como un archivo PowerPoint editable y exportable a PDF. La demostración web y un video explicativo corto deben utilizarse como evidencias complementarias, no como sustitutos de las diapositivas.

```text
Presentación PPTX
    -> conduce el argumento y controla el tiempo

Aplicación web
    -> demuestra que el sistema funciona con un caso real

Video explicativo corto
    -> anima conceptos difíciles como prominencia e interpolación
```

Esta combinación reduce el riesgo de depender de internet durante la exposición y permite conservar fórmulas, referencias y figuras con un diseño controlado.

## 2. Audiencia y principio narrativo

La audiencia no necesita conocer previamente MediaPipe, procesamiento de señales ni geometría analítica. Por eso cada concepto debe responder, en este orden:

1. ¿Qué problema técnico resuelve?
2. ¿Qué dato utiliza?
3. ¿Qué transformación realiza?
4. ¿Qué resultado produce?
5. ¿Qué limitación conserva?

La fórmula debe aparecer después de la intuición visual, no antes.

## 3. Estructura sugerida

| Diapositiva | Mensaje principal | Evidencia recomendada |
|---:|---|---|
| 1 | El sistema detecta compensaciones observables durante una sentadilla bilateral | Título y fotograma con overlay |
| 2 | El problema no es solo observar, sino medir de forma reproducible | Comparación observación visual frente a salida estructurada |
| 3 | El pipeline convierte video en evidencia trazable | Flujo fases 2, 3, 4 y 5 |
| 4 | MediaPipe proporciona coordenadas 2D por fotograma | Sistema de coordenadas, 13 puntos y visibilidad |
| 5 | La calidad determina qué fotogramas pueden participar | Overlay correcto/deficiente y gráfica de disponibilidad |
| 6 | La trayectoria de caderas representa el ciclo de sentadilla | Curva `hip_midpoint_y` y convención `y` hacia abajo |
| 7 | La señal se limpia antes de buscar repeticiones | Cruda, interpolación, mediana y promedio |
| 8 | La prominencia separa profundidades reales de oscilaciones | Pico, bases laterales, fórmula y umbral adaptativo |
| 9 | El retorno vertical evita dividir una pausa en dos repeticiones | Caso de cuatro repeticiones corregido |
| 10 | Cada variable usa una geometría interpretable | Selector tronco, pelvis, rodilla y diferencia bilateral |
| 11 | El valgo se mide contra una posición esperada | Interpolación espacial sobre cadera-tobillo y punto `K` |
| 12 | La normalización permite comparar distancias de imagen | Referencia `W0` y porcentajes |
| 13 | Las reglas convierten mediciones en clasificaciones independientes | Bandas ausente, no concluyente y presente |
| 14 | El desempeño se evalúa contra referencia experta | Instrumento 3, F1-score y Kappa |
| 15 | El alcance es técnico y observacional | Aportes, limitaciones y trabajo futuro |

Para una exposición breve pueden fusionarse las diapositivas 4-5, 7-9 y 11-12, obteniendo una versión de 10 a 12 diapositivas.

## 4. Conceptos que requieren una figura propia

### 4.1. Coordenadas de imagen

Mostrar una imagen con:

- origen `(0, 0)` en la esquina superior izquierda;
- eje `x` hacia la derecha;
- eje `y` hacia abajo;
- cadera alta con menor `y` y cadera baja con mayor `y`.

### 4.2. Interpolación temporal

Mostrar dos muestras conocidas y una pérdida intermedia. La animación debe construir el puente lineal y aclarar que la calidad original del fotograma no cambia.

### 4.3. Prominencia

Mostrar un máximo, dos bases y la base más alta. La línea vertical debe crecer desde la base seleccionada hasta el máximo. Después se compara contra la prominencia mínima.

### 4.4. Interpolación espacial para la rodilla

Mostrar cadera `H`, tobillo `A`, rodilla observada `K_obs` y punto esperado `K`. Primero se localiza `K` sobre el segmento `H-A` a la altura de la rodilla; luego se representa la distancia horizontal firmada entre `K_obs` y `K`.

### 4.5. Normalización con `W0`

Mostrar la misma desviación en dos videos con tamaños de imagen diferentes. Al dividir por el ancho inicial de hombros, ambos resultados pueden expresarse en una escala corporal comparable.

## 5. Uso de las herramientas

| Herramienta | Uso recomendado | Decisión |
|---|---|---|
| PowerPoint | Presentación principal, notas del expositor, referencias y respaldo offline | Principal |
| Aplicación web | Demostración de un caso real, navegación por repetición y trazabilidad | Complementaria obligatoria |
| HyperFrames | Video animado de 60-90 segundos para explicar coordenadas, limpieza, prominencia y geometría | Complementaria opcional |
| Gamma | Borrador rápido de estructura o exploración visual | No usar como fuente final de fórmulas ni diagramas |
| diagrams.net | Arquitectura y flujo general del sistema | Recurso estático dentro del PPTX |
| Matplotlib | Gráficas científicas reproducibles desde datos reales | Fuente principal de figuras cuantitativas |

Gamma permite exportar a PowerPoint y PDF, pero algunos efectos, escalas y fuentes pueden variar durante la exportación. En una presentación con ecuaciones y geometrías precisas, ese comportamiento obliga a revisar manualmente cada diapositiva. Por eso puede ayudar a explorar estilos, pero no debe gobernar el contenido técnico final.

HyperFrames transforma HTML, CSS, medios y animaciones controlables en videos MP4 deterministas. Es apropiado para una explicación animada y repetible, especialmente para:

- hacer aparecer progresivamente los ejes y puntos anatómicos;
- animar la interpolación entre muestras;
- dibujar las bases y prominencia de un pico;
- recorrer el eje cadera-tobillo hasta el punto esperado de rodilla;
- superponer fórmulas sobre un fragmento del video.

No conviene usar HyperFrames como presentación principal. Un video tiene ritmo fijo, dificulta detenerse ante una pregunta y no reemplaza la demostración interactiva de la aplicación. Su mejor función es producir una pieza breve que pueda insertarse en PowerPoint o reproducirse desde un archivo local.

## 6. Video explicativo opcional

Duración recomendada: 60 a 90 segundos.

```text
0-10 s   Video -> pose 2D y coordenadas
10-25 s  Señal cruda -> interpolación -> filtros
25-40 s  Prominencia y selección de repetición
40-60 s  Geometría de tronco, pelvis y rodilla
60-75 s  Umbral -> clasificación
75-90 s  Comparación experta y alcance
```

El video debe utilizar datos del caso real y conservar una leyenda que indique cuándo una figura es demostrativa. No debe presentar los umbrales provisionales como valores clínicos establecidos.

## 7. Qué evitar

- Mostrar cuatro fórmulas completas en una sola diapositiva.
- Reproducir tablas extensas de CSV o instrumentos sin jerarquía visual.
- Usar animaciones decorativas que no expliquen una transformación.
- Confundir interpolación temporal con interpolación espacial.
- Describir prominencia como confianza o probabilidad.
- Presentar la salida como diagnóstico o causa anatómica.
- Depender exclusivamente de la aplicación web o de internet durante la defensa.

## 8. Recursos existentes

- `docs/analisis_caso_dev_valgo_izq_002_fases_2_5.md`;
- `docs/explicacion_visual_limpieza_prominencia_segmentacion.md`;
- `docs/assets/segmentacion_sentadilla/01_limpieza_interpolacion_suavizado.png`;
- `docs/assets/segmentacion_sentadilla/02_prominencia_picos_reales.png`;
- `docs/assets/segmentacion_sentadilla/03_error_doble_pico_recuperacion.png`;
- aplicación web con overlay, gráficas sincronizadas, geometría y reglas;
- diagramas de arquitectura y flujos existentes.

## 9. Siguiente incremento recomendado

1. Preparar el guion definitivo y el tiempo disponible.
2. Crear el PowerPoint maestro con 10-15 diapositivas.
3. Implementar en la web el modo de demostración descrito en `uso_artefactos_outputs_interfaz_sentadilla.md`.
4. Producir con HyperFrames únicamente el video corto de los conceptos que se benefician de movimiento.
5. Ensayar con una versión offline del video y capturas de respaldo de la web.

## 10. Referencias de herramientas

- [HyperFrames](https://github.com/heygen-com/hyperframes): motor abierto para crear composiciones HTML y renderizarlas como MP4 mediante Chromium y FFmpeg.
- [Gamma: exportación](https://help.gamma.app/en/articles/8022861-what-s-the-easiest-way-to-export-my-gamma): formatos disponibles y consideraciones de exportación a PPTX, PDF y PNG.
