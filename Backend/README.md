# Backend — Plataforma Multi-Conjunto de Control Vehicular

API REST multi-tenant construida con FastAPI. Cada **unidad de negocio** (conjunto residencial)
tiene sus propios residentes, vehículos, torres, apartamentos y usuarios, completamente aislados
del resto de las unidades. Un **Administrador de Plataforma** crea y gestiona las unidades de
negocio; cada unidad tiene su propio **Super Administrador**, con control total pero limitado a su
propio conjunto.

## 1. Requisitos

- Python 3.12+
- PostgreSQL 16 (o Docker, que lo incluye)
- Docker y Docker Compose (para ejecución containerizada)

## 2. Tecnologías utilizadas

FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL · Alembic · Pydantic v2 · JWT (python-jose) ·
Passlib/bcrypt · Pytest · Docker.

## 3. Arquitectura

Clean Architecture con 4 capas y dependencia unidireccional hacia el dominio:

```
presentation → application → domain ← infrastructure
```

- **`domain/`**: entidades (`UnidadNegocio`, `Usuario`, `Torre`, `Apartamento`, `Residente`,
  `Vehiculo`, `Bloque`, `Parqueadero`, `TipoResidente`, `TipoVehiculo`), value objects (`Placa`),
  interfaces de repositorios, excepciones de negocio (cada una con su `codigo`) y el servicio
  `ValidadorReglasVehiculo` (PROPIETARIO: máximo 2 vehículos y nunca 2 carros; ARRENDATARIO:
  máximo 1). No depende de ninguna otra capa.
- **`application/`**: casos de uso (un caso de uso = una acción del sistema) y DTOs. Cada caso de
  uso de un recurso "de conjunto" (torres, residentes, vehículos, usuarios) recibe explícitamente
  el `unidad_negocio_id` del llamador y valida que todo lo que toca pertenezca a esa misma unidad.
- **`infrastructure/`**: repositorios con SQLAlchemy, modelos ORM, sesión de base de datos,
  hashing de contraseñas (bcrypt, ejecutado en un hilo aparte con `hashear_password_async` /
  `verificar_password_async` para no bloquear el event loop), JWT, lectura de Excel y generación
  de la plantilla de carga masiva, y almacenamiento de logos subidos (codificados como data URI y
  guardados en la misma fila de la base de datos, para que sobrevivan a un despliegue con disco
  no persistente).
- **`presentation/`**: routers de FastAPI, esquemas Pydantic y dependencias de inyección
  (repositorios, casos de uso, autenticación, autorización por rol, extracción del
  `unidad_negocio_id` desde el token y límite de intentos de login).
- **`shared/`**: manejo centralizado de excepciones, logging y utilidades (normalización de slugs).

### Aislamiento multi-tenant (importante)

Todas las tablas de un conjunto (`torres`, `apartamentos`, `residentes`, `vehiculos`, `bloques`,
`parqueaderos`, usuarios del conjunto) tienen una
columna `unidad_negocio_id`, y las restricciones de unicidad (código de torre, documento,
**placa**) están definidas **por unidad de negocio**, no globalmente — dos conjuntos distintos
pueden tener perfectamente una placa `ABC123` cada uno, sin conflicto.

El `unidad_negocio_id` viaja embebido en el JWT del usuario autenticado (nunca se confía en un
valor enviado por el cliente ni en la URL del frontend). Cada endpoint de un recurso de conjunto
usa la dependencia `UnidadNegocioActual` para obtenerlo y filtrar/validar automáticamente.

## 4. Roles del sistema

| Rol | Alcance | Puede hacer |
|---|---|---|
| `ADMIN_PLATAFORMA` | Toda la plataforma (sin unidad de negocio propia) | Crear, editar, habilitar/deshabilitar unidades de negocio, su Super Administrador inicial, y listar/restablecer contraseña de sus usuarios |
| `SUPER_ADMIN` | Una unidad de negocio | Control total de residentes, vehículos, torres, apartamentos, bloques, parqueaderos, usuarios y carga masiva **de su propio conjunto** |
| `VIGILANTE` | Una unidad de negocio | Consultar placas y lectura (listados) de residentes, torres, apartamentos, bloques, parqueaderos y catálogos de su propio conjunto |

