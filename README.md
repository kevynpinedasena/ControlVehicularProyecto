# Plataforma Multi-Conjunto de Control Vehicular

Sistema que permite administrar **múltiples conjuntos residenciales** (unidades de negocio) desde
una sola plataforma. Cada conjunto tiene su propia marca (nombre, logo y colores), sus propios
residentes/vehículos/torres/apartamentos/parqueaderos, y su propio equipo (Super Administrador +
Vigilantes), completamente aislado de los demás conjuntos.

## Funcionalidades principales

- **Multi-conjunto**: cada unidad de negocio con su marca (logo y color primario) y datos aislados.
- **Residentes y vehículos**, con reglas de negocio por tipo de residente (Propietario: máximo 2
  vehículos y nunca 2 carros; Arrendatario: máximo 1).
- **Torres y apartamentos**, **bloques y parqueaderos** (con asignación de vehículo a parqueadero).
- **Consulta rápida de placa** para el puesto de vigilancia.
- **Carga masiva desde Excel** (plantilla descargable) de torres, apartamentos, residentes y
  vehículos.
- **Usuarios por conjunto** (Super Administrador y Vigilantes), con restablecimiento de contraseña
  desde la plataforma.
- **Seguridad**: JWT con refresh, contraseñas con bcrypt, límite de intentos de login y validación
  de secretos al arrancar en producción.

## Estructura del repositorio

```
CONJUNTO/
├── Backend/        # API FastAPI + PostgreSQL — ver Backend/README.md
├── Frontend/       # React + TypeScript + Vite — ver Frontend/README.md
├── graphify-out/   # Grafo de conocimiento del código (ver más abajo)
└── docker-compose.yml
```

## Roles

| Rol | Qué gestiona |
|---|---|
| **Administrador de Plataforma** | Crea y gestiona las unidades de negocio (conjuntos): nombre, logo, colores, su Super Administrador inicial, y puede restablecer contraseñas de sus usuarios |
| **Super Administrador** | Todo dentro de su propio conjunto: residentes, vehículos, torres, apartamentos, bloques, parqueaderos, usuarios y carga masiva |
| **Vigilante** | Consulta rápida de placas y consulta de residentes de su propio conjunto |

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
4. Desde ahí: registra torres, apartamentos, residentes, vehículos, bloques y parqueaderos (a mano
   o con la carga masiva desde Excel), o crea usuarios `VIGILANTE` para el puesto de seguridad.

## Grafo de conocimiento del código

La carpeta [graphify-out/](graphify-out/) contiene un grafo del código generado con
[graphify](https://github.com/safishamsi/graphify): clases, funciones, módulos y conceptos de la
documentación, con sus relaciones, agrupados en comunidades.

- [graphify-out/graph.html](graphify-out/graph.html) — grafo interactivo (abrir en el navegador).
- [graphify-out/GRAPH_REPORT.md](graphify-out/GRAPH_REPORT.md) — reporte: nodos más conectados,
  comunidades, conexiones inesperadas y preguntas sugeridas.
- [graphify-out/graph.json](graphify-out/graph.json) — datos del grafo.

Para regenerarlo tras cambios en el código: `/graphify . --update` desde Claude Code. La caché y
los archivos locales de graphify están excluidos en `.gitignore`.

## Documentación detallada

- [Backend/README.md](Backend/README.md) — arquitectura, variables de entorno, migraciones,
  endpoints, pruebas.
- [Frontend/README.md](Frontend/README.md) — estructura, sistema de diseño, theming dinámico por
  conjunto, ejecución y build.
- [graphify-out/GRAPH_REPORT.md](graphify-out/GRAPH_REPORT.md) — mapa del código generado
  automáticamente.
