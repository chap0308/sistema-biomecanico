# Guía técnica de grabación para el desarrollo de la sentadilla bilateral

## 1. Finalidad

Esta guía complementa el protocolo formal de participación. Su objetivo es estandarizar los videos usados durante el desarrollo y las pruebas del sistema, sin modificar el alcance metodológico aprobado.

El protocolo formal sigue siendo [protocolo_participacion_grabacion_sentadilla.md](/D:/sistema-biomecanico/docs/protocolo_participacion_grabacion_sentadilla.md).

## 2. Alcance obligatorio de la captura

- Ejercicio: sentadilla bilateral.
- Condición: sin barra, mancuernas ni otra carga externa.
- Vista: anterior; la persona mira directamente a la cámara.
- Plano de análisis: frontal.
- Cámara: monocular y fija durante toda la grabación.
- Ejecución: al menos una repetición completa con posición inicial, descenso, punto de máxima profundidad tolerada, ascenso y cierre.
- Uso del resultado: detección de compensaciones observables; no diagnóstico clínico.

## 3. Configuración recomendada de cámara

| Elemento | Recomendación para desarrollo | Razón |
|---|---|---|
| Dispositivo | Teléfono inteligente con cámara posterior | Suele ofrecer mejor resolución y evita el espejo automático de la cámara frontal |
| Orientación | Vertical | Facilita incluir cuerpo completo y márgenes sin alejar demasiado la cámara |
| Resolución | Preferida: 1080 × 1920; mínima práctica: 720 × 1280 | Mejora la localización de rodillas, tobillos, talones y puntas de los pies |
| Frecuencia | 30 fotogramas por segundo | Es suficiente para una sentadilla controlada y simplifica la comparación entre videos |
| Formato | MP4, preferentemente H.264 | Compatible con OpenCV y con el pipeline local |
| Lente | 1×, sin zoom digital ni modo gran angular | Reduce deformaciones y diferencias entre casos |
| Soporte | Trípode o apoyo completamente estable | Evita que el movimiento de cámara se confunda con desplazamiento corporal |
| Altura | Aproximadamente a la altura media de la pelvis del participante | Reduce distorsión por perspectiva entre tronco y miembros inferiores |
| Dirección | Cámara centrada y perpendicular al plano frontal de la persona | Evita que una rotación de cámara parezca una asimetría |
| Distancia | Aproximadamente 2,5 a 3,5 m, ajustada al lente y estatura | Debe priorizarse el encuadre corporal completo sobre una distancia rígida |

La cuadrícula de la cámara puede usarse para comprobar que el teléfono no esté inclinado. No debe aplicarse zoom durante la grabación ni cambiar la posición del dispositivo entre repeticiones del mismo caso.

## 4. Encuadre obligatorio

- Deben verse la cabeza, ambos hombros, ambas caderas, ambas rodillas, ambos tobillos, ambos talones y ambas puntas de los pies durante todo el movimiento.
- Debe conservarse un margen aproximado de 5 % a 10 % alrededor del cuerpo, especialmente debajo de los pies y a ambos lados.
- El participante debe ubicarse en el centro del encuadre.
- Ambos pies deben aparecer completos y apoyados en el suelo.
- No deben aparecer otras personas, máquinas, barras u objetos cruzando el cuerpo.
- El video no debe estar espejado. Las etiquetas izquierda y derecha siempre corresponden al lado anatómico del participante, no al lado de la pantalla.

Si el cuerpo sale parcialmente del encuadre, se corta un pie o se pierde una rodilla, el video no debe trasladarse a la carpeta de casos aceptados.

## 5. Iluminación y fondo

### Iluminación

- Usar luz frontal o frontal-diagonal uniforme.
- Evitar una ventana o luminaria intensa detrás del participante.
- Evitar zonas oscuras sobre pelvis, rodillas y pies.
- Evitar parpadeo de luces y sombras fuertes que atraviesen las articulaciones.
- Comprobar en una grabación de prueba que se distingan claramente tronco, pelvis y miembros inferiores.

La iluminación se considera adecuada cuando todos esos segmentos pueden distinguirse con claridad. Puede aceptarse como regular si existe una limitación leve, pero el cuerpo continúa siendo analizable. Se rechaza cuando compromete los puntos anatómicos críticos.