Guards de rol en `presentation/dependencies/autenticacion.py`: `requerir_admin_plataforma`,
`requerir_super_admin` y `requerir_cualquier_rol` (SUPER_ADMIN + VIGILANTE).

## 5. Estructura del proyecto

```
Backend/
├── app/
│   ├── domain/{entities,repositories,services,value_objects,exceptions}/
│   ├── application/{use_cases,dto}/
│   ├── infrastructure/{database,repositories,security,storage,excel}/
│   ├── presentation/{api/v1,schemas,dependencies}/
│   ├── shared/{exceptions,logging,utils}/
│   ├── config/
│   └── main.py
├── migrations/            # Alembic
├── tests/{unit,integration}/
├── Dockerfile
├── docker-entrypoint.sh
├── requirements.txt
└── .env.example
```

## 6. Variables de entorno

Copiar `.env.example` a `.env` y ajustar los valores (`DATABASE_URL`, `SECRET_KEY`, tiempos de
expiración de tokens, etc). **Nunca** subir un `.env` real con secretos al repositorio.

Con `ENVIRONMENT=production`, la app rechaza arrancar si `SECRET_KEY` o `ADMIN_PLATAFORMA_PASSWORD`
se dejan en su valor de ejemplo del repositorio (`app/config/settings.py`): hay que definir ambos
con valores propios antes del primer despliegue.

## 7. Ejecución con Docker

Desde la raíz del proyecto (`CONJUNTO/`), no desde `Backend/`:

```bash
cp .env.example .env   # y ajustar valores
docker compose up --build
```

Esto levanta PostgreSQL, aplica las migraciones, siembra los datos iniciales (roles + Administrador
de Plataforma) y expone la API en `http://localhost:8000` (o el puerto que definas en
`BACKEND_PORT`), con documentación interactiva en `/docs`.

## 8. Ejecución local (sin Docker)

```bash
cd Backend
python -m venv .venv
./.venv/Scripts/activate        # Windows
pip install -r requirements.txt
cp .env.example .env            # y apuntar DATABASE_URL a un Postgres local
alembic upgrade head
python -m app.infrastructure.database.seed
uvicorn app.main:app --reload
```

## 9. Migraciones (Alembic)

```bash
alembic upgrade head                          # aplicar migraciones
alembic revision --autogenerate -m "mensaje"  # generar una nueva migración
```

Los archivos de migración se nombran `YYYYMMDDNNNN_descripcion.py` en `migrations/versions/`.

## 10. Ejecución de pruebas

```bash
pytest -v                                              # todas
pytest tests/integration/test_vehiculos_api.py         # un archivo
pytest tests/unit/test_placa.py -k "<nombre>" -v       # una prueba
```

Las pruebas usan una base de datos SQLite en memoria (no requieren PostgreSQL) y cubren:

- **Unitarias**: value object `Placa`, reglas de negocio de vehículos por tipo de residente y
  validación de secretos en producción (`settings`).
- **Integración**: autenticación multi-tenant y permisos por rol, límite de intentos de login,
  unidades de negocio (slugs duplicados, unidades deshabilitadas), usuarios, vehículos
  (placas duplicadas, consulta de placa registrada y no registrada), bloques y parqueaderos, y
  carga masiva desde Excel.

## 11. Credenciales iniciales de desarrollo

El script de siembra (`app/infrastructure/database/seed.py`, ejecutado automáticamente por Docker)
crea únicamente los 3 roles y el usuario **Administrador de Plataforma**, con el correo y la
contraseña definidos en las variables de entorno `ADMIN_PLATAFORMA_CORREO` y
`ADMIN_PLATAFORMA_PASSWORD` de tu `.env` (ver `.env.example`). Si no se configuran, el código usa
un valor de ejemplo pensado únicamente para desarrollo local.

