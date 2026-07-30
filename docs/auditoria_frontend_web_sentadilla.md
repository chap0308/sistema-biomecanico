# Auditoría técnica y visual del frontend de sentadilla bilateral

## 1. Alcance

La revisión se concentró en `apps/web` y cubrió la estructura de Next.js,
renderizado, autenticación, accesibilidad, diseño adaptable, carga de recursos,
metadatos, manejo de errores y pruebas automatizadas. No se modificaron las
reglas biomecánicas ni el backend FastAPI.

## 2. Mejoras aplicadas

### 2.1. Identidad visual y experiencia

- Se conservó la dirección visual clínica-editorial basada en tonos crema,
  petróleo y cian, evitando recursos decorativos que compitan con los videos,
  métricas y evidencias.
- Se agregó tema oscuro con preferencia del sistema y persistencia entre rutas.
- Se incorporó un control accesible para cambiar el tema en las vistas públicas
  y protegidas.
- Se mejoró el encabezado protegido con comportamiento fijo, transparencia y
  adaptación para pantallas estrechas.
- Se añadieron transiciones de aparición discretas y una alternativa sin
  movimiento para usuarios con `prefers-reduced-motion`.
- Se agregó un icono propio de la aplicación y estados globales para error y
  página no encontrada.

### 2.2. Next.js y React

- Se mantuvo el App Router, los Server Components y el prerenderizado parcial
  ya configurado mediante Cache Components.
- La consulta del perfil autenticado se memoiza con `cache()` de React durante
  una misma solicitud. Esto evita consultas repetidas sin conservar
  autorizaciones entre usuarios o solicitudes.
- El espacio de explicabilidad, que incluye las gráficas de Recharts, se carga
  de forma diferida. Así, el detalle inicial del caso no necesita evaluar esa
  interfaz pesada hasta que el navegador la requiera.
- Se estabilizaron valores de contexto, claves de listas y formateadores
  reutilizados para reducir trabajo repetido de renderizado.
- Los estados pendientes de inicio de sesión, cierre de sesión, registro y carga
  de videos se liberan mediante `finally`, incluso cuando ocurre un error.

### 2.3. Accesibilidad y adaptación

- Se agregaron nombres accesibles a controles de selección sin etiqueta
  explícita.
- Se eliminó un rol redundante de navegación en la paginación.
- Se verificó navegación por teclado, enlace de salto al contenido y ausencia de
  desbordamiento horizontal en vista móvil.
- El tema oscuro mantiene los colores semánticos de fondo, texto, borde,
  estado y énfasis, en lugar de invertir colores de forma global.

### 2.4. Metadatos y exposición

- Se añadieron título, descripción, nombre de aplicación y palabras clave.
- Se configuró `noindex` y `nofollow` porque el sistema contiene datos de una
  investigación y no debe indexarse como un sitio público.
- Las rutas principales incorporan títulos contextuales.

## 3. Decisiones deliberadas

### 3.1. Sesión y caché

No se agregó una caché temporal propia para sesiones o roles. El proxy de
Supabase renueva y valida los tokens, mientras que `cache()` solo deduplica la
consulta del perfil dentro del render actual. Una caché persistente de
autorización podría mantener permisos revocados o mezclar información entre
solicitudes.

### 3.2. Navegaciones completas

Dos enlaces internos sensibles conservan navegación completa mediante `<a>`.
Anteriormente, la transición cliente de React Server Components dejó la
interfaz en una ruta anterior pese a recibir respuesta HTTP 200. Se priorizó la
estabilidad demostrada sobre la advertencia genérica de usar `Link`.

### 3.3. Separación de componentes

No se fragmentaron indiscriminadamente los formularios y espacios de análisis
grandes. La primera optimización aplicada fue separar dinámicamente la sección
de gráficas, que sí produce una reducción de carga. Una división adicional debe
realizarse por responsabilidades funcionales y acompañarse de pruebas para no
reintroducir errores de sincronización entre video, repetición y formularios.

## 4. Verificación

| Verificación | Resultado |
|---|---|
| ESLint | Sin errores |
| TypeScript y compilación Next.js | Compilación de producción correcta |
| Vitest | 29 pruebas aprobadas en 12 archivos |
| Playwright público | 4 pruebas aprobadas |
| Playwright autenticado | 9 pruebas aprobadas y 4 omitidas por fixtures opcionales |
| React Doctor | Mejora de 63 a 69 puntos |
| Medición local de portada | 25 recursos, aproximadamente 355 KB transferidos |
| Diseño adaptable | Sin desbordamiento horizontal en la portada móvil |

Los avisos restantes de React Doctor corresponden principalmente a componentes
complejos ya cubiertos por pruebas, código base de shadcn y las navegaciones
completas mantenidas por estabilidad.

## 5. Trabajo posterior recomendado

1. Ejecutar Lighthouse y pruebas E2E contra el despliegue de producción, donde
   las métricas de red, caché y compresión sean representativas.
2. Dividir el formulario experto y el espacio de explicabilidad únicamente
   cuando se agreguen nuevas responsabilidades o se detecte un problema medible
   de mantenimiento o rendimiento.
3. Auditar las políticas RLS, expiración de sesión y recuperación de errores con
   Supabase desplegado, no solo con la instancia local.
4. Mantener animaciones decorativas fuera de las pantallas de análisis; el
   movimiento visual debe explicar estados, fases o transiciones del estudio.

## 6. Referencias de diseño evaluadas

- Hallmark: criterios para evitar interfaces genéricas o excesivamente
  decorativas.
- Refero Styles y UI Skills: patrones de jerarquía, densidad y revisión de
  interfaces.
- shadcn/ui: implementación recomendada de tema oscuro con `next-themes`.
- Orbs: evaluado como recurso visual, pero descartado por no aportar a la
  lectura del análisis biomecánico.
