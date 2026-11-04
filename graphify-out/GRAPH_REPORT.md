# Graph Report - CONJUNTO  (2026-11-04)

## Corpus Check
- Corpus is ~44,755 words - fits in a single context window. You may not need a graph.

## Summary
- 1572 nodes · 5201 edges · 104 communities (59 shown, 45 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 654 edges (avg confidence: 0.93)
- Token cost: 71,883 input · 0 output

## Community Hubs (Navigation)
- Routers residentes y vehículos
- Casos de uso de residentes
- Gestión de torres
- Gestión de apartamentos
- UI compartida: tarjetas y paginación
- UI marca tenant y alertas
- Importación Excel y plantilla
- Auth frontend y tipos
- Tests integración auth y permisos
- Proveedores DI de vehículos
- Arquitectura documentada
- DTOs de importación
- Gestión de usuarios
- API unidades de negocio
- Enrutado y contexto frontend
- Diálogos y formularios
- Modelos ORM y conftest
- Configuración y seed
- API parqueaderos
- API usuarios
- Repositorio unidades de negocio
- Endpoints de autenticación
- Catálogo tipos de residente
- Caso de uso de login
- Casos de uso unidades de negocio
- Dependencias npm
- Casos de uso de bloques
- API bloques
- Entidad Usuario y repo
- DevDependencies npm
- Casos de uso de parqueaderos
- Reglas de negocio vehículos
- tsconfig app
- Manejo de excepciones
- Consulta de placa (vigilante)
- Roles y usuario actual
- Entidad Bloque y repo
- Entidad Residente y repo
- Value object Placa
- Entidad Vehículo y repo
- Validación de secretos
- Tipos de vehículo
- Entidad Parqueadero y repo
- Metadatos package.json
- Toaster de avisos
- tsconfig node
- Tokens JWT
- Tipos de residente
- Almacenamiento de logos
- Docker Postgres
- Tests API vehículos
- Variables de entorno backend
- Rate limit de login
- Entorno Alembic
- Servicio Docker backend
- Docker compose raíz
- Build args frontend
- Servicio Docker frontend
- Config Vite
- Healthcheck Docker
- Scripts npm
- Tailwind
- Scoping de tenant
- Flujo consulta de placa
- Tipos Vite env
- tsconfig raíz
- Entrypoint Docker
- Radix dialog
- Radix slot
- Tipos Node
- Tipos React
- Vercel rewrites

## God Nodes (most connected - your core abstractions)
1. `ImportarDatosMasivosUseCase` - 57 edges
2. `Usuario` - 49 edges
3. `cn()` - 48 edges
4. `Vehiculo` - 44 edges
5. `IVehiculoRepository` - 44 edges
6. `Button` - 44 edges
7. `IResidenteRepository` - 42 edges
8. `IUsuarioRepository` - 41 edges
9. `EntidadNoEncontradaError` - 39 edges
10. `react` - 39 edges

## Surprising Connections (you probably didn't know these)
- `El slug de la URL no autoriza` --semantically_similar_to--> `Aislamiento multi-tenant por unidad_negocio_id`  [INFERRED] [semantically similar]
  Frontend/README.md → Backend/README.md
- `AdminLayout, VigilanteLayout, PlatformLayout` --conceptually_related_to--> `Roles del sistema (ADMIN_PLATAFORMA, SUPER_ADMIN, VIGILANTE)`  [INFERRED]
  Frontend/README.md → README.md
- `Flujo para agregar endpoint (interfaz → repo → caso de uso → provider → schema → router)` --implements--> `Clean Architecture (presentation → application → domain ← infrastructure)`  [INFERRED]
  CLAUDE.md → Backend/README.md
- `services/api-client.ts (axios, refresh single-flight)` --shares_data_with--> `JWT con unidad_negocio_id embebido`  [INFERRED]
  CLAUDE.md → Backend/README.md
- `TenantLogo (fallback a ícono genérico)` --shares_data_with--> `Almacenamiento de logos como data URI`  [INFERRED]
  Frontend/README.md → Backend/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Aislamiento de tenant extremo a extremo (JWT → UnidadNegocioActual → filtrado; slug solo para marca)** — backend_readme_jwt, backend_readme_unidadnegocioactual, backend_readme_aislamiento_multi_tenant, frontend_readme_slug_no_autoriza, claude_role_guards [INFERRED 0.85]
- **Branding por conjunto (endpoint público, logos data URI, theming, TenantLogo)** — backend_readme_endpoint_publico_unidad, backend_readme_almacenamiento_logos, frontend_readme_theming_dinamico, frontend_readme_tenantlogo [INFERRED 0.85]

## Communities (104 total, 45 thin omitted)

### Community 0 - "Routers residentes y vehículos"
Cohesion: 0.07
Nodes (30): ListarResidentesUseCase, ObtenerResidenteUseCase, ListarTiposVehiculoUseCase, consultar_placa(), _a_response(), actualizar_residente(), crear_residente(), eliminar_residente() (+22 more)

### Community 1 - "Casos de uso de residentes"
Cohesion: 0.08
Nodes (15): ActualizarResidenteDTO, CrearResidenteDTO, ActualizarResidenteUseCase, CrearResidenteUseCase, EliminarResidenteUseCase, _obtener_residente_del_tenant(), ListarTiposResidenteUseCase, ConsultarPlacaUseCase (+7 more)

### Community 2 - "Gestión de torres"
Cohesion: 0.08
Nodes (25): ActualizarTorreDTO, CrearTorreDTO, ActualizarTorreUseCase, CrearTorreUseCase, EliminarTorreUseCase, ListarTorresUseCase, Torre, CodigoTorreDuplicadoError (+17 more)

### Community 3 - "Gestión de apartamentos"
Cohesion: 0.09
Nodes (23): ActualizarApartamentoDTO, CrearApartamentoDTO, ActualizarApartamentoUseCase, CrearApartamentoUseCase, EliminarApartamentoUseCase, ListarApartamentosUseCase, _obtener_apartamento_del_tenant(), _obtener_torre_del_tenant() (+15 more)

### Community 4 - "UI compartida: tarjetas y paginación"
Cohesion: 0.16
Nodes (39): EmptyState(), EmptyStateProps, Pagination(), PaginationIcon(), PaginationProps, TAMANOS_PAGINA, Badge(), BadgeProps (+31 more)

### Community 5 - "UI marca tenant y alertas"
Cohesion: 0.16
Nodes (39): TenantLogo(), TenantLogoProps, Alert, AlertDescription, alertVariants, Button, Input, InputProps (+31 more)

### Community 6 - "Importación Excel y plantilla"
Cohesion: 0.07
Nodes (21): FilaImportacion, _agregar_hoja(), generar_plantilla_excel(), ArchivoImportacionInvalidoError, _celda_a_texto(), leer_datos_importacion(), descargar_plantilla(), subir_archivo_importacion() (+13 more)

### Community 7 - "Auth frontend y tipos"
Cohesion: 0.08
Nodes (34): AuthContext, AuthContextValue, ProtectedRouteProps, ResumenTarjeta(), almacenTokens, apiClient, authService, CredencialesLogin (+26 more)

### Community 8 - "Tests integración auth y permisos"
Cohesion: 0.10
Nodes (30): _login(), test_acceso_sin_token_es_rechazado(), test_admin_plataforma_no_puede_gestionar_residentes(), test_login_bloquea_tras_demasiados_intentos_fallidos(), test_login_con_credenciales_invalidas_es_rechazado(), test_login_con_slug_de_otra_unidad_es_rechazado(), test_super_admin_no_puede_gestionar_unidades_de_negocio(), test_super_admin_puede_acceder_a_gestion_de_residentes() (+22 more)

### Community 9 - "Proveedores DI de vehículos"
Cohesion: 0.10
Nodes (25): EliminarVehiculoUseCase, ListarVehiculosUseCase, ObtenerVehiculoUseCase, caso_uso_actualizar_residente(), caso_uso_actualizar_vehiculo(), caso_uso_asignar_parqueadero_vehiculo(), caso_uso_consultar_placa(), caso_uso_crear_residente() (+17 more)

### Community 10 - "Arquitectura documentada"
Cohesion: 0.05
Nodes (34): Migraciones Alembic, Backend FastAPI multi-tenant, GET /business-units/public/{slug}, Formato de error {error, mensaje, codigo}, JWT con unidad_negocio_id embebido, Pruebas con SQLite en memoria, Script de siembra (roles + Administrador de Plataforma), UnidadNegocioActual (dependencia) (+26 more)

### Community 11 - "DTOs de importación"
Cohesion: 0.14
Nodes (16): DatosImportacion, DetalleImportacionDTO, ErrorImportacionDTO, ReporteImportacionDTO, ActualizarVehiculoDTO, AsignarParqueaderoVehiculoDTO, CrearVehiculoDTO, ResultadoConsultaPlacaDTO (+8 more)

### Community 12 - "Gestión de usuarios"
Cohesion: 0.10
Nodes (13): ActualizarUsuarioDTO, CrearUsuarioDTO, RestablecerPasswordResultadoDTO, ActualizarUsuarioUseCase, CrearUsuarioUseCase, ListarUsuariosDeUnidadUseCase, _obtener_usuario_del_tenant(), RestablecerPasswordUsuarioUseCase (+5 more)

### Community 13 - "API unidades de negocio"
Cohesion: 0.12
Nodes (22): ObtenerUnidadNegocioPublicaUseCase, _a_response(), actualizar_unidad_negocio(), crear_unidad_negocio(), listar_unidades_negocio(), listar_usuarios_de_unidad(), obtener_unidad_negocio_publica(), restablecer_password_usuario() (+14 more)

### Community 14 - "Enrutado y contexto frontend"
Cohesion: 0.14
Nodes (24): router, AuthProvider(), useAuth(), ProtectedRoute(), TenantContext, TenantContextValue, useTenant(), TenantLayout() (+16 more)

### Community 15 - "Diálogos y formularios"
Cohesion: 0.15
Nodes (26): ConfirmDialog(), ConfirmDialogProps, DialogContent, DialogDescription, DialogFooter(), DialogHeader(), DialogOverlay, DialogTitle (+18 more)

### Community 16 - "Modelos ORM y conftest"
Cohesion: 0.14
Nodes (20): Base, ParqueaderoModel, RolModel, TipoResidenteModel, TipoVehiculoModel, TorreModel, UnidadNegocioModel, hashear_password() (+12 more)

### Community 17 - "Configuración y seed"
Cohesion: 0.09
Nodes (6): obtener_configuracion(), obtener_sesion(), verificar_password(), verificar_password_async(), _ciclo_de_vida(), verificar_salud()

### Community 18 - "API parqueaderos"
Cohesion: 0.14
Nodes (17): EliminarParqueaderoUseCase, ListarParqueaderosUseCase, _a_response(), actualizar_parqueadero(), crear_parqueadero(), eliminar_parqueadero(), listar_parqueaderos(), caso_uso_actualizar_parqueadero() (+9 more)

### Community 19 - "API usuarios"
Cohesion: 0.17
Nodes (18): CambiarEstadoUsuarioUseCase, ListarUsuariosUseCase, ObtenerUsuarioUseCase, _a_response(), actualizar_usuario(), cambiar_estado_usuario(), crear_usuario(), listar_usuarios() (+10 more)

### Community 20 - "Repositorio unidades de negocio"
Cohesion: 0.16
Nodes (6): ActualizarLogoUnidadNegocioUseCase, ListarUnidadesNegocioUseCase, UnidadNegocio, IUnidadNegocioRepository, _a_entidad(), UnidadNegocioRepository

### Community 21 - "Endpoints de autenticación"
Cohesion: 0.16
Nodes (12): ObtenerUsuarioActualUseCase, RefrescarTokenUseCase, iniciar_sesion(), obtener_usuario_actual(), refrescar_token(), caso_uso_autenticar(), caso_uso_refrescar_token(), caso_uso_usuario_actual() (+4 more)

### Community 22 - "Catálogo tipos de residente"
Cohesion: 0.15
Nodes (8): listar_tipos_residente(), upgrade(), upgrade(), downgrade(), upgrade(), upgrade(), downgrade(), upgrade()

### Community 23 - "Caso de uso de login"
Cohesion: 0.21
Nodes (12): CredencialesLoginDTO, TokensDTO, AutenticarUsuarioUseCase, AccesoUnidadNegocioInvalidoError, CredencialesInvalidasError, ErrorDominio, PropietarioInvalidoError, TipoVehiculoIncompatibleError (+4 more)

### Community 24 - "Casos de uso unidades de negocio"
Cohesion: 0.16
Nodes (6): ActualizarUnidadNegocioDTO, CrearUnidadNegocioDTO, ActualizarUnidadNegocioUseCase, CrearUnidadNegocioUseCase, SlugDuplicadoError, normalizar_slug()

### Community 25 - "Dependencias npm"
Cohesion: 0.09
Nodes (22): dependencies, class-variance-authority@^0.7.1, clsx@^2.1.1, @fontsource/barlow-semi-condensed@^5.3.0, @fontsource-variable/bricolage-grotesque@^5.3.0, framer-motion@^11.15.0, @hookform/resolvers@^3.10.0, lucide-react@^0.469.0 (+14 more)

### Community 26 - "Casos de uso de bloques"
Cohesion: 0.19
Nodes (7): ActualizarBloqueDTO, CrearBloqueDTO, ActualizarBloqueUseCase, CrearBloqueUseCase, _obtener_bloque_del_tenant(), CodigoBloqueDuplicadoError, IBloqueRepository

### Community 27 - "API bloques"
Cohesion: 0.21
Nodes (12): EliminarBloqueUseCase, ListarBloquesUseCase, _a_response(), actualizar_bloque(), crear_bloque(), eliminar_bloque(), listar_bloques(), caso_uso_actualizar_bloque() (+4 more)

### Community 28 - "Entidad Usuario y repo"
Cohesion: 0.20
Nodes (6): Usuario, UsuarioModel, sembrar_datos_iniciales(), _a_entidad(), obtener_o_crear_rol(), UsuarioRepository

### Community 29 - "DevDependencies npm"
Cohesion: 0.10
Nodes (21): devDependencies, autoprefixer@^10.4.20, eslint@^9.17.0, eslint-plugin-react-hooks@^5.1.0, eslint-plugin-react-refresh@^0.4.16, postcss@^8.4.49, tailwindcss@^3.4.17, @types/react-dom@^18.3.5 (+13 more)

### Community 30 - "Casos de uso de parqueaderos"
Cohesion: 0.24
Nodes (8): ActualizarParqueaderoDTO, CrearParqueaderoDTO, ParqueaderoConOcupacionDTO, ActualizarParqueaderoUseCase, CrearParqueaderoUseCase, _obtener_parqueadero_del_tenant(), _resolver_propietario(), ParqueaderoDuplicadoError

### Community 31 - "Reglas de negocio vehículos"
Cohesion: 0.26
Nodes (11): ReglaVehiculoInvalidaError, ValidadorReglasVehiculo, test_arrendatario_no_puede_registrar_mas_de_un_vehiculo(), test_arrendatario_puede_registrar_un_vehiculo(), test_cambio_de_propietario_a_arrendatario_revalida_vehiculos(), test_propietario_no_puede_registrar_dos_carros(), test_propietario_no_puede_registrar_mas_de_dos_vehiculos(), test_propietario_puede_registrar_carro_y_moto() (+3 more)

### Community 32 - "tsconfig app"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+11 more)

### Community 33 - "Manejo de excepciones"
Cohesion: 0.15
Nodes (7): registrar_manejadores_excepciones(), manejar_error_dominio(), manejar_error_inesperado(), manejar_error_validacion(), _respuesta_error(), configurar_logging(), obtener_logger()

### Community 34 - "Consulta de placa (vigilante)"
Cohesion: 0.16
Nodes (15): ENTRADA_VEREDICTO, Fila(), PlateSearchPage(), ResultadoConsulta(), telefonosDe(), esquemaVehiculo, FormularioVehiculo, VehicleFormDialogProps (+7 more)

### Community 35 - "Roles y usuario actual"
Cohesion: 0.20
Nodes (5): UsuarioActualDTO, NombreRol, Rol, requerir_roles(), verificar()

### Community 36 - "Entidad Bloque y repo"
Cohesion: 0.24
Nodes (4): Bloque, BloqueModel, _a_entidad(), BloqueRepository

### Community 37 - "Entidad Residente y repo"
Cohesion: 0.23
Nodes (5): Residente, ResidenteModel, _a_entidad(), ResidenteRepository, _vehiculo_a_entidad()

### Community 38 - "Value object Placa"
Cohesion: 0.22
Nodes (4): PlacaInvalidaError, Placa, test_placa_invalida_lanza_error(), test_placas_equivalentes_se_normalizan_igual()

### Community 39 - "Entidad Vehículo y repo"
Cohesion: 0.30
Nodes (4): Vehiculo, VehiculoModel, _a_entidad(), VehiculoRepository

### Community 40 - "Validación de secretos"
Cohesion: 0.24
Nodes (5): Settings, test_desarrollo_acepta_los_valores_de_ejemplo(), test_produccion_acepta_secretos_personalizados(), test_produccion_rechaza_password_admin_de_ejemplo(), test_produccion_rechaza_secret_key_de_ejemplo()

### Community 41 - "Tipos de vehículo"
Cohesion: 0.29
Nodes (3): TipoVehiculo, _a_entidad(), TipoVehiculoRepository

### Community 42 - "Entidad Parqueadero y repo"
Cohesion: 0.26
Nodes (3): Parqueadero, _a_entidad(), ParqueaderoRepository

### Community 43 - "Metadatos package.json"
Cohesion: 0.15
Nodes (12): axios@^1.7.9, @fontsource-variable/instrument-sans@^5.3.0, react-dom@^18.3.1, recharts@^3.10.1, name, private, type, version (+4 more)

### Community 44 - "Toaster de avisos"
Cohesion: 0.22
Nodes (12): agregar(), Aviso, avisos, cerrar(), DURACION_MS, emitir(), notificar, suscribir() (+4 more)

### Community 45 - "tsconfig node"
Cohesion: 0.15
Nodes (12): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+4 more)

