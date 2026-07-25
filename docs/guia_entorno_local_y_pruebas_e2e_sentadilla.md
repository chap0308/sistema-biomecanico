# Entorno local y pruebas E2E del sistema de sentadilla

## 1. URLs de Supabase

`http://127.0.0.1:54321` es el gateway de API, no una interfaz web. Consultar
su raíz devuelve correctamente:

```json
{"message":"no Route matched with those values"}
```

Las rutas útiles son:

| Servicio | URL |
|---|---|
| Supabase Studio | `http://127.0.0.1:54323` |
| Usuarios de Authentication | `http://127.0.0.1:54323/project/default/auth/users` |
| Table Editor | `http://127.0.0.1:54323/project/default/editor` |
| API REST | `http://127.0.0.1:54321/rest/v1` |
| Mailpit | `http://127.0.0.1:54324` |

En Windows, si el CLI detiene Studio por una comprobación de salud demasiado
estricta, puede iniciarse el entorno conservando los contenedores con:

```powershell
supabase start --ignore-health-check
```

Esto solo es aceptable después de comprobar que PostgreSQL, Auth, Kong y
Studio responden localmente.

## 2. Cuentas locales

Las cuentas canónicas de desarrollo son:

| Rol | Correo |
|---|---|
| Investigador | `investigator@sentadilla.local` |
| Experto 1 | `expert1@sentadilla.local` |
| Experto 2 | `expert2@sentadilla.local` |
| Experto 3 | `expert3@sentadilla.local` |

Contraseña local compartida:

```text
Sentadilla2026!
```

Estas credenciales son exclusivamente locales y no deben utilizarse en un
despliegue real. Pueden recrearse de forma idempotente con:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\seed_squat_local_accounts.py
```

Las identidades se consultan en Authentication y sus roles metodológicos en
la tabla `public.profiles`, columna `squat_role`.

## 3. Fixture del Instrumento 1

El archivo `apps/web/e2e/fixtures/squat-case.ts`:

- genera un código de caso único;
- completa la identificación del video y participante;
- llena las condiciones cerradas del Instrumento 1;
- adjunta por defecto
  `data/sentadilla_bilateral/raw/dev_negativo_001.mp4`;
- permite reemplazar el video con `SQUAT_E2E_UPLOAD_VIDEO`.

La prueba rápida `case-intake.spec.ts` llena el formulario y adjunta el archivo
sin ejecutar el análisis completo.

La prueba `case-analysis.spec.ts` ejecuta registro, análisis, persistencia y
reproducción real del overlay. Por ser costosa, se habilita explícitamente:

```powershell
cd apps\web
$env:SQUAT_E2E_EMAIL="investigator@sentadilla.local"
$env:SQUAT_E2E_PASSWORD="Sentadilla2026!"
$env:SQUAT_E2E_RUN_ANALYSIS="1"
npx playwright test e2e/case-analysis.spec.ts --project=chromium-authenticated
```

## 4. Videos y reportes de Playwright

Para grabar los recorridos:

```powershell
$env:SQUAT_E2E_RECORD_VIDEO="1"
npx playwright test --reporter=html
```

Playwright genera:

```text
apps/web/test-results/<nombre-de-prueba>/video.webm
apps/web/playwright-report/index.html
```

`test-results` se limpia al iniciar otra ejecución. Por ello, las evidencias
durables de los flujos principales se copiaron a:

```text
docs/evidencias/fase6/playwright/flujo_registro_analisis_caso.webm
docs/evidencias/fase6/playwright/flujo_evaluador_experto.webm
```

## 5. Compatibilidad de los videos analizados

OpenCV produce primero un archivo intermedio. FFmpeg genera después el archivo
publicado con:

- códec H.264/AVC;
- etiqueta `avc1`;
- formato de píxel `yuv420p`;
- metadatos `faststart`.

La prueba Playwright no se limita a comprobar que exista `<video>`: valida que
Chrome pueda cargar metadatos, obtener dimensiones, ejecutar `play()` y buscar
un instante posterior a cero.

Los artefactos antiguos pueden normalizarse con:

```powershell
D:\anaconda4\envs\analisis-bio\python.exe scripts\normalize_squat_output_videos.py
```
