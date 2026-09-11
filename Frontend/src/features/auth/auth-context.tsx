import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, type ReactNode, useContext, useState } from "react";

import { authService, type CredencialesLogin } from "@/services/auth-service";
import { almacenTokens } from "@/services/api-client";
import { conCargaGlobal } from "@/lib/carga-global";
import type { UsuarioActual } from "@/types";

interface AuthContextValue {
  usuario: UsuarioActual | undefined;
  cargando: boolean;
  autenticado: boolean;
  iniciarSesion: (credenciales: CredencialesLogin) => Promise<UsuarioActual>;
  cerrarSesion: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [tieneToken, setTieneToken] = useState(() => Boolean(almacenTokens.obtenerAccessToken()));

  const { data: usuario, isLoading } = useQuery({
    queryKey: ["usuario-actual"],
    queryFn: authService.obtenerUsuarioActual,
    enabled: tieneToken,
    retry: false,
  });

  const iniciarSesion = async (credenciales: CredencialesLogin) =>
    conCargaGlobal(async () => {
      const tokens = await authService.login(credenciales);
      almacenTokens.guardarTokens(tokens.access_token, tokens.refresh_token);
      setTieneToken(true);
      const usuarioActual = await authService.obtenerUsuarioActual();
      queryClient.setQueryData(["usuario-actual"], usuarioActual);
      return usuarioActual;
    });

  const cerrarSesion = () => {
    almacenTokens.limpiarTokens();
    setTieneToken(false);
    queryClient.setQueryData(["usuario-actual"], undefined);
    queryClient.clear();
  };

  return (
    <AuthContext.Provider
      value={{
        usuario,
        cargando: tieneToken && isLoading,
        autenticado: Boolean(usuario),
        iniciarSesion,
        cerrarSesion,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const contexto = useContext(AuthContext);
  if (!contexto) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return contexto;
}