### Community 46 - "Tokens JWT"
Cohesion: 0.21
Nodes (4): TokenInvalidoError, _crear_token(), decodificar_token(), obtener_usuario_autenticado()

### Community 47 - "Tipos de residente"
Cohesion: 0.33
Nodes (3): TipoResidente, _a_entidad(), TipoResidenteRepository

### Community 49 - "Docker Postgres"
Cohesion: 0.18
Nodes (11): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, container_name, environment, image, networks, ports (+3 more)

### Community 50 - "Tests API vehículos"
Cohesion: 0.53
Nodes (7): ApartamentoModel, _crear_residente(), test_consultar_placa_no_registrada(), test_consultar_placa_registrada_devuelve_ubicacion(), test_propietario_no_puede_registrar_dos_carros_via_api(), test_registrar_placa_duplicada_es_rechazado(), _token_admin()

### Community 51 - "Variables de entorno backend"
Cohesion: 0.20
Nodes (10): environment, ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_PLATAFORMA_CORREO, ADMIN_PLATAFORMA_PASSWORD, DATABASE_URL, ENVIRONMENT, FRONTEND_URL, JWT_ALGORITHM (+2 more)

### Community 54 - "Servicio Docker backend"
Cohesion: 0.25
Nodes (8): container_name, depends_on, networks, ports, restart, postgres, condition, backend