Con esta cuenta se crean las unidades de negocio (conjuntos) y su primer Super Administrador desde
`POST /api/v1/business-units`. **En cualquier despliegue real, define ambas variables de entorno con
tus propios valores antes del primer arranque** — nunca dejes el valor de ejemplo.

## 12. Endpoints principales

Todos bajo el prefijo `/api/v1`. Documentación completa e interactiva en `/docs` (Swagger) una vez
la API esté corriendo.

| Módulo | Acceso | Endpoints |
|---|---|---|
| Autenticación | Público | `POST /auth/login` (recibe `correo`, `password` y opcionalmente `slug_unidad_negocio`; máx. 5 intentos por IP+correo cada 60 s), `POST /auth/refresh`, `GET /auth/me` |
| Unidades de negocio | `ADMIN_PLATAFORMA` | `GET/POST /business-units`, `PUT /business-units/{id}`, `POST /business-units/{id}/logo`, `GET /business-units/{id}/users`, `POST /business-units/{id}/users/{usuario_id}/reset-password` |
| Unidad de negocio (público) | Público | `GET /business-units/public/{slug}` — nombre, logo y colores para la pantalla de ingreso |
| Usuarios | `SUPER_ADMIN` (de su propio conjunto) | `GET/POST /users`, `GET/PUT /users/{id}`, `PATCH /users/{id}/status` |
| Residentes | Lectura: `SUPER_ADMIN` y `VIGILANTE`; escritura: `SUPER_ADMIN` | `GET/POST /residents`, `GET/PUT/DELETE /residents/{id}` |
| Vehículos | `SUPER_ADMIN` | `GET/POST /vehicles`, `GET/PUT/DELETE /vehicles/{id}`, `PUT /vehicles/{id}/parking-spot` |
| **Consulta de placa** | `SUPER_ADMIN` y `VIGILANTE` | `GET /vehicles/plate/{placa}` |
| Torres | Lectura: ambos; escritura: `SUPER_ADMIN` | `GET/POST /towers`, `PUT/DELETE /towers/{id}` |
| Apartamentos | Lectura: ambos; escritura: `SUPER_ADMIN` | `GET/POST /apartments`, `PUT/DELETE /apartments/{id}` |
| Bloques de parqueaderos | Lectura: ambos; escritura: `SUPER_ADMIN` | `GET/POST /parking-blocks`, `PUT/DELETE /parking-blocks/{id}` |
| Parqueaderos | Lectura: ambos; escritura: `SUPER_ADMIN` | `GET/POST /parking-spots`, `PUT/DELETE /parking-spots/{id}` |
| Carga masiva | `SUPER_ADMIN` | `GET /import/template` (plantilla Excel), `POST /import/upload` (devuelve reporte por fila) |
| Catálogos | `SUPER_ADMIN` y `VIGILANTE` | `GET /vehicle-types`, `GET /resident-types` |

Todas las respuestas de error siguen el formato:

```json
{ "error": true, "mensaje": "...", "codigo": "REGLA_VEHICULO_INVALIDA" }
```

Códigos relevantes de multi-tenancy: `SLUG_DUPLICADO`, `UNIDAD_NEGOCIO_INACTIVA`,
`ACCESO_UNIDAD_NEGOCIO_INVALIDO` (el usuario existe pero no pertenece a la unidad indicada, o un
administrador de plataforma intentó loguearse con un `slug_unidad_negocio`). Exceso de intentos de
login: `DEMASIADOS_INTENTOS` (HTTP 429).

Al agregar un nuevo código de error, hay que registrarlo en `_CODIGO_A_STATUS`
(`shared/exceptions/manejador_excepciones.py`); si no, responde con 400 por defecto.

## 13. Agregar un endpoint

El recorrido habitual es: interfaz del repositorio en `domain/` → implementación en
`infrastructure/repositories/` → caso de uso en `application/use_cases/` → provider en
`presentation/dependencies/casos_uso.py` → esquema Pydantic → router en `presentation/api/v1/`
(registrado en `router.py`). Si el recurso es de un conjunto, el `unidad_negocio_id` se toma solo
de `UnidadNegocioActual` y el caso de uso valida que cada entidad referenciada le pertenezca.
