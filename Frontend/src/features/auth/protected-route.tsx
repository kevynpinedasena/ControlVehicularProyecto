import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "@/features/auth/auth-context";
import { Spinner } from "@/components/ui/spinner";
import type { NombreRol } from "@/types";

interface ProtectedRouteProps {
  rolesPermitidos: NombreRol[];
  redirigirLoginA: string;
  redirigirSinPermisoA: string;
}

export function ProtectedRoute({ rolesPermitidos, redirigirLoginA, redirigirSinPermisoA }: ProtectedRouteProps) {
  const { usuario, cargando, autenticado } = useAuth();

  if (cargando) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (!autenticado) {
    return <Navigate to={redirigirLoginA} replace />;
  }

  if (usuario && !rolesPermitidos.includes(usuario.rol)) {
    return <Navigate to={redirigirSinPermisoA} replace />;
  }

  return <Outlet />;
}