### Community 55 - "Docker compose raíz"
Cohesion: 0.29
Nodes (6): driver, networks, conjunto_network, services, volumes, postgres_data

### Community 56 - "Build args frontend"
Cohesion: 0.40
Nodes (6): VITE_API_URL, build, args, context, dockerfile, build

### Community 57 - "Servicio Docker frontend"
Cohesion: 0.33
Nodes (6): container_name, depends_on, networks, ports, restart, frontend

### Community 58 - "Config Vite"
Cohesion: 0.33
Nodes (4): vite@^6.0.5, @vitejs/plugin-react@^4.3.4, vite, @vitejs/plugin-react

### Community 59 - "Healthcheck Docker"
Cohesion: 0.40
Nodes (5): interval, retries, test, timeout, healthcheck

### Community 60 - "Scripts npm"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 63 - "Flujo consulta de placa"
Cohesion: 0.67
Nodes (3): Consulta de placa GET /vehicles/plate/{placa}, Placa (value object), features/plate-search (pantalla del vigilante)

## Knowledge Gaps
- **16 isolated node(s):** `Flujo de primer uso`, `ValidadorReglasVehiculo`, `Placa (value object)`, `GET /business-units/public/{slug}`, `Migraciones Alembic` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 408 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **45 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ImportarDatosMasivosUseCase` connect `DTOs de importación` to `Casos de uso de residentes`, `Gestión de torres`, `Gestión de apartamentos`, `Entidad Residente y repo`, `Value object Placa`, `Importación Excel y plantilla`, `Proveedores DI de vehículos`, `Entidad Parqueadero y repo`, `Caso de uso de login`, `Casos de uso de bloques`, `Casos de uso de parqueaderos`, `Reglas de negocio vehículos`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `ImportarDatosMasivosUseCase` (e.g. with `DatosImportacion` and `DetalleImportacionDTO`) actually correct?**
  _`ImportarDatosMasivosUseCase` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Flujo de primer uso`, `ValidadorReglasVehiculo`, `Placa (value object)` to the rest of the system?**
  _16 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Routers residentes y vehículos` be split into smaller, more focused modules?**
  _Cohesion score 0.06760316066725197 - nodes in this community are weakly interconnected._
- **Why does `IUsuarioRepository` connect `Gestión de usuarios` to `Lookup usuario por id`, `Proveedores DI de vehículos`, `API usuarios`, `Endpoints de autenticación`, `Caso de uso de login`, `Casos de uso unidades de negocio`, `Entidad Usuario y repo`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `Usuario` (e.g. with `CrearUnidadNegocioUseCase` and `ActualizarUsuarioUseCase`) actually correct?**
  _`Usuario` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Should `Casos de uso de residentes` be split into smaller, more focused modules?**
  _Cohesion score 0.07615018508725542 - nodes in this community are weakly interconnected._