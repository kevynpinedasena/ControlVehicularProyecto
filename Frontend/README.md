# Frontend — Plataforma Multi-Conjunto de Control Vehicular

Aplicación React + TypeScript que consume la API del backend. Cada conjunto residencial (unidad de
negocio) se identifica por un **código (slug)** en la URL, y la interfaz se "tiñe" dinámicamente
con el logo y el color primario configurados por el Administrador de Plataforma para esa unidad.

## Tecnologías

React 18 · TypeScript · Vite · Tailwind CSS · Framer Motion · React Router · TanStack Query ·
React Hook Form + Zod · Docker (build multi-stage con Nginx).

## Estructura

```
Frontend/
├── src/
│   ├── app/            # Router principal
│   ├── components/ui/  # Sistema de diseño (Button, Input, Dialog, Select, ...)
│   ├── components/shared/
│   ├── features/
│   │   ├── auth/        # Login, rutas protegidas
│   │   ├── tenant/      # Selector de unidad de negocio, theming dinámico
│   │   ├── platform/    # Administración de plataforma (unidades de negocio)
│   │   ├── residents/ vehicles/ locations/ users/
│   │   └── plate-search/  # Consulta de placa (pantalla del vigilante)
│   ├── layouts/         # AdminLayout, VigilanteLayout, PlatformLayout
│   ├── services/        # Capa de acceso a la API (un archivo por dominio)
│   ├── hooks/ lib/ types/
│   └── main.tsx
├── Dockerfile           # build con Node + serve con Nginx
├── nginx.conf
└── .env.example
```

## Rutas principales

| Ruta | Quién la ve |
|---|---|
| `/` | Pantalla pública para ingresar el código del conjunto |
| `/:slug/login` | Login del conjunto (con su logo y color) |
| `/:slug/consulta-placa` | Vigilante y Super Administrador |
| `/:slug/admin/*` | Solo Super Administrador (dashboard, residentes, vehículos, torres/apartamentos, usuarios) |
| `/plataforma/login` | Administrador de Plataforma |
| `/plataforma/business-units` | Gestión de unidades de negocio |

El backend nunca confía en el `slug` de la URL para autorizar nada — solo se usa para mostrar la
marca correcta y armar el login; la unidad de negocio real del usuario viaja en su JWT.

## Theming dinámico

`TenantLayout` obtiene la info pública de la unidad (`GET /business-units/public/{slug}`) y aplica
su color primario como variables CSS (`--primary`, `--ring`, `--primary-foreground`) sobre el
`:root`, además de mostrar su logo (con `TenantLogo`, que cae a un ícono genérico si la imagen no
carga). El resto de la paleta (fondos, texto, bordes) se mantiene fija para garantizar buen
contraste sin importar el color que elija cada conjunto.

## Variables de entorno

```
VITE_API_URL=http://localhost:8010/api/v1
```

Se usa en build-time (Vite la incrusta en el bundle), por lo que en Docker se pasa como build arg
(`docker-compose.yml` ya lo hace automáticamente desde `.env`).

## Ejecución local (sin Docker)

```bash
cd Frontend
npm install
cp .env.example .env   # apuntar VITE_API_URL al backend
npm run dev
```

## Ejecución con Docker

Desde la raíz del proyecto:

```bash
docker compose up --build frontend
```

Sirve el build de producción (Vite + Nginx) en el puerto configurado (`FRONTEND_PORT`, por defecto
5173).

## Build de producción

```bash
npm run build     # type-check + build a dist/
npm run preview   # previsualizar el build localmente
```
