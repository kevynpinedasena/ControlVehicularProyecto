import { ProtectedRoute } from "@/features/auth/protected-route";
import { useTenant } from "@/features/tenant/tenant-context";
import type { NombreRol } from "@/types";

export function TenantProtectedRoute({ rolesPermitidos }: { rolesPermitidos: NombreRol[] }) {
  const { slug } = useTenant();
  return (
    <ProtectedRoute
      rolesPermitidos={rolesPermitidos}
      redirigirLoginA={`/${slug}/login`}
      redirigirSinPermisoA={`/${slug}/consulta-placa`}
    />
  );
}
