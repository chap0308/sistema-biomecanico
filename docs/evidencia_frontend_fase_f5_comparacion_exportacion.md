# Evidencia de la fase F5: comparación y exportación

## 1. Propósito

La fase F5 transforma las evaluaciones bloqueadas del Instrumento 3 en una
referencia experta consolidada, la compara con la salida del sistema y genera
las métricas necesarias para evaluar su desempeño técnico.

La matriz de análisis producida en esta fase es una salida derivada. No se
considera un cuarto instrumento de recolección de datos.

## 2. Consolidación de la referencia experta

La consolidación se realiza de forma independiente para tronco, pelvis, valgo
y asimetría bilateral.

| Situación | Regla aplicada |
|---|---|
| Dos evaluadores coinciden | Coincidencia directa |
| Tres evaluadores y al menos dos coinciden | Mayoría absoluta |
| Dos evaluadores discrepan | Consenso guiado registrado por el investigador |
| Tres evaluadores emiten tres clasificaciones diferentes | Consenso guiado registrado por el investigador |
| Menos de dos evaluaciones enviadas | Evaluaciones pendientes |

El consenso guiado exige almacenar la clasificación acordada, la lateralidad
cuando corresponde y una observación que documente el criterio empleado.

## 3. Comparación y métricas

La detección de presencia se analiza de forma binaria:

- verdadero positivo: referencia presente y sistema presente;
- verdadero negativo: referencia ausente y sistema ausente;
- falso positivo: referencia ausente y sistema presente;
- falso negativo: referencia presente y sistema ausente.

Las fórmulas implementadas son:

```text
Exactitud = (VP + VN) / (VP + VN + FP + FN)
Precisión = VP / (VP + FP)
Sensibilidad = VP / (VP + FN)
Especificidad = VN / (VN + FP)
F1 = 2VP / (2VP + FP + FN)
Kappa = (acuerdo observado - acuerdo esperado) /
        (1 - acuerdo esperado)
```

F1 evalúa la detección de presencia sin ocultar errores de lateralidad. El
acuerdo exacto y Kappa utilizan etiquetas categóricas que conservan dirección
y lateralidad para tronco, pelvis y valgo. La asimetría bilateral se compara
como presente o ausente porque su indicador principal no exige una dirección
final. Kappa se calcula por patrón; el valor general corresponde a la media
macro de los valores por patrón que tengan denominador válido.

Los pares donde la referencia o el sistema sean no concluyentes se excluyen
del denominador y se reportan mediante un contador independiente. Cuando una
fórmula tiene denominador cero, la interfaz presenta `N/D` en vez de inventar
un valor.

## 4. Persistencia y seguridad

Los consensos guiados se almacenan en
`public.squat_expert_references`. La tabla:

- admite una referencia por caso y patrón;
- registra el investigador responsable;
- mantiene fecha de creación y actualización;
- está protegida mediante RLS para el rol investigador;
- no es accesible al evaluador experto.

Las evaluaciones enviadas permanecen inmutables. F5 consume únicamente
evaluaciones con estado final.

## 5. Interfaz

La ruta `/cases/[caseId]/comparison` permite al investigador:

1. verificar cuántos evaluadores fueron asignados y cuántos enviaron su ficha;
2. revisar las clasificaciones expertas sin revelar identidades en la tabla;
3. visualizar la salida del sistema;
4. identificar coincidencias y discrepancias;
5. registrar consenso guiado cuando corresponde;
6. consultar métricas generales y por patrón;
7. descargar el libro Excel y el reporte PDF.

Una advertencia indica cuando existen menos de diez pares incluidos, porque
las métricas del piloto no deben interpretarse como desempeño definitivo.

## 6. Exportaciones

El libro Excel contiene:

- `Instrumento 1`: registro y revisión del video;
- `Instrumento 2`: procesamiento, calidad, variables y reglas;
- `Instrumento 3`: evaluadores, sistema y referencia final;
- `Matriz de análisis`: una fila por patrón;
- `Métricas`: resultados generales y por patrón.

El PDF resume el caso, la comparación, las métricas acumuladas y la limitación
de que los resultados no constituyen un diagnóstico clínico.

Las exportaciones comparativas requieren que los cuatro patrones tengan
referencia final. Los archivos se generan desde FastAPI con datos persistidos
y se descargan mediante un proxy autenticado de Next.js.

## 7. Endpoints implementados

| Operación | Endpoint |
|---|---|
| Comparación de un caso | `GET /api/v1/squat/cases/{case_id}/comparison` |
| Registrar consenso | `PUT /api/v1/squat/cases/{case_id}/comparison/references/{pattern}` |
| Métricas acumuladas | `GET /api/v1/squat/comparison/metrics` |
| Libro Excel | `GET /api/v1/squat/cases/{case_id}/exports/instruments.xlsx` |
| Reporte PDF | `GET /api/v1/squat/cases/{case_id}/exports/report.pdf` |

## 8. Validación realizada

La integración local utilizó un caso persistido con dos evaluaciones enviadas.
Dos patrones se consolidaron por coincidencia directa y dos requirieron
consenso guiado. Después de registrar los consensos:

- los cuatro patrones quedaron consolidados;
- tres pares fueron incluidos;
- un par no concluyente fue excluido;
- Excel y PDF respondieron correctamente con sus tipos MIME;
- Playwright abrió la comparación y descargó ambos archivos.

Los valores obtenidos en esta prueba técnica no representan resultados de la
tesis ni sustituyen la futura evaluación con la muestra definitiva.