### Fondo

- Preferir una pared lisa o un espacio visualmente simple.
- Debe existir contraste entre la ropa y el fondo.
- Evitar espejos, pantallas, reflejos, patrones complejos y objetos alineados con las extremidades.
- Evitar que el piso y el calzado tengan exactamente el mismo color.

## 6. Ropa, calzado y presentación del participante

- Usar camiseta ajustada o de corte cercano al cuerpo.
- Usar short por encima de la rodilla o pantalón deportivo ajustado que permita identificar cadera, rodilla y tobillo.
- Evitar ropa holgada, chaquetas, prendas largas, cinturones anchos y telas que oculten la silueta.
- Evitar que la ropa tenga el mismo color que el fondo.
- Mantener el mismo criterio de calzado en toda la muestra. Para pruebas iniciales se recomienda calzado deportivo bajo, sin plataforma alta y con contraste respecto al piso.
- No usar sandalias o calzado suelto en la muestra formal, porque pueden desplazarse respecto al pie y reducir la estabilidad de los puntos de talón y punta.
- Recoger el cabello si cubre hombros o parte superior del tronco.
- Retirar objetos que puedan tapar articulaciones, como bolsos o prendas atadas a la cintura.

No es necesario colocar marcadores físicos. La prioridad es que los puntos anatómicos estimados por MediaPipe sean visibles y estables.

### 6.1 Referencias opcionales en el suelo

Una referencia plana en el suelo puede mejorar la **repetibilidad de la colocación**, pero no aumenta directamente la precisión interna de MediaPipe ni sustituye los puntos anatómicos clave. Su utilidad es mantener estable la base de apoyo y facilitar la revisión visual entre repeticiones.

No se recomienda una única cruz rígida en la punta de los pies para todos los participantes, porque podría forzar una separación u orientación que no corresponde a su postura cómoda. Si se usa cinta adhesiva, la configuración recomendada es:

1. una línea central alineada con el centro de la cámara;
2. una marca plana para cada talón;
3. una línea corta desde cada talón hacia la dirección del segundo dedo del pie;
4. colocación definida después de que el participante adopte una base cómoda;
5. conservación de esa misma base durante las tres repeticiones y registros comparables.

La cinta debe ser plana, antideslizante, de color contrastante y no reflectante. No debe colocarse ningún elemento elevado debajo del talón. La referencia del suelo se registrará como ayuda de estandarización, no como marcador anatómico ni como evidencia de una alteración del pie.

## 7. Posición inicial y ejecución estándar

1. Colocarse de frente a la cámara.
2. Adoptar una separación cómoda de pies, aproximadamente al ancho de hombros, y mantenerla durante todos los intentos del mismo caso.
3. Mantener las puntas de los pies en una orientación cómoda y constante; no modificar deliberadamente la base entre repeticiones.
4. Extender los brazos hacia delante a la altura aproximada de los hombros para evitar que las manos cubran caderas o rodillas.
5. Permanecer quieto entre 2 y 3 segundos antes de iniciar.
6. Realizar tres repeticiones controladas, siempre que no exista dolor o fatiga.
7. Usar una velocidad aproximada de 2 segundos de descenso y 2 segundos de ascenso, sin rebotes.
8. Descender solo hasta una profundidad cómoda y reproducible.
9. Mantener ambos talones apoyados y no usar discos, cuñas ni soportes para aumentar artificialmente la profundidad.
10. Permanecer quieto entre 2 y 3 segundos al finalizar.

Para pruebas técnicas se recomienda grabar las tres repeticiones en un solo video. La unidad registrada continúa siendo un video por caso.

## 8. Casos controlados para el desarrollo

Los siguientes patrones se pueden representar de manera deliberada solo para verificar el comportamiento inicial del software. Deben realizarse sin carga, con amplitud moderada, sin dolor y sin forzar posiciones articulares. Si intervienen participantes distintos del investigador, conviene que un entrenador o fisioterapeuta supervise la instrucción.

