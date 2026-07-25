# Protocolo de uso real de los instrumentos metodológicos de sentadilla

Este documento explica cómo se usarían los instrumentos metodológicos en un caso real, suponiendo que el sistema de visión por computadora ya se encuentra implementado y operativo.

## 1. Idea general

Los instrumentos no se llenan todos por la misma persona ni en la misma etapa.

- El **investigador** usa primero el **Instrumento 1** para construir la base de videos y filtrar cuáles casos realmente entran al estudio.
- Luego el **sistema** genera la información del **Instrumento 2**, y el investigador la registra o la importa.
- Después los **expertos** usan el **Instrumento 3** para evaluar los mismos videos sin depender del sistema.
- Finalmente, el investigador consolida la comparación y calcula las métricas en la **Matriz de análisis**.

## 2. Flujo real de trabajo

### Etapa 1. Registro y filtro inicial del video

Se usa la hoja **`01_Inst1_FichaMaestra`**.

Su finalidad no es medir aún la biomecánica final, sino responder:

- si el video cumple condiciones mínimas de calidad;
- si la sentadilla realmente puede observarse;
- y si los puntos anatómicos clave necesarios son visibles o razonablemente detectables.

En esta etapa el investigador completa:

- código del video;
- fecha;
- fuente;
- ruta o enlace;
- datos básicos del caso;
- vista de captura;
- resolución;
- iluminación;
- fondo visual;
- visibilidad corporal;
- oclusiones;
- si la sentadilla es observable completa;
- si el video es válido para procesamiento;
- y, si no lo es, el motivo de exclusión.

### Etapa 2. Registro del comportamiento del sistema

Se usa la hoja **`02_Inst2_Procesamiento`**.

Aquí ya no se evalúa si el video “sirve” o no, sino qué hizo el software con ese video:

- si procesó o falló;
- cuántos fotogramas leyó;
- cuántos fotogramas fueron válidos;
- cuántos fotogramas se procesaron correctamente;
- cuántos puntos anatómicos clave detectó;
- qué variables biomecánicas calculó;
- qué criterio biomecánico aplicó;
- y cuál fue la salida final.

Esta hoja debe llenarse desde la salida automática del sistema. Idealmente:

- algunos campos se completan automáticamente;
- y el investigador solo verifica o importa los resultados.

### Etapa 3. Evaluación experta independiente

Se usa la hoja **`03_Inst3_Comparacion`**.

En esta etapa los expertos no ven el resultado del sistema como base para decidir. Cada experto observa el video y clasifica por separado cada repetición detectada en sus columnas:

- tronco;
- pelvis;
- valgo;
- asimetría bilateral.

Después, el investigador completa:

- la columna del sistema computacional;
- la referencia final por consenso o mayoría;
- y la comparación final.

En esta etapa conviene distinguir dos niveles dentro de la misma hoja:

- el bloque de **evaluación**, donde cada experto y el sistema registran su clasificación;
- y el bloque de **consolidación**, donde el investigador resume cuál será la referencia final para cada patrón.

### Etapa 4. Consolidación para análisis estadístico

Se usa la hoja **`04_Matriz_Analisis`**.

Aquí se descompone cada video por repetición y patrón evaluado. Cada ejecución genera cuatro filas:

- tronco;
- pelvis;
- valgo;
- asimetría bilateral.

Con esa matriz consolidada se calculan:

- exactitud;
- precisión;
- sensibilidad;
- especificidad;
- puntaje F1;
- índice Kappa.

## 3. Cómo se llenan los casilleros de landmarks del Instrumento 1

Esta fue la principal ambigüedad detectada.

La respuesta corta es: **no conviene usar solo una `X`**, porque pierde información útil. Tampoco conviene escribir libremente “izquierda” o “derecha” en cada celda, porque vuelve la ficha inconsistente.

Lo más útil es usar una **codificación controlada**.

## 4. Codificación recomendada para landmarks

Para landmarks pares del plano frontal:

- `B`: bilateral visible.
- `I`: solo lado izquierdo visible.
- `D`: solo lado derecho visible.
- `O`: ocluido o intermitente.
- `N`: no visible.

Aplica a:

- hombro;
- cadera;
- rodilla;
- tobillo;
- talón;
- punta del pie.

Para el landmark central:

- `C`: visible.
- `O`: ocluido.
- `N`: no visible.

Aplica a:

- nariz o centro facial.

## 5. Qué significa realmente cada código

### `B`

