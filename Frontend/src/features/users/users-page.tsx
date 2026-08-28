import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Users as UsersIcon } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { EmptyState } from "@/components/shared/empty-state";
import { Pagination } from "@/components/shared/pagination";
import { UserFormDialog } from "@/features/users/user-form-dialog";
import { userService } from "@/services/user-service";

const ETIQUETAS_ROL = {
  ADMIN_PLATAFORMA: "Administrador de plataforma",
  SUPER_ADMIN: "Super administrador",
  VIGILANTE: "Vigilante",
} as const;

export function UsersPage() {
  const queryClient = useQueryClient();
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [pagina, setPagina] = useState(1);
  const [tamanoPagina, setTamanoPagina] = useState(50);

  const usuariosQuery = useQuery({
    queryKey: ["users", pagina, tamanoPagina],
    queryFn: () => userService.listar({ skip: (pagina - 1) * tamanoPagina, limit: tamanoPagina }),
  });
  const cambiarEstadoMutacion = useMutation({
    mutationFn: ({ id, activo }: { id: number; activo: boolean }) => userService.cambiarEstado(id, activo),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Usuarios</h1>
          <p className="mt-1 text-muted-foreground">Cuentas de acceso al sistema</p>
        </div>
        <Button onClick={() => setDialogoAbierto(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          Nuevo usuario
        </Button>
      </div>

      <div className="mt-6 overflow-hidden rounded-xl border border-border bg-card">
        {usuariosQuery.isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner className="h-8 w-8" />
          </div>
        ) : usuariosQuery.data?.length === 0 ? (
          <EmptyState icon={UsersIcon} title="No hay usuarios" />
        ) : (
          <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-secondary/50 text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Nombre</th>
                <th className="px-4 py-3 font-medium">Correo</th>
                <th className="px-4 py-3 font-medium">Rol</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {usuariosQuery.data?.map((usuario) => (
                <tr key={usuario.id} className="transition-colors hover:bg-secondary/30">
                  <td className="px-4 py-3 font-medium">{usuario.nombre}</td>
                  <td className="px-4 py-3 text-muted-foreground">{usuario.correo}</td>
                  <td className="px-4 py-3">{ETIQUETAS_ROL[usuario.rol]}</td>
                  <td className="px-4 py-3">
                    <Badge variant={usuario.activo ? "success" : "outline"}>
                      {usuario.activo ? "Activo" : "Inactivo"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      loading={
                        cambiarEstadoMutacion.isPending &&
                        cambiarEstadoMutacion.variables?.id === usuario.id
                      }
                      onClick={() =>
                        cambiarEstadoMutacion.mutate({ id: usuario.id, activo: !usuario.activo })
                      }
                    >
                      {usuario.activo ? "Desactivar" : "Activar"}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        )}
        {usuariosQuery.data && usuariosQuery.data.length > 0 && (
          <Pagination
            pagina={pagina}
            onCambiarPagina={setPagina}
            tamanoPagina={tamanoPagina}
            onCambiarTamanoPagina={setTamanoPagina}
            cantidadEnPagina={usuariosQuery.data.length}
          />
        )}
      </div>

      <UserFormDialog abierto={dialogoAbierto} onCerrar={() => setDialogoAbierto(false)} />
    </div>
  );
}