| Caso de prueba | Ejecución controlada | Variable que debe responder | Salida esperada |
|---|---|---|---|
| Negativo o sin patrón marcado | Mantener hombros y pelvis centrados y procurar que las rodillas sigan una trayectoria estable sobre los pies | Todas las variables deben permanecer próximas a su referencia | Ausente o no detectado |
| Inclinación de tronco a la izquierda | Mantener la pelvis lo más centrada posible y desplazar suavemente el eje de hombros hacia el lado anatómico izquierdo durante el descenso | Ángulo del eje hombros-pelvis respecto a la vertical | Inclinación lateral izquierda |
| Inclinación de tronco a la derecha | Repetir el patrón hacia el lado anatómico derecho | Ángulo del eje hombros-pelvis respecto a la vertical | Inclinación lateral derecha |
| Desplazamiento pélvico a la izquierda | Trasladar suavemente el punto medio de la pelvis hacia la izquierda durante el descenso, procurando no girar el cuerpo | Desplazamiento horizontal normalizado del centro pélvico | Desplazamiento pélvico izquierdo |
| Desplazamiento pélvico a la derecha | Repetir el patrón hacia el lado anatómico derecho | Desplazamiento horizontal normalizado del centro pélvico | Desplazamiento pélvico derecho |
| Valgo visible izquierdo | Permitir una aproximación medial leve y controlada de la rodilla izquierda respecto a la relación cadera-tobillo | Alineación frontal cadera-rodilla-tobillo izquierda | Valgo dinámico visible izquierdo |
| Valgo visible derecho | Repetir el patrón con la rodilla derecha | Alineación frontal cadera-rodilla-tobillo derecha | Valgo dinámico visible derecho |
| Valgo visible bilateral | Permitir una aproximación medial leve de ambas rodillas | Alineación frontal de ambos miembros inferiores | Valgo dinámico visible bilateral |

No debe forzarse el valgo, realizarse cerca del fallo ni buscar una profundidad que produzca dolor. Una desviación leve pero visible es suficiente para una prueba de software.

La asimetría bilateral observable no se recomienda como gesto aislado en la primera ronda. Se calculará comparando las trayectorias o medidas derecha e izquierda y puede aparecer como consecuencia de valgo unilateral, desplazamiento pélvico u otro comportamiento desigual. Después de validar cada señal por separado se pueden grabar casos mixtos y ambiguos.

### 8.1 Casos con más de un patrón

Sí es posible que un mismo video presente simultáneamente inclinación del tronco, desplazamiento pélvico, valgo y diferencia bilateral. El sistema se diseñará como **clasificador multietiqueta**: cada patrón tendrá una regla independiente y un caso podrá conservar cero, una o varias salidas, además del estado `no concluyente` por patrón.

La estrategia de grabación tendrá dos etapas:

1. **Casos aislados controlados:** sirven para verificar signo, dirección, sensibilidad y umbral inicial de cada regla con la menor interferencia posible.
2. **Casos combinados y espontáneos:** sirven para comprobar que las reglas pueden coexistir y que una compensación no oculta ni genera artificialmente otra.

La asimetría bilateral no debe interpretarse como causa de las otras compensaciones. Es una medida transversal de desigualdad entre lados y puede coexistir con un valgo unilateral, un desplazamiento pélvico u otra diferencia lateral. Para evitar doble conteo, el reporte conservará por separado:

- variables geométricas medidas;
- patrones específicos detectados;
- índice o estado de asimetría bilateral;
- evidencia y regla aplicada para cada salida.

El registro técnico ya admite varias etiquetas previstas mediante una lista de `intended_findings`. Para las pruebas aisladas se registrará una etiqueta principal; para casos combinados se podrán registrar varias sin cambiar el contrato de datos.

Los casos controlados no demuestran que una persona tenga una deficiencia real ni constituyen diagnóstico. Su finalidad es comprobar dirección, sensibilidad, trazabilidad y estabilidad del algoritmo. La referencia final de evaluación será la clasificación consolidada de los expertos.

## 9. Organización y nombres de archivos

Colocar inicialmente los videos originales en:

```text
data/sentadilla_bilateral/raw/
```

No colocarlos directamente en `curated`. Esa carpeta se reserva para los videos aceptados después de aplicar el Instrumento 1.

Nombres sugeridos para desarrollo:

