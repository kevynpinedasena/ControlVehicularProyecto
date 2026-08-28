import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Car, Loader2, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { EmptyState } from "@/components/shared/empty-state";
import { Pagination } from "@/components/shared/pagination";
import { VehicleFormDialog } from "@/features/vehicles/vehicle-form-dialog";
import { useDebounce } from "@/hooks/use-debounce";
import { residentService } from "@/services/resident-service";
import { vehicleService } from "@/services/vehicle-service";
import type { Vehiculo } from "@/types";

export function VehiclesPage() {
  const queryClient = useQueryClient();
  const [busqueda, setBusqueda] = useState("");
  const busquedaDebounced = useDebounce(busqueda);
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [vehiculoEditando, setVehiculoEditando] = useState<Vehiculo | null>(null);
  const [pagina, setPagina] = useState(1);
  const [tamanoPagina, setTamanoPagina] = useState(50);
  const [vehiculoAEliminar, setVehiculoAEliminar] = useState<Vehiculo | null>(null);

  const vehiculosQuery = useQuery({
    queryKey: ["vehicles", busquedaDebounced, pagina, tamanoPagina],
    queryFn: () =>
      vehicleService.listar({
        busqueda: busquedaDebounced || undefined,
        skip: (pagina - 1) * tamanoPagina,
        limit: tamanoPagina,
      }),
  });
  const residentesQuery = useQuery({
    queryKey: ["residents", "todos"],
    queryFn: () => residentService.listar({ limit: 200 }),
  });

  const eliminarMutacion = useMutation({
    mutationFn: (id: number) => vehicleService.eliminar(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      setVehiculoAEliminar(null);
    },
  });

  const residenteDe = (id: number) => residentesQuery.data?.find((r) => r.id === id)?.nombre ?? "—";

  const abrirCrear = () => {
    setVehiculoEditando(null);
    setDialogoAbierto(true);
  };

  const abrirEditar = (vehiculo: Vehiculo) => {
    setVehiculoEditando(vehiculo);
    setDialogoAbierto(true);
  };

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Vehículos</h1>
          <p className="mt-1 text-muted-foreground">Carros y motos registrados en el conjunto</p>
        </div>
        <Button onClick={abrirCrear} className="gap-2">
          <Plus className="h-4 w-4" />
          Registrar vehículo
        </Button>
      </div>

      <div className="relative mt-6 max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Buscar por placa..."
          className="pl-9 uppercase"
          value={busqueda}
          onChange={(e) => {
            setBusqueda(e.target.value);
            setPagina(1);
          }}
        />
      </div>

      <div className="mt-6 overflow-hidden rounded-xl border border-border bg-card">
        {vehiculosQuery.isLoading || residentesQuery.isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner className="h-8 w-8" />
          </div>
        ) : vehiculosQuery.data?.length === 0 ? (
          <EmptyState icon={Car} title="No hay vehículos" description="Registra el primer vehículo" />
        ) : (
          <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-secondary/50 text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Placa</th>
                <th className="px-4 py-3 font-medium">Tipo</th>
                <th className="px-4 py-3 font-medium">Residente</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {vehiculosQuery.data?.map((vehiculo) => (
                <tr key={vehiculo.id} className="transition-colors hover:bg-secondary/30">
                  <td className="px-4 py-3 font-mono font-semibold tracking-wider">{vehiculo.placa}</td>
                  <td className="px-4 py-3">{vehiculo.tipo_vehiculo.nombre}</td>
                  <td className="px-4 py-3 text-muted-foreground">{residenteDe(vehiculo.residente_id)}</td>
                  <td className="px-4 py-3">
                    <Badge variant={vehiculo.activo ? "success" : "outline"}>
                      {vehiculo.activo ? "Activo" : "Inactivo"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-1">
                      <Button variant="ghost" size="icon" onClick={() => abrirEditar(vehiculo)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-destructive hover:text-destructive"
                        disabled={eliminarMutacion.isPending && eliminarMutacion.variables === vehiculo.id}
                        onClick={() => setVehiculoAEliminar(vehiculo)}
                      >
                        {eliminarMutacion.isPending && eliminarMutacion.variables === vehiculo.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        )}
        {vehiculosQuery.data && vehiculosQuery.data.length > 0 && (
          <Pagination
            pagina={pagina}
            onCambiarPagina={setPagina}
            tamanoPagina={tamanoPagina}
            onCambiarTamanoPagina={setTamanoPagina}
            cantidadEnPagina={vehiculosQuery.data.length}
          />
        )}
      </div>

      <VehicleFormDialog
        abierto={dialogoAbierto}
        onCerrar={() => setDialogoAbierto(false)}
        vehiculo={vehiculoEditando}
      />

      <ConfirmDialog
        abierto={Boolean(vehiculoAEliminar)}
        onCerrar={() => setVehiculoAEliminar(null)}
        onConfirmar={() => vehiculoAEliminar && eliminarMutacion.mutate(vehiculoAEliminar.id)}
        titulo="Eliminar vehículo"
        descripcion={`¿Eliminar el vehículo ${vehiculoAEliminar?.placa}? Esta acción no se puede deshacer.`}
        cargando={eliminarMutacion.isPending}
      />
    </div>
  );
}