Significa que ambos lados del landmark están suficientemente visibles para que el investigador considere razonable el análisis posterior del video.

Ejemplo:

- se observan hombro izquierdo y derecho;
- ambas caderas son visibles;
- ambas rodillas y ambos tobillos están dentro del encuadre.

### `I`

Significa que solo el lado izquierdo puede verse o detectarse de forma suficiente.

Esto no implica necesariamente que el video quede excluido de inmediato, pero sí deja evidencia de que el análisis puede quedar limitado.

### `D`

Igual que el caso anterior, pero para el lado derecho.

### `O`

Se usa cuando el punto aparece parcialmente, de forma inestable o con oclusión.

Ejemplo:

- la rodilla se ve solo en parte por la ropa o por la posición de los brazos;
- el talón entra y sale del encuadre;
- el fondo hace difícil distinguir el contorno distal.

### `N`

Significa que no es visible o que no sería razonable esperar una detección confiable.

Ejemplo:

- el pie está fuera de cuadro;
- la resolución es insuficiente;
- el tobillo no se distingue.

### `C`

Se usa solo para el punto central facial cuando es visible. En esta tesis ese punto es complementario, no crítico.

## 6. Entonces, ¿una X ya no sirve?

Puede servir en una versión muy resumida, pero es débil para tesis porque no distingue:

- bilateralidad;
- lateralidad parcial;
- oclusión;
- ausencia real.

Por eso, para un uso metodológico más defendible, la codificación `B / I / D / O / N` es mejor que una `X`.

La `X` solo diría “algo hay”, pero no permitiría justificar por qué un video fue aceptado, observado con reservas o descartado.

## 7. Ejemplo real de llenado del Instrumento 1

Supongamos un video frontal, completo y usable:

- Sentadilla observable completa: `Sí`
- Video válido para procesamiento: `Sí`
- Hombro: `B`
- Cadera: `B`
- Rodilla: `B`
- Tobillo: `B`
- Talón: `O`
- Punta del pie: `B`
- Nariz o centro facial: `C`

Interpretación:

- el video es aceptable;
- el talón tiene alguna limitación;
- pero el conjunto general permite análisis del tronco, pelvis, valgo y asimetría bilateral.

Otro ejemplo, video con problema:

- Sentadilla observable completa: `No`
- Video válido para procesamiento: `No`
- Motivo de exclusión: `Miembro inferior distal fuera de cuadro`
- Hombro: `B`
- Cadera: `B`
- Rodilla: `B`
- Tobillo: `N`
- Talón: `N`
- Punta del pie: `N`

Interpretación:

- aunque parte del cuerpo sí es visible, el video no sirve para el estudio porque faltan referencias distales críticas.

## 8. Qué campos llenaría automáticamente el sistema

En el **Instrumento 2**, varios campos deberían provenir del software:

- estado de procesamiento;
- cantidad total de fotogramas;
- fotogramas válidos para análisis;
- porcentaje de fotogramas válidos;
- fotogramas procesados correctamente;
- porcentaje de fotogramas procesados correctamente;
- número de puntos anatómicos clave detectados;
- variables biomecánicas calculadas;
- tipo de compensación detectada;
- umbral aplicado;
- generación de reporte;
- visualización de resultados.

En una implementación madura, esto no debería transcribirse manualmente uno por uno. Lo ideal sería:

- exportar automáticamente a Excel o CSV;
- o copiar desde una tabla generada por el sistema.

## 8.1. Cómo se llenan las variables biomecánicas del Instrumento 2

Aquí es donde conviene separar dos niveles:

- **variable biomecánica observable**;
- **hallazgo o compensación interpretada**.

No son lo mismo.

### Variables biomecánicas

Estas columnas guardan el valor que el sistema calculó antes de interpretar el resultado:

- `Inclinación del tronco`
- `Desplazamiento lateral de pelvis`
- `Alineación rodilla-cadera-tobillo`
- `Diferencias bilaterales`

Es decir, aquí no debería ir solo el nombre de la compensación, sino el **resultado medido** o la **salida técnica inmediata** del cálculo.

Ejemplos de llenado posibles:

- `Inclinación del tronco = 4.6° hacia la derecha`
- `Desplazamiento lateral de pelvis = 2.1 cm hacia la izquierda`
- `Alineación rodilla-cadera-tobillo = 13° de valgo visual derecho`
- `Diferencias bilaterales = 11 %`

Si el sistema no trabaja directamente con grados o centímetros, entonces puede registrar:

