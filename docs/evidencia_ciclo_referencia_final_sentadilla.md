# Ciclo de asignación y referencia final

## Estados del caso

La comparación experta-sistema utiliza un ciclo irreversible e independiente
del estado del procesamiento computacional:

| Estado | Evaluadores | Referencias finales | Visibilidad para expertos |
|---|---|---|---|
| `open` | Se pueden agregar o retirar, con un máximo de tres | Bloqueadas | Resultado del sistema oculto |
| `in_progress` | Nómina bloqueada | Se pueden registrar y editar | Resultado del sistema oculto |
| `closed` | Nómina bloqueada | Bloqueadas definitivamente | Resultado del sistema visible |

El inicio de la referencia final requiere que todos los evaluadores asignados
hayan enviado su evaluación. Esto evita que una respuesta tardía cambie la
base experta después de iniciar la consolidación.

## Retiro de evaluadores

Mientras el caso permanezca abierto, el investigador puede retirar a un
evaluador. La eliminación es en cascada: también elimina su borrador o respuesta
y sus clasificaciones por repetición. La interfaz advierte esta consecuencia
porque puede modificar la referencia experta y las métricas derivadas.

## Referencias finales

Cada repetición y patrón conserva una referencia final independiente. Durante
la revisión, el investigador puede confirmar o modificar la clasificación y
añadir una observación opcional. La observación documenta decisiones que
requieran contexto, pero no es necesaria cuando la clasificación se explica
por coincidencia directa o mayoría absoluta.

El cierre solo se habilita cuando todas las combinaciones de repetición y patrón
tienen una referencia consolidada. Después del cierre no se permite editar,
agregar ni retirar evaluadores. Los expertos asignados pueden entonces consultar
las clasificaciones del sistema sin comprometer el cegamiento de su evaluación.

## Exportación PDF

La tabla comparativa se pagina en bloques de hasta ocho filas. Las métricas
acumuladas se ubican en una página separada para evitar solapamientos cuando el
video contiene varias repeticiones.
