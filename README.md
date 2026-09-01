# Plataforma Multi-Conjunto de Control Vehicular

Sistema que permite administrar **múltiples conjuntos residenciales** (unidades de negocio) desde
una sola plataforma. Cada conjunto tiene su propia marca (nombre, logo y colores), sus propios
residentes/vehículos/torres/apartamentos, y su propio equipo (Super Administrador + Vigilantes),
completamente aislado de los demás conjuntos.

## Estructura del repositorio

```
CONJUNTO/
├── Backend/     # API FastAPI + PostgreSQL — ver Backend/README.md
├── Frontend/    # React + TypeScript + Vite — ver Frontend/README.md
└── docker-compose.yml
```

## Roles

| Rol | Qué gestiona |
|---|---|
| **Administrador de Plataforma** | Crea y gestiona las unidades de negocio (conjuntos): nombre, logo, colores, y su Super Administrador inicial |
| **Super Administrador** | Todo dentro de su propio conjunto: residentes, vehículos, torres, apartamentos y usuarios |
| **Vigilante** | Únicamente la consulta rápida de placas de su propio conjunto |

## Ejecución rápida (Docker)

```bash
cp .env.example .env    # ajustar POSTGRES_PASSWORD, SECRET_KEY, etc.
docker compose up --build
```

Levanta PostgreSQL, el backend (con migraciones y siembra automáticas) y el frontend:

- **Frontend:** http://localhost:5173
- **Backend / docs:** http://localhost:8010/docs (o el puerto que definas en `.env`)

## Primer uso

1. Entra a **http://localhost:5173/plataforma/login** con la cuenta de Administrador de Plataforma
   sembrada automáticamente al arrancar (correo y contraseña definidos en las variables de entorno
   `ADMIN_PLATAFORMA_CORREO` / `ADMIN_PLATAFORMA_PASSWORD` de tu `.env` — ver
   [Backend/README.md](Backend/README.md#11-credenciales-iniciales-de-desarrollo)).
2. Crea tu primera unidad de negocio (nombre, código/slug, colores, logo opcional, y los datos de
   su Super Administrador).
3. Ve a **http://localhost:5173**, escribe el código (slug) de esa unidad, e inicia sesión con el
   Super Administrador que acabas de crear.
4. Desde ahí: registra torres, apartamentos, residentes y vehículos, o crea usuarios `VIGILANTE`
   para el puesto de seguridad.

## Documentación detallada

- [Backend/README.md](Backend/README.md) — arquitectura, variables de entorno, migraciones,
  endpoints, pruebas.
- [Frontend/README.md](Frontend/README.md) — estructura, sistema de diseño, theming dinámico por
  conjunto, ejecución y build.