- un valor normalizado;
- un índice;
- o una categoría técnica intermedia.

Ejemplo:

- `Inclinación del tronco = índice 0.18`
- `Diferencias bilaterales = asimetría moderada`

### Tipo de compensación detectada

Esta columna ya no guarda el valor calculado, sino la **conclusión interpretativa** derivada de las variables biomecánicas.

Ejemplos:

- `tronco`
- `pelvis`
- `valgo`
- `asimetría`

Incluso, si el sistema lo permite, podría quedar más explícito:

- `inclinación lateral del tronco`
- `desplazamiento lateral de pelvis`
- `valgo dinámico visible`
- `asimetría bilateral observable`

### Relación entre ambas partes

La lógica correcta sería:

1. el sistema calcula la variable biomecánica;
2. compara ese valor con un umbral o regla;
3. y luego produce el hallazgo interpretable.

En forma simple:

- `Variable biomecánica = qué midió`
- `Umbral aplicado = con qué regla lo evaluó`
- `Tipo de compensación detectada = qué concluyó`

## 8.2. Ejemplo completo del Instrumento 2

Supongamos un caso real:

- `Estado de procesamiento = exitoso`
- `Cantidad total de fotogramas = 240`
- `Fotogramas válidos para análisis = 214`
- `% de fotogramas válidos = 89.2`
- `Fotogramas procesados correctamente = 228`
- `% procesados correctamente = 95.0`
- `N.° de puntos anatómicos clave detectados = 29`
- `Inclinación del tronco = 5.1° derecha`
- `Desplazamiento lateral de pelvis = 2.8 cm izquierda`
- `Alineación rodilla-cadera-tobillo = valgo visible bilateral`
- `Diferencias bilaterales = 12 %`
- `N.° de criterios implementados = 4`
- `Tipo de compensación detectada = pelvis / valgo`
- `Umbral aplicado = >4° tronco; >2 cm pelvis; criterio de colapso medial`
- `Generación de reporte = sí`
- `Visualización de resultados = sí`

Interpretación:

- las columnas de variables biomecánicas muestran qué calculó el sistema;
- la columna de tipo de compensación detectada resume qué hallazgos finales produjo;
- y el umbral aplicado deja trazabilidad de cómo pasó del valor al hallazgo.

## 9. Qué llenan exactamente los expertos

Los expertos **no deberían llenar**:

- el Instrumento 1;
- ni el Instrumento 2.

Los expertos participan principalmente en:

- **Instrumento 3**, como evaluadores del movimiento;
- y en el **documento institucional de validación por juicio de expertos**, si además actúan como validadores de instrumentos.

## 9.1. Uso detallado del documento de validación por juicio de expertos

La ficha institucional de validación no se usa para evaluar videos ni para comparar el sistema contra el criterio experto. Su función aparece antes de la aplicación definitiva de la investigación.

Sirve para que dos o tres expertos revisen si los instrumentos están bien construidos metodológicamente.

En la práctica, cada experto revisa:

- si las cabeceras son claras;
- si cada campo realmente corresponde a una dimensión o indicador;
- si hay coherencia entre lo que se quiere medir y lo que la tabla pide registrar;
- y si faltan campos necesarios para aplicar el estudio sin ambigüedades.

Por tanto, esta ficha se usa una sola vez o en muy pocas iteraciones, normalmente antes de la recolección formal de datos.

### Quién lo llena

- Cada experto validador llena una fila o bloque del instrumento.
- El investigador organiza los instrumentos a validar y consolida las observaciones.

### Qué se espera como resultado

- observaciones de mejora;
- recomendación final;
- y validación firmada del instrumento.

### Cómo se usaría en un caso real

Ejemplo:

1. El investigador presenta el Instrumento 1, 2 y 3 a dos expertos.
2. Cada experto revisa claridad, pertinencia, coherencia y suficiencia.
3. Si ambos observan que falta codificación para landmarks o que una cabecera es ambigua, se ajusta el instrumento.
4. Una vez corregido, el experto vuelve a revisar y firma la versión final.

En otras palabras, esta ficha no mide la sentadilla; valida la calidad metodológica de los instrumentos que sí medirán la sentadilla.

En el **Instrumento 3**, cada experto solo clasifica el patrón visible:

- `Tronco`: ausente / izquierda / derecha / no concluyente
- `Pelvis`: ausente / izquierda / derecha / no concluyente
- `Valgo`: ausente / izquierdo / derecho / bilateral / no concluyente
- `Asimetría bilateral`: ausente / presente / no concluyente

