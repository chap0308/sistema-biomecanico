# Frontend de sentadilla bilateral

Aplicación Next.js para registrar casos, ejecutar el análisis de sentadilla bilateral y presentar evidencia técnica alineada con los instrumentos de la tesis.

## Requisitos

- Node.js 20 o superior.
- API FastAPI disponible en `http://127.0.0.1:8000`.
- Supabase local para las fases con autenticación y persistencia.

## Comandos desde la raíz

```powershell
npm run web:dev
npm run web:lint
npm run web:test
npm run web:build
```

## Comandos desde `apps/web`

```powershell
npm run generate:contracts
npm run test:e2e
```

Los tipos de `src/types/squat-case-*.ts` son generados desde los JSON Schema de `config/squat/schemas/`. No deben editarse manualmente.

## Decisiones

- App Router y Server Components por defecto.
- Cache Components habilitado.
- Datos autenticados resueltos en tiempo de solicitud mediante Supabase SSR.
- FastAPI conserva toda la lógica biomecánica y de exportación.
- Estado compartible, como página y filtros, se representa en la URL.
- No se utiliza Zustand mientras el estado local de React y los formularios sean suficientes.
