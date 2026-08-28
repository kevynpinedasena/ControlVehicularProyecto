import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Building2, ExternalLink, Pencil, Plus, Users } from "lucide-react";
import { useState } from "react";

import { TenantLogo } from "@/components/shared/tenant-logo";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/shared/empty-state";
import { Pagination } from "@/components/shared/pagination";
import { Spinner } from "@/components/ui/spinner";
import { BusinessUnitCreateDialog } from "@/features/platform/business-unit-create-dialog";
import { BusinessUnitEditDialog } from "@/features/platform/business-unit-edit-dialog";
import { BusinessUnitUsersDialog } from "@/features/platform/business-unit-users-dialog";
import { businessUnitService } from "@/services/business-unit-service";
import type { UnidadNegocio } from "@/types";

export function BusinessUnitsPage() {
  const queryClient = useQueryClient();
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [unidadEditando, setUnidadEditando] = useState<UnidadNegocio | null>(null);
  const [unidadUsuarios, setUnidadUsuarios] = useState<UnidadNegocio | null>(null);
  const [pagina, setPagina] = useState(1);
  const [tamanoPagina, setTamanoPagina] = useState(50);

  const unidadesQuery = useQuery({ queryKey: ["business-units"], queryFn: businessUnitService.listar });
  const unidadesVisibles = unidadesQuery.data?.slice(
    (pagina - 1) * tamanoPagina,
    pagina * tamanoPagina,
  );

  const cambiarEstadoMutacion = useMutation({
    mutationFn: (vars: { id: number; unidad: Awaited<ReturnType<typeof businessUnitService.listar>>[number] }) =>
      businessUnitService.actualizar(vars.id, {
        nombre: vars.unidad.nombre,
        slug: vars.unidad.slug,
        color_primario: vars.unidad.color_primario,
        color_secundario: vars.unidad.color_secundario,
        activo: !vars.unidad.activo,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["business-units"] }),
  });

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Unidades de negocio</h1>
          <p className="mt-1 text-muted-foreground">Conjuntos residenciales registrados en la plataforma</p>
        </div>
        <Button onClick={() => setDialogoAbierto(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          Nueva unidad de negocio
        </Button>
      </div>

      <div className="mt-6 overflow-hidden rounded-xl border border-border bg-card">
        {unidadesQuery.isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner className="h-8 w-8" />
          </div>
        ) : unidadesQuery.data?.length === 0 ? (
          <EmptyState icon={Building2} title="Sin unidades de negocio" description="Crea la primera" />
        ) : (
          <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-secondary/50 text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Nombre</th>
                <th className="px-4 py-3 font-medium">Código</th>
                <th className="px-4 py-3 font-medium">Colores</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {unidadesVisibles?.map((unidad) => (
                <tr key={unidad.id} className="transition-colors hover:bg-secondary/30">
                  <td className="px-4 py-3 font-medium">
                    <div className="flex items-center gap-2">
                      <TenantLogo
                        logoUrl={unidad.logo_url}
                        nombre={unidad.nombre}
                        icono={Building2}
                        className="h-6 w-6 rounded-full"
                        iconoClassName="h-5 w-5 text-muted-foreground"
                      />
                      <span className="truncate">{unidad.nombre}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{unidad.slug}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1.5">
                      <span
                        className="h-5 w-5 rounded-full border border-border"
                        style={{ backgroundColor: unidad.color_primario }}
                      />
                      <span
                        className="h-5 w-5 rounded-full border border-border"
                        style={{ backgroundColor: unidad.color_secundario }}
                      />
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={unidad.activo ? "success" : "outline"}>
                      {unidad.activo ? "Activa" : "Deshabilitada"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-2">
                      <a
                        href={`/${unidad.slug}/login`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-accent"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                      <Button variant="ghost" size="icon" onClick={() => setUnidadUsuarios(unidad)}>
                        <Users className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => setUnidadEditando(unidad)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        loading={
                          cambiarEstadoMutacion.isPending &&
                          cambiarEstadoMutacion.variables?.id === unidad.id
                        }
                        onClick={() => cambiarEstadoMutacion.mutate({ id: unidad.id, unidad })}
                      >
                        {unidad.activo ? "Deshabilitar" : "Habilitar"}
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        )}
        {unidadesQuery.data && unidadesQuery.data.length > 0 && (
          <Pagination
            pagina={pagina}
            onCambiarPagina={setPagina}
            tamanoPagina={tamanoPagina}
            onCambiarTamanoPagina={setTamanoPagina}
            cantidadEnPagina={unidadesVisibles?.length ?? 0}
          />
        )}
      </div>

      <BusinessUnitCreateDialog abierto={dialogoAbierto} onCerrar={() => setDialogoAbierto(false)} />
      <BusinessUnitEditDialog
        abierto={Boolean(unidadEditando)}
        onCerrar={() => setUnidadEditando(null)}
        unidad={unidadEditando}
      />
      <BusinessUnitUsersDialog
        abierto={Boolean(unidadUsuarios)}
        onCerrar={() => setUnidadUsuarios(null)}
        unidad={unidadUsuarios}
      />
    </div>
  );
}