## 9.2. Qué llena el investigador en la parte de consolidación del Instrumento 3

En el **Instrumento 3**, los expertos no completan la consolidación. Esa parte corresponde al investigador, una vez que ya tiene:

- la clasificación del evaluador 1;
- la clasificación del evaluador 2;
- y la clasificación emitida por el sistema.

La consolidación todavía **no es** la matriz final de análisis. Sigue siendo parte del Instrumento 3 y su función es cerrar, para cada par repetición-patrón, cuál será la referencia experta que luego se comparará contra el sistema.

### Qué iría en cada columna del grupo de consolidación

Las columnas de consolidación deberían funcionar así:

- `Referencia final tronco`
  Qué se registra:
  La decisión final experta para el patrón tronco en ese video.
  Ejemplos:
  `izquierda`, `derecha`, `ausente`, `no concluyente`.

- `Referencia final pelvis`
  Qué se registra:
  La decisión final experta para el patrón pelvis.
  Ejemplos:
  `izquierda`, `derecha`, `ausente`, `no concluyente`.

- `Referencia final valgo`
  Qué se registra:
  La decisión final experta para el patrón valgo.
  Ejemplos:
  `izquierdo`, `derecho`, `bilateral`, `ausente`, `no concluyente`.

- `Referencia final asimetría bilateral`
  Qué se registra:
  La decisión final experta para el patrón asimetría bilateral.
  Ejemplos:
  `presente`, `ausente`, `no concluyente`.

### Cómo se decide esa referencia final

La referencia final puede salir de cualquiera de estas reglas:

- `coincidencia directa`
  Cuando ambos expertos coinciden sin discusión.

- `consenso posterior`
  Cuando al inicio discrepan, revisan el video nuevamente y acuerdan una salida final.

- `mayoría`
  Si en el estudio participa un tercer evaluador.

### Ejemplo completo de consolidación dentro del Instrumento 3

Supongamos la ejecución `SQ-07-repeticion-1`.

Resultado en la hoja comparativa:

- `Evaluador 1 - Tronco = izquierda`
- `Evaluador 2 - Tronco = izquierda`
- `Sistema - Tronco = izquierda`
- `Consolidación - Referencia final tronco = izquierda`

- `Evaluador 1 - Pelvis = ausente`
- `Evaluador 2 - Pelvis = derecha`
- `Sistema - Pelvis = derecha`
- `Consolidación - Referencia final pelvis = derecha`
  Nota:
  aquí la referencia final podría salir por `consenso posterior`.

- `Evaluador 1 - Valgo = bilateral`
- `Evaluador 2 - Valgo = bilateral`
- `Sistema - Valgo = bilateral`
- `Consolidación - Referencia final valgo = bilateral`

- `Evaluador 1 - Asimetría bilateral = presente`
- `Evaluador 2 - Asimetría bilateral = presente`
- `Sistema - Asimetría bilateral = presente`
- `Consolidación - Referencia final asimetría bilateral = presente`

### Qué no debería ponerse en la consolidación del Instrumento 3

No conviene poner aquí:

- `verdadero positivo`;
- `falso positivo`;
- `exactitud`;
- `F1`;
- `Kappa`;
- ni observaciones estadísticas globales.

Eso ya pertenece a la matriz complementaria o al análisis final, no al Instrumento 3.

## 10. Cómo se comparan expertos y sistema

El procedimiento recomendado es:

1. El investigador codifica y filtra videos con el Instrumento 1.
2. El sistema procesa los videos válidos y produce la salida del Instrumento 2.
3. Los expertos revisan esos mismos videos y llenan el Instrumento 3.
4. El investigador agrega la salida del sistema en el mismo Instrumento 3.
5. Se define la referencia final:

- coincidencia directa entre 2 expertos;
- o consenso posterior;
- o mayoría si existe un tercer evaluador.

6. Esa referencia final se lleva a la Matriz de análisis.
7. Se calculan las métricas.

## 10.1. Uso detallado de la matriz consolidada de análisis

La matriz consolidada corresponde al anexo complementario de consolidación. Estrictamente hablando, no es un instrumento de recolección primaria como los anteriores, sino una **matriz de análisis final**.

Su función es transformar la comparación del Instrumento 3 en una base apta para cálculo estadístico.

La diferencia central entre ambas cosas es esta:

