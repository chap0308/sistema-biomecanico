# Reutilización del proyecto actual para la línea de sentadilla bilateral

## Propósito de este archivo

Este archivo queda como complemento breve del plan maestro y no como documento paralelo.

Su función es una sola: registrar la decisión de que la tesis **sí reutilizará el proyecto actual** y recordar dónde está detallado cada aspecto.

## Decisión consolidada

La línea de sentadilla bilateral:

- se desarrollará dentro del repositorio actual;
- reutilizará infraestructura técnica existente;
- aislará su lógica dentro de un módulo propio;
- y podrá separarse más adelante, si el módulo madura y conviene independizarlo.

## Dónde quedó cada detalle

- arquitectura general del sistema: ver [plan_desarrollo_tecnico_sentadilla.md](/D:/sistema-biomecanico/docs/plan_desarrollo_tecnico_sentadilla.md), secciones 5 y 8;
- reutilización de componentes actuales: ver [plan_desarrollo_tecnico_sentadilla.md](/D:/sistema-biomecanico/docs/plan_desarrollo_tecnico_sentadilla.md), sección 3;
- stack real de tecnologías: ver [plan_desarrollo_tecnico_sentadilla.md](/D:/sistema-biomecanico/docs/plan_desarrollo_tecnico_sentadilla.md), secciones 5.3 y 8;
- estructura propuesta de `src/squat/` y `data/sentadilla_bilateral/`: ver [backlog_tecnico_sentadilla_fase0_fase1.md](/D:/sistema-biomecanico/docs/backlog_tecnico_sentadilla_fase0_fase1.md);
- estrategia de Git y repo público: ver [plan_desarrollo_tecnico_sentadilla.md](/D:/sistema-biomecanico/docs/plan_desarrollo_tecnico_sentadilla.md), secciones 8 y 13.1.

## Resumen ejecutivo

No conviene abrir otro proyecto en esta etapa. Conviene:

1. trabajar en una rama dedicada;
2. crear un módulo aislado de sentadilla;
3. reutilizar pose, geometría, debug, overlays, CSV, plots y pruebas;
4. mantener en GitHub solo material técnico apto para un repositorio público;
5. reservar Google Drive para entregables institucionales o sensibles.

o, si prefieres una más explícita:

```text
codex/sentadilla-bilateral-dev
```

Estrategia recomendada:

- un commit para estructura y contratos;
- un commit para extracción de pose en video;
- un commit para segmentación;
- un commit para métricas;
- un commit para reglas;
- un commit para anonimización;
- un commit para pruebas.

Si luego más adelante quieres separar el módulo en otro repositorio, esa historia limpia de commits te lo facilitará mucho.

## 8. Pixelado o anonimización del rostro

Sí debe incluirse como parte real del desarrollo, no solo como una nota ética.

### Qué necesitamos anonimizar

Como mínimo:

- ojos;
- boca.

Como alternativa más robusta:

- toda la región facial.

### Tecnología recomendable

Ruta más simple y coherente con el proyecto:

- detección facial con MediaPipe Face Mesh o detector facial liviano;
- construcción de región de interés facial;
- pixelado o desenfoque gaussiano con OpenCV;
- exportación del video anonimizado para revisión y almacenamiento.

### Recomendación práctica

Para tesis, la opción más sólida es:

- anonimizar **toda la cara** en el video exportado,
- conservar si hace falta landmarks corporales visibles,
- y no depender de pixelar solo ojos y boca, porque eso puede fallar si la cabeza rota.

### Dónde entra en el flujo

Hay dos opciones:

1. anonimizar antes del procesamiento completo;
2. anonimizar en artefactos de salida y revisión.

La más segura para no afectar pose corporal es:

- procesar el video original localmente;
- exportar overlays, vistas de revisión y archivos compartibles con anonimización facial.

Así se preserva la calidad del análisis y se protege la identidad en los materiales mostrados.

## 9. Conclusión operativa

La tesis sí puede desarrollarse dentro del proyecto actual sin volverse confusa, siempre que:

- la línea de sentadilla se aísle bien;
- reutilicemos infraestructura y no significado biomecánico ajeno;
- el nuevo flujo tenga su propia estructura, pruebas, salidas y scripts;
- y el manejo de Git se haga en una rama específica con commits por fase.

La decisión más eficiente ahora no es separar el repositorio, sino **separar claramente el módulo dentro del repositorio**.

## 10. Politica de commits y publicacion

La rama de desarrollo de esta linea es `codex/sentadilla-bilateral-dev`.

A partir de la linea base de las fases 0 a 2, cada fase o incremento verificable debe:

1. incluir solamente los archivos tecnicos utilizados o modificados por el incremento;
2. ejecutar sus pruebas y validaciones antes del commit;
3. usar un mensaje descriptivo que identifique la fase o capacidad implementada;
4. hacer push inmediato a la rama de desarrollo despues del commit.

El staging se realizara mediante rutas explicitas. No se publicaran videos crudos, resultados generados, registros reales de participantes, documentos institucionales ni archivos con datos personales. Esta separacion permite extraer posteriormente `src/squat/`, sus scripts, pruebas, contratos de datos y documentacion tecnica hacia un repositorio independiente.
