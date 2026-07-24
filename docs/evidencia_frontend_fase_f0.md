# Evidencia de la fase F0 del frontend

## 1. Objetivo

Preparar una base reproducible para la interfaz web sin duplicar la lógica biomecánica implementada en Python.

## 2. Implementación

La aplicación fue creada en `apps/web/` con:

- Next.js 16.2 y App Router;
- TypeScript;
- React 19;
- Tailwind CSS 4;
- shadcn/ui con componentes basados en Base UI;
- Cache Components habilitado;
- rutas tipadas;
- Vitest;
- Playwright;
- tipos TypeScript generados desde los contratos JSON Schema del backend.

El shell visual adopta la dirección de laboratorio de movimiento definida en el plan frontend. La página inicial comunica que se trata de un prototipo de investigación y presenta el flujo desde el registro técnico hasta la evidencia.

## 3. Decisiones SSR

Cache Components está habilitado para permitir una composición con contenido estático, contenido cacheado y contenido dinámico bajo límites `Suspense`.

No se cachearán de manera compartida:

- sesiones;
- datos privados del investigador;
- asignaciones de expertos;
- evaluaciones;
- resultados computacionales restringidos.

Estos datos dependerán de cookies o parámetros de solicitud y se resolverán en tiempo de ejecución. El uso de `use cache` se reservará para contenido público o invariable que no contenga identidad ni resultados privados.

La paginación y los filtros del historial se representarán mediante `searchParams`. Esto hace que las consultas sean reproducibles, compartibles y compatibles con renderizado del servidor.

## 4. Estado local

Zustand no se incorporó en esta fase. Los formularios se resolverán con React Hook Form y el archivo de video permanecerá en el componente cliente responsable de la carga.

Solo se añadirá un almacén global si aparece estado cliente compartido entre rutas que no pueda representarse correctamente mediante:

- URL;
- datos del servidor;
- estado local de React;
- contexto acotado;
- estado del formulario.

## 5. Contratos

Los archivos:

- `src/types/squat-case-record.ts`;
- `src/types/squat-case-report.ts`;

se generan desde:

- `config/squat/schemas/squat_case_record.schema.json`;
- `config/squat/schemas/squat_case_report.schema.json`.

Esta estrategia evita mantener manualmente una segunda definición de los instrumentos 1 y 2 en TypeScript.

## 6. Pruebas ejecutadas

```powershell
npm run web:lint
npm run web:test
npm run test:e2e --workspace @sistema-biomecanico/web
npm run web:build
```

Resultados:

- ESLint sin errores;
- Vitest: prueba unitaria aprobada;
- Playwright: recorrido inicial aprobado en Chromium;
- Next.js: compilación de producción aprobada;
- página inicial prerenderizada con Cache Components activo.

## 7. Relación con el desarrollo posterior

Esta fase no valida todavía un objetivo biomecánico de la tesis. Funciona como infraestructura de presentación para las evidencias ya generadas por el pipeline y como base de las fases:

1. autenticación y persistencia;
2. registro del Instrumento 1;
3. procesamiento y visualización del Instrumento 2;
4. evaluación ciega mediante el Instrumento 3;
5. comparación y exportación.
