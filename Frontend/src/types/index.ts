export type NombreRol = "ADMIN_PLATAFORMA" | "SUPER_ADMIN" | "VIGILANTE";

export interface TipoResidente {
  id: number;
  codigo: "PROPIETARIO" | "ARRENDATARIO";
  nombre: string;
}

export interface TipoVehiculo {
  id: number;
  codigo: "CARRO" | "MOTO";
  nombre: string;
}

export interface UsuarioActual {
  id: number;
  nombre: string;
  correo: string;
  rol: NombreRol;
  unidad_negocio_id: number | null;
}

export interface Usuario {
  id: number;
  nombre: string;
  correo: string;
  rol: NombreRol;
  unidad_negocio_id: number | null;
  activo: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface Torre {
  id: number;
  nombre: string;
  codigo: string;
}

export interface Apartamento {
  id: number;
  torre_id: number;
  numero: string;
  activo: boolean;
}

export interface Vehiculo {
  id: number;
  placa: string;
  tipo_vehiculo: TipoVehiculo;
  residente_id: number;
  parqueadero_id: number | null;
  activo: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface Bloque {
  id: number;
  nombre: string;
  codigo: string;
}

export interface Parqueadero {
  id: number;
  bloque_id: number;
  numero: string;
  tipo_espacio: "COMUNAL" | "PRIVADO";
  tipo_vehiculo: TipoVehiculo;
  capacidad: number;
  propietario_residente_id: number | null;
  vehiculos_asignados: number;
  activo: boolean;
}

export interface Residente {
  id: number;
  nombre: string;
  documento: string;
  tipo_residente: TipoResidente;
  apartamento_id: number;
  telefono_1: string | null;
  telefono_2: string | null;
  activo: boolean;
  created_at: string | null;
  updated_at: string | null;
  vehiculos: Vehiculo[];
}

export interface ConsultaPlacaResultado {
  registrado: boolean;
  placa: string;
  mensaje: string | null;
  tipo_vehiculo: TipoVehiculo | null;
  torre: string | null;
  apartamento: string | null;
  tipo_residente: TipoResidente | null;
  estado: string | null;
  telefono_1: string | null;
  telefono_2: string | null;
  parqueadero: string | null;
}

export interface UnidadNegocioPublica {
  nombre: string;
  slug: string;
  logo_url: string | null;
  color_primario: string;
  color_secundario: string;
  activo: boolean;
}

export interface UnidadNegocio extends UnidadNegocioPublica {
  id: number;
  created_at: string | null;
}

export interface ErrorApi {
  error: true;
  mensaje: string;
  codigo: string;
}

export interface ErrorImportacion {
  hoja: string;
  fila: number;
  mensaje: string;
}

export interface DetalleImportacion {
  hoja: string;
  fila: number;
  accion: "creado" | "actualizado";
  descripcion: string;
}

export interface ReporteImportacion {
  torres_creadas: number;
  apartamentos_creados: number;
  residentes_creados: number;
  vehiculos_creados: number;
  torres_actualizadas: number;
  apartamentos_actualizados: number;
  residentes_actualizados: number;
  vehiculos_actualizados: number;
  bloques_creados: number;
  bloques_actualizados: number;
  parqueaderos_creados: number;
  parqueaderos_actualizados: number;
  errores: ErrorImportacion[];
  detalles: DetalleImportacion[];
}
