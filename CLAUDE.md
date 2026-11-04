# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Multi-tenant vehicle-control platform for residential complexes ("conjuntos" / "unidades de negocio"). Monorepo: `Backend/` (FastAPI + async SQLAlchemy + PostgreSQL) and `Frontend/` (React 18 + TS + Vite + Tailwind + TanStack Query). Code, identifiers, comments, error messages, and commit messages are in **Spanish** — keep that convention. Detailed docs: [README.md](README.md), [Backend/README.md](Backend/README.md), [Frontend/README.md](Frontend/README.md).

## Commands

Full stack (from repo root, not from `Backend/`): `cp .env.example .env && docker compose up --build`. The backend entrypoint runs `alembic upgrade head` + seed before uvicorn.

Backend (from `Backend/`, Python 3.12+):
```bash
pip install -r requirements.txt
alembic upgrade head && python -m app.infrastructure.database.seed
uvicorn app.main:app --reload
pytest -v                                                    # all tests (SQLite in-memory, no Postgres needed)
pytest tests/integration/test_vehiculos_api.py               # one file
pytest tests/unit/test_placa.py -k "<substring>" -v         # one test by name
alembic revision --autogenerate -m "mensaje"                 # new migration
```
Migration files are named `YYYYMMDDNNNN_descripcion.py` in `Backend/migrations/versions/`.

Frontend (from `Frontend/`):
```bash
npm run dev       # Vite dev server
npm run build     # tsc -b && vite build — this is the type-check
```
`npm run lint` exists but there is no ESLint config file in the repo, so it won't work as-is.

## Backend architecture

Clean Architecture, dependencies point inward: `presentation → application → domain ← infrastructure`.

- `domain/` — entities, `Placa` value object, abstract repository interfaces, `ErrorDominio` subclasses (each has a `codigo`), and `ValidadorReglasVehiculo` (PROPIETARIO: max 2 vehicles and never 2 cars; ARRENDATARIO: max 1).
- `application/use_cases/` — one class per action with an `ejecutar(...)` method; DTOs in `application/dto/`.
- `infrastructure/` — ORM models (`database/models.py`), `*_repository_impl.py`, JWT, bcrypt hashing, Excel import/template, logo storage (logos stored as data URIs in the DB row, not on disk).
- `presentation/` — routers in `api/v1/` (registered in `api/v1/router.py`), Pydantic schemas, and DI in `dependencies/`: `repositorios.py` builds repos from the session, `casos_uso.py` has a `caso_uso_*` provider per use case, `autenticacion.py` has auth/role guards.

Adding an endpoint typically touches: domain interface → repo impl → use case → provider in `casos_uso.py` → schema → router.

### Multi-tenancy (critical)
- Every tenant-scoped table has `unidad_negocio_id`; uniqueness constraints (tower code, document, **plate**) are per tenant, not global.
- The tenant id comes **only** from the JWT via the `UnidadNegocioActual` dependency — never from request bodies, query params, or the frontend URL slug. Tenant use cases receive `unidad_negocio_id` explicitly and must verify that every referenced entity belongs to it.
- Role guards: `requerir_super_admin`, `requerir_cualquier_rol` (SUPER_ADMIN + VIGILANTE), `requerir_admin_plataforma`, usually passed as `dependencies=[Depends(...)]` on the route. `ADMIN_PLATAFORMA` has no tenant.

### Errors
Raise domain exceptions; `shared/exceptions/manejador_excepciones.py` converts them to `{"error": true, "mensaje": ..., "codigo": ...}`. **When adding a new error code, add it to `_CODIGO_A_STATUS`** or it falls back to 400.

### Async gotchas
- In request paths use `hashear_password_async` / `verificar_password_async` (bcrypt is offloaded to a thread so it doesn't block the event loop). The sync versions are only for the seed script.
- Login rate limiting (`dependencies/limitador_tasa.py`) is in-process memory; tests reset it via `reiniciar_limitador()` in `conftest.py`.

### Tests
`tests/conftest.py` overrides `obtener_sesion` with in-memory SQLite (`aiosqlite`, `StaticPool`), recreates the schema per test, and autoseeds vehicle/resident types. Fixtures like `unidad_negocio`, `torre_y_apartamento`, `credenciales_admin_plataforma` build tenant data; `cliente` is an httpx `AsyncClient` over ASGI. `asyncio_mode = auto`, so no `@pytest.mark.asyncio` needed. Keep code SQLite-compatible enough for tests to run.

## Frontend architecture

- Routing in `src/app/router.tsx`: `/` (enter tenant slug), `/:slug/login`, `/:slug/consulta-placa` (VIGILANTE + SUPER_ADMIN), `/:slug/admin/*` (SUPER_ADMIN), `/plataforma/*` (ADMIN_PLATAFORMA). The slug is only for branding/login — authorization lives in the JWT.
- `features/tenant/TenantLayout` fetches `GET /business-units/public/{slug}` and sets the tenant's primary color as CSS vars (`--primary`, `--ring`, `--primary-foreground`); the rest of the palette is fixed.
- `services/api-client.ts`: axios instance (`VITE_API_URL`, baked in at build time), tokens in localStorage, single-flight refresh on 401 (skipped for `/auth/login` and `/auth/refresh`), redirects to `/` if refresh fails. Use `obtenerMensajeError(error)` to show backend `mensaje`s.
- One service file per domain in `src/services/`; data fetching via TanStack Query; forms with React Hook Form + Zod; UI primitives in `components/ui/` (shadcn/Radix style). Import alias `@/` → `src/`.