- la **consolidación del Instrumento 3** decide, por repetición, cuál es la referencia final de cada patrón;
- la **matriz complementaria de análisis** toma esa referencia final y la convierte en filas aptas para cálculo estadístico.

En otras palabras:

- el Instrumento 3 responde: `¿qué concluyeron finalmente los expertos para esta repetición?`
- la matriz complementaria responde: `¿coincidió o no coincidió el sistema con esa referencia, patrón por patrón?`

### Qué contiene

Por cada repetición y por cada patrón evaluado, registra:

- código del video y número de repetición;
- patrón evaluado;
- referencia final;
- salida del sistema;
- coincidencia;
- observación.

### Qué va en cada columna de la matriz complementaria

- `Código del video`
  Qué se registra:
  El identificador único del caso.
  Ejemplos:
  `SQ-07`, `SQ-12`, `SQ-18`.

- `Patrón evaluado`
  Qué se registra:
  El patrón específico que se está comparando en esa fila.
  Ejemplos:
  `Tronco`, `Pelvis`, `Valgo`, `Asimetría bilateral`.

- `Referencia final`
  Qué se registra:
  El resultado consolidado de los expertos tomado desde el Instrumento 3.
  Ejemplos:
  `izquierda`, `ausente`, `bilateral`, `presente`.

- `Salida del sistema`
  Qué se registra:
  La clasificación emitida por el software para ese mismo patrón.
  Ejemplos:
  `izquierda`, `derecha`, `ausente`, `presente`.

- `Coincidencia`
  Qué se registra:
  Si el sistema coincide o no con la referencia final.
  Ejemplos:
  `Sí`, `No`.

- `Observación`
  Qué se registra:
  Notas breves sobre discrepancias, dudas o condiciones especiales.
  Ejemplos:
  `Coincidencia total`, `Discrepancia sistema-expertos`, `Caso no concluyente`, `Referencia final definida por consenso`.

### Quién lo llena

- Lo llena únicamente el investigador.
- Los expertos no llenan esta matriz.
- El sistema tampoco la llena de forma directa, aunque parte de su salida puede importarse.

### Cómo se construye

Se toma cada fila del Instrumento 3 y se “desdobla” por patrón.

Ejemplo:

Si `SQ-07-repeticion-1` fue evaluada en cuatro patrones, en la matriz final aparecerán cuatro filas:

- `SQ-07-repeticion-1 | Tronco | izquierda | izquierda | Sí | Coincidencia total`
- `SQ-07-repeticion-1 | Pelvis | ausente | derecha | No | Discrepancia sistema-expertos`
- `SQ-07-repeticion-1 | Valgo | bilateral | bilateral | Sí | Coincidencia total`
- `SQ-07-repeticion-1 | Asimetría bilateral | presente | presente | Sí | Coincidencia total`

### Ejemplo de cómo nace una fila desde el Instrumento 3

Supongamos que en el Instrumento 3 quedó así para `SQ-12`:

- `Referencia final tronco = derecha`
- `Sistema tronco = izquierda`

Entonces, en la matriz complementaria se crea una fila:

- `SQ-12 | Tronco | derecha | izquierda | No | Discrepancia lateral`

Si además:

- `Referencia final valgo = bilateral`
- `Sistema valgo = bilateral`

Se crea otra fila:

- `SQ-12 | Valgo | bilateral | bilateral | Sí | Coincidencia total`

### Para qué sirve realmente

Esta matriz es la que permite:

- construir matrices de confusión;
- contar verdaderos positivos, falsos positivos, falsos negativos y verdaderos negativos;
- calcular exactitud, precisión, sensibilidad, especificidad y puntaje F1;
- y calcular concordancia como Kappa.

Por eso, aunque en la práctica se presenta como “anexo complementario”, funcionalmente actúa como la base final de integración para el análisis estadístico del estudio.

## 10.2. Qué significa el cuadro “Métrica prevista y su uso”

En la hoja del anexo complementario aparece además un cuadro resumen de **“Métrica prevista y su uso”**.

Ese cuadro **no forma parte de las columnas fila por fila** de la matriz complementaria.

Su función no es registrar casos, sino servir como guía metodológica para recordar:

- qué métrica se calculará;
- para qué servirá;
- y cómo se interpretará dentro de la tesis.

Por tanto:

- las **columnas reales de la matriz complementaria** son:
  `Código del video`, `Patrón evaluado`, `Referencia final`, `Salida del sistema`, `Coincidencia`, `Observación`;
- mientras que el cuadro **“Métrica prevista y su uso”** es una tabla de apoyo metodológico separada.

