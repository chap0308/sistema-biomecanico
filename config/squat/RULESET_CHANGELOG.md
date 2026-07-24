# Historial de conjuntos de reglas

## 0.1.0-provisional - 2026-07-23

Estado: desarrollo.

Base:

- fórmulas geométricas implementadas en la Fase 4;
- revisión exploratoria de siete videos controlados;
- bandas conservadoras con salida `no_concluyente`;
- consenso mínimo de dos de tres repeticiones.

Videos utilizados:

- `dev_negativo_001`;
- `dev_pelvis_der_001`;
- `dev_pelvis_izq_001`;
- `dev_tronco_der_001`;
- `dev_tronco_izq_001`;
- `dev_valgo_der_001`;
- `dev_valgo_izq_001`.

Limitaciones:

- el valgo derecho intentado no fue confirmado por la geometría;
- falta un caso de valgo bilateral;
- existen pocos negativos y una sola persona;
- los hallazgos de asimetría requieren más casos para revisar sensibilidad;
- no se ha incorporado todavía retroalimentación experta.

Esta versión no puede utilizarse como resultado final de desempeño ni como
punto de corte clínico.

### Verificación exploratoria - 2026-07-24

Se aplicó la misma versión, sin modificar umbrales, a 12 videos nuevos:

- 11 casos fueron aptos para clasificación;
- 10 coincidieron exactamente con el patrón principal intentado;
- 1 caso de valgo bilateral coincidió parcialmente al detectarse solo el lado
  izquierdo;
- 1 caso de pelvis derecha fue excluido por contener dos repeticiones;
- se observaron salidas multietiqueta y patrones no concluyentes.

Esta ronda no produjo cambios en el conjunto de reglas. Los resultados se
registran en `docs/evaluacion_lote_piloto_002_multietiqueta.md`.
