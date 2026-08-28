import axios, { type AxiosError } from "axios";

import type { ErrorApi } from "@/types";

const CLAVE_ACCESS_TOKEN = "conjunto_access_token";
const CLAVE_REFRESH_TOKEN = "conjunto_refresh_token";

export const almacenTokens = {
  obtenerAccessToken: () => localStorage.getItem(CLAVE_ACCESS_TOKEN),
  obtenerRefreshToken: () => localStorage.getItem(CLAVE_REFRESH_TOKEN),
  guardarTokens: (accessToken: string, refreshToken: string) => {
    localStorage.setItem(CLAVE_ACCESS_TOKEN, accessToken);
    localStorage.setItem(CLAVE_REFRESH_TOKEN, refreshToken);
  },
  limpiarTokens: () => {
    localStorage.removeItem(CLAVE_ACCESS_TOKEN);
    localStorage.removeItem(CLAVE_REFRESH_TOKEN);
  },
};

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  const token = almacenTokens.obtenerAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refrescandoPromesa: Promise<string> | null = null;

async function refrescarAccessToken(): Promise<string> {
  const refreshToken = almacenTokens.obtenerRefreshToken();
  if (!refreshToken) throw new Error("No hay refresh token disponible");

  const respuesta = await axios.post(
    `${apiClient.defaults.baseURL}/auth/refresh`,
    { refresh_token: refreshToken },
  );
  const { access_token, refresh_token } = respuesta.data;
  almacenTokens.guardarTokens(access_token, refresh_token);
  return access_token;
}

/** Endpoints públicos de autenticación: un 401 aquí es "credenciales inválidas", no una sesión
 * expirada — nunca se debe intentar refrescar el token ni redirigir por esto. */
function esPeticionDeAutenticacionPublica(url: string | undefined): boolean {
  return Boolean(url && (url.includes("/auth/login") || url.includes("/auth/refresh")));
}

apiClient.interceptors.response.use(
  (respuesta) => respuesta,
  async (error: AxiosError) => {
    const peticionOriginal = error.config;
    const debeIntentarRefrescar =
      error.response?.status === 401 &&
      peticionOriginal &&
      !esPeticionDeAutenticacionPublica(peticionOriginal.url) &&
      !("_reintentado" in peticionOriginal);

    if (debeIntentarRefrescar) {
      try {
        refrescandoPromesa ??= refrescarAccessToken();
        const nuevoToken = await refrescandoPromesa;
        refrescandoPromesa = null;

        (peticionOriginal as typeof peticionOriginal & { _reintentado: boolean })._reintentado = true;
        peticionOriginal.headers = peticionOriginal.headers ?? {};
        peticionOriginal.headers.Authorization = `Bearer ${nuevoToken}`;
        return apiClient(peticionOriginal);
      } catch {
        refrescandoPromesa = null;
        almacenTokens.limpiarTokens();
        // Vuelve a la selección de unidad de negocio: no conocemos aquí el slug del
        // conjunto ni si es el login de plataforma, así que este es el destino neutral.
        window.location.href = "/";
      }
    }
    return Promise.reject(error);
  },
);

export function obtenerMensajeError(error: unknown, fallback = "Ocurrió un error inesperado"): string {
  if (axios.isAxiosError(error)) {
    const datos = error.response?.data as ErrorApi | undefined;
    if (datos?.mensaje) return datos.mensaje;
  }
  return fallback;
}