### Ejemplo de lectura correcta de ese cuadro

- `Exactitud`
  Uso:
  ver la proporción global de coincidencias correctas del sistema.

- `Precisión`
  Uso:
  evaluar cuántas detecciones positivas del sistema fueron correctas.

- `Sensibilidad`
  Uso:
  evaluar cuántos casos positivos reales fueron detectados.

- `Especificidad`
  Uso:
  evaluar cuántos casos negativos reales fueron reconocidos como negativos.

- `Puntaje F1`
  Uso:
  resumir precisión y sensibilidad cuando interesa balancear ambas.

- `Índice Kappa`
  Uso:
  medir concordancia más allá del azar entre referencia final y sistema.

En resumen:

- la **matriz complementaria** guarda los datos por caso;
- el cuadro **“Métrica prevista y su uso”** explica qué harás con esos datos después.

## 11. Afinamiento recomendado de los instrumentos

Los instrumentos sí eran funcionales, pero les faltaba explicitar mejor el uso operativo. El principal ajuste recomendado es:

- mantener el **Instrumento 1** como ficha maestra de entrada;
- mantener el **Instrumento 2** como salida automática del sistema;
- mantener el **Instrumento 3** como comparación experto-sistema;
- mantener la **ficha institucional de validación por juicio de expertos** como documento externo de respaldo metodológico;
- mantener la **matriz final de consolidación** como anexo complementario para métricas;
- y dejar visible en el anexo la codificación sugerida.

Eso evita confusión entre:

- lo que observa el investigador al aceptar el video;
- lo que calcula el sistema;
- y lo que juzga el experto.

## 12. Conclusión operativa

En un caso real:

- el **Instrumento 1** decide si el video entra y documenta si los puntos anatómicos clave están disponibles;
- el **Instrumento 2** documenta lo que hizo el software;
- el **Instrumento 3** compara software versus expertos;
- y la **Matriz de análisis** convierte esa comparación en evidencia cuantitativa.

Por tanto, en los casilleros de landmarks del Anexo 1, la mejor opción no es una `X` simple, sino una codificación breve como `B / I / D / O / N`, porque refleja mejor la calidad real del caso y fortalece la defensa metodológica del estudio.

## 13. Mejora operativa del Instrumento 1

Con la incorporación de leyendas operativas dentro del Instrumento 1, su uso cambia en un punto importante: ya no funciona solo como una ficha descriptiva de entrada, sino también como una ficha con **reglas explícitas de decisión**.

Antes, campos como `iluminación`, `fondo visual`, `oclusiones` o `video válido para procesamiento` podían quedar demasiado abiertos al criterio del investigador. Ahora, la ficha incluye definiciones resumidas que permiten aplicar una misma lógica de registro y aceptación en todos los casos.

### 13.1. Cómo se usa ahora el Instrumento 1

El flujo recomendado queda así:

1. se registran los datos generales del video;
2. se evalúan las condiciones técnicas con escalas cerradas;
3. se codifican los landmarks con la leyenda definida;
4. se contrasta esa información con el criterio de aceptación del video;
5. se decide si el caso es `válido para procesamiento`;
6. y, si no lo es, se registra el motivo de exclusión.

### 13.2. Qué aportan las nuevas leyendas

Las nuevas leyendas cumplen tres funciones metodológicas:

- reducen la ambigüedad en el llenado de la ficha;
- vuelven trazable la decisión de inclusión o exclusión del video;
- y facilitan la validación del instrumento por expertos, porque la ficha ya no depende de interpretaciones implícitas.

### 13.3. Relación entre la tesis y el instrumento

La tesis mantiene la explicación metodológica general del instrumento, mientras que la hoja Excel incorpora la versión operativa resumida. No se trata de duplicación innecesaria, sino de dos niveles complementarios:

- en la **tesis** se justifica el uso del instrumento;
- en el **instrumento** se deja visible cómo debe aplicarse.

### 13.4. Presentación recomendada

Para mejorar la lectura, las leyendas del Instrumento 1 conviene presentarlas como **mini-tablas** en lugar de bloques largos de texto. Eso permite que el investigador o el validador identifiquen rápidamente:

- la codificación de landmarks;
- la escala de iluminación;
- la escala de fondo visual;
- la escala de visibilidad corporal;
- la escala de oclusiones;
- y el criterio de aceptación del video.

Esta mejora es principalmente de forma, pero fortalece el uso real de la ficha y su defensa metodológica.