```text
dev_negativo_001.mp4
dev_tronco_izq_001.mp4
dev_tronco_der_001.mp4
dev_pelvis_izq_001.mp4
dev_pelvis_der_001.mp4
dev_valgo_izq_001.mp4
dev_valgo_der_001.mp4
dev_valgo_bilateral_001.mp4
```

Para la muestra formal se usarán identificadores neutros como `caso_001.mp4`; la etiqueta no debe quedar expuesta en el nombre del archivo evaluado por los expertos si se busca reducir sesgo.

## 10. Registro y resultados disponibles actualmente

Inicializar el registro local:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_squat_analysis.py init
```

Registrar un video pendiente de revisión:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_squat_analysis.py register `
  --case-id dev_valgo_izq_001 `
  --video data\sentadilla_bilateral\raw\dev_valgo_izq_001.mp4 `
  --profile positivo_controlado `
  --intended-finding valgo_dinamico_visible `
  --protocol-review-status pendiente
```

El registro se guarda en:

```text
data/sentadilla_bilateral/metadata/casos.csv
```

El resultado técnico inicial se guarda en:

```text
data/sentadilla_bilateral/outputs/<case_id>/registration.json
```

`registration.json` contiene resolución, frecuencia, cantidad de fotogramas, duración, alcance metodológico y estado de revisión. La Fase 2 ya permite generar puntos anatómicos, calidad por fotograma, gráfica y overlay mediante el comando `extract-pose`. Las variables biomecánicas y compensaciones todavía no se calculan.

La elevación del talón no es una salida principal del sistema actual. Se controla como condición de ejecución porque puede modificar la profundidad, la inclinación del tronco y la trayectoria de las rodillas. Una elevación breve puede registrarse como observación; una elevación evidente o sostenida, o el uso de soporte externo, se considera una desviación del protocolo cuando compromete la comparación entre casos.

## 11. Depuración disponible en la Fase 2

Cada caso procesado tendrá una estructura semejante a:

```text
data/sentadilla_bilateral/outputs/<case_id>/
  registration.json
  landmarks.csv
  frame_quality.csv
  overlay.mp4
  pose_quality.png
  pose_summary.json
```

- `overlay.mp4`: puntos anatómicos, conexiones, estado de validez, visibilidad y anonimización facial.
- `landmarks.csv`: coordenadas y visibilidad por fotograma.
- `frame_quality.csv`: fotogramas procesados, válidos y motivos de rechazo.
- `pose_quality.png`: gráfica temporal para revisar estabilidad, disponibilidad y umbral de visibilidad.
- `pose_summary.json`: resumen agregado de procesamiento y rutas de artefactos.

Las fases implementadas generan además métricas biomecánicas, `findings.json`
y `rule_evidence.csv`. El primero contiene la clasificación multietiqueta y el
segundo conserva los valores, estados por repetición, dirección y umbrales
aplicados.

La clasificación provisional se ejecuta con:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\run_squat_analysis.py classify `
  --case-id dev_valgo_izq_001 `
  --biomechanics-summary-json data\sentadilla_bilateral\outputs\dev_valgo_izq_001\biomechanical_summary.json `
  --quality-summary-json data\sentadilla_bilateral\outputs\dev_valgo_izq_001\quality_gate_summary.json
```

Las pruebas automatizadas se ejecutan con:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe -m pytest tests\squat
```

La salida de esas pruebas se observa en la terminal. Para generar un reporte HTML de cobertura:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe -m pytest tests\squat --cov=src.squat --cov-report=html
```

El reporte se abre desde `htmlcov/index.html`.

## 12. Lista rápida antes de entregar un video

- Cámara posterior, fija, a 1× y sin espejo.
- Vista anterior y cámara centrada a la altura de la pelvis.
- Cuerpo completo y ambos pies visibles durante todo el video.
- Luz frontal uniforme y fondo con contraste.
- Ropa ajustada que permita distinguir caderas, rodillas y tobillos.
- Sentadilla sin carga externa y sin dolor.
- Dos o tres segundos quieto antes y después.
- Tres repeticiones controladas.
- Archivo MP4 colocado en `data/sentadilla_bilateral/raw/`.
- Nombre de desarrollo coherente con el patrón representado.
