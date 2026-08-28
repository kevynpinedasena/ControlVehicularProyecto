import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, Loader2, Pencil, Phone, Plus, Search, Trash2, UserSquare2 } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { EmptyState } from "@/components/shared/empty-state";
import { Pagination } from "@/components/shared/pagination";
import { useAuth } from "@/features/auth/auth-context";
import { ResidentDetailDialog } from "@/features/residents/resident-detail-dialog";
import { ResidentFormDialog } from "@/features/residents/resident-form-dialog";
import { useDebounce } from "@/hooks/use-debounce";
import { apartmentService, towerService } from "@/services/location-service";
import { blockService, parkingSpotService } from "@/services/parking-service";
import { residentService } from "@/services/resident-service";
import type { Residente } from "@/types";

export function ResidentsPage() {
  const queryClient = useQueryClient();
  const { usuario } = useAuth();
  const puedeAdministrar = usuario?.rol === "SUPER_ADMIN";
  const [busqueda, setBusqueda] = useState("");
  const busquedaDebounced = useDebounce(busqueda);
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [residenteEditando, setResidenteEditando] = useState<Residente | null>(null);
  const [residenteDetalle, setResidenteDetalle] = useState<Residente | null>(null);
  const [residenteAEliminar, setResidenteAEliminar] = useState<Residente | null>(null);
  const [pagina, setPagina] = useState(1);
  const [tamanoPagina, setTamanoPagina] = useState(50);

  const residentesQuery = useQuery({
    queryKey: ["residents", busquedaDebounced, pagina, tamanoPagina],
    queryFn: () =>
      residentService.listar({
        busqueda: busquedaDebounced || undefined,
        skip: (pagina - 1) * tamanoPagina,
        limit: tamanoPagina,
      }),
  });
  const torresQuery = useQuery({
    queryKey: ["towers"],
    queryFn: () => towerService.listar({ limit: 500 }),
  });
  const apartamentosQuery = useQuery({
    queryKey: ["apartments", "todos"],
    queryFn: () => apartmentService.listar({ limit: 500 }),
  });
  const bloquesQuery = useQuery({ queryKey: ["parking-blocks"], queryFn: blockService.listar });
  const parqueaderosQuery = useQuery({
    queryKey: ["parking-spots"],
    queryFn: () => parkingSpotService.listar(),
  });

  const eliminarMutacion = useMutation({
    mutationFn: (id: number) => residentService.eliminar(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["residents"] });
      setResidenteAEliminar(null);
    },
  });

  const ubicacionDe = (apartamentoId: number) => {
    const apto = apartamentosQuery.data?.find((a) => a.id === apartamentoId);
    const torre = torresQuery.data?.find((t) => t.id === apto?.torre_id);
    return apto && torre ? `${torre.nombre} · Apto ${apto.numero}` : "—";
  };

  const parqueaderoDe = (parqueaderoId: number | null) => {
    if (!parqueaderoId) return "Sin asignar";
    const parqueadero = parqueaderosQuery.data?.find((p) => p.id === parqueaderoId);
    if (!parqueadero) return "Sin asignar";
    const bloque = bloquesQuery.data?.find((b) => b.id === parqueadero.bloque_id);
    return `${bloque?.nombre ?? "—"} · ${parqueadero.numero}`;
  };

  const telefonosDe = (residente: Residente) => {
    const telefonos = [residente.telefono_1, residente.telefono_2].filter(Boolean);
    return telefonos.length > 0 ? telefonos.join(" / ") : "—";
  };

  const abrirCrear = () => {
    setResidenteEditando(null);
    setDialogoAbierto(true);
  };

  const abrirEditar = (residente: Residente) => {
    setResidenteEditando(residente);
    setDialogoAbierto(true);
  };

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Residentes</h1>
          <p className="mt-1 text-muted-foreground">Propietarios y arrendatarios del conjunto</p>
        </div>
        {puedeAdministrar && (
          <Button onClick={abrirCrear} className="gap-2">
            <Plus className="h-4 w-4" />
            Nuevo residente
          </Button>
        )}
      </div>

      <div className="relative mt-6 max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Buscar por nombre o documento..."
          className="pl-9"
          value={busqueda}
          onChange={(e) => {
            setBusqueda(e.target.value);
            setPagina(1);
          }}
        />
      </div>

      <div className="mt-6 overflow-hidden rounded-xl border border-border bg-card">
        {residentesQuery.isLoading || torresQuery.isLoading || apartamentosQuery.isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner className="h-8 w-8" />
          </div>
        ) : residentesQuery.data?.length === 0 ? (
          <EmptyState
            icon={UserSquare2}
            title="No hay residentes"
            description="Registra el primer residente del conjunto"
          />
        ) : (
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-secondary/50 text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Nombre</th>
                <th className="px-4 py-3 font-medium">Documento</th>
                <th className="px-4 py-3 font-medium">Tipo</th>
                <th className="px-4 py-3 font-medium">Ubicación</th>
                <th className="px-4 py-3 font-medium">Teléfonos</th>
                <th className="px-4 py-3 font-medium">Vehículos</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {residentesQuery.data?.map((residente) => (
                <tr key={residente.id} className="transition-colors hover:bg-secondary/30">
                  <td className="px-4 py-3 font-medium">{residente.nombre}</td>
                  <td className="px-4 py-3 text-muted-foreground">{residente.documento}</td>
                  <td className="px-4 py-3">{residente.tipo_residente.nombre}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {ubicacionDe(residente.apartamento_id)}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    <span className="flex items-center gap-1.5">
                      <Phone className="h-3.5 w-3.5 shrink-0" />
                      {telefonosDe(residente)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant="secondary">{residente.vehiculos.length}</Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={residente.activo ? "success" : "outline"}>
                      {residente.activo ? "Activo" : "Inactivo"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setResidenteDetalle(residente)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {puedeAdministrar && (
                        <>
                          <Button variant="ghost" size="icon" onClick={() => abrirEditar(residente)}>
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-destructive hover:text-destructive"
                            disabled={eliminarMutacion.isPending && eliminarMutacion.variables === residente.id}
                            onClick={() => setResidenteAEliminar(residente)}
                          >
                            {eliminarMutacion.isPending && eliminarMutacion.variables === residente.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </Button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {residentesQuery.data && residentesQuery.data.length > 0 && (
          <Pagination
            pagina={pagina}
            onCambiarPagina={setPagina}
            tamanoPagina={tamanoPagina}
            onCambiarTamanoPagina={setTamanoPagina}
            cantidadEnPagina={residentesQuery.data.length}
          />
        )}
      </div>

      {puedeAdministrar && (
        <ResidentFormDialog
          abierto={dialogoAbierto}
          onCerrar={() => setDialogoAbierto(false)}
          residente={residenteEditando}
        />
      )}

      <ResidentDetailDialog
        abierto={Boolean(residenteDetalle)}
        onCerrar={() => setResidenteDetalle(null)}
        residente={residenteDetalle}
        ubicacion={residenteDetalle ? ubicacionDe(residenteDetalle.apartamento_id) : "—"}
        parqueaderoDe={parqueaderoDe}
      />

      <ConfirmDialog
        abierto={Boolean(residenteAEliminar)}
        onCerrar={() => setResidenteAEliminar(null)}
        onConfirmar={() => residenteAEliminar && eliminarMutacion.mutate(residenteAEliminar.id)}
        titulo="Eliminar residente"
        descripcion={`¿Eliminar a ${residenteAEliminar?.nombre}? Esta acción no se puede deshacer.`}
        cargando={eliminarMutacion.isPending}
      />
    </div>
  );
}
