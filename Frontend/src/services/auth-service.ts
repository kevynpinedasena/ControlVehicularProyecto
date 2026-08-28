import { apiClient } from "@/services/api-client";
import type { UsuarioActual } from "@/types";

export interface CredencialesLogin {
  correo: string;
  password: string;
  slug_unidad_negocio?: string | null;
}

interface TokensRespuesta {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authService = {
  login: async (credenciales: CredencialesLogin) => {
    const { data } = await apiClient.post<TokensRespuesta>("/auth/login", credenciales);
    return data;
  },
  obtenerUsuarioActual: async () => {
    const { data } = await apiClient.get<UsuarioActual>("/auth/me");
    return data;
  },
};
