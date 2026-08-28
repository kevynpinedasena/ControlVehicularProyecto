import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Car, Loader2, LogOut, Power, Trash2, UserRound } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { EmptyState } from "@/components/shared/empty-state";
import { obtenerMensajeError } from "@/services/api-client";
import { vehicleService } from "@/services/vehicle-service";
import type { Bloque, Parqueadero, Residente, Vehiculo } from "@/types";

interface ParkingSpotDetailDialogProps {
  abierto: boolean;
  onCerrar: () => void;
  parqueadero: Parqueadero | null;
  bloques: Bloque[];
  parqueaderos: Parqueadero[];
  residentes: Residente[];
}

export function ParkingSpotDetailDialog({
  abierto,
  onCerrar,
  parqueadero,
  bloques,
  parqueaderos,
  residentes,
}: ParkingSpotDetailDialogProps) {
  const queryClient = useQueryClient();
  const [errorAsignar, setErrorAsignar] = useState<string | null>(null);
  const [vehiculoSeleccionado, setVehiculoSeleccionado] = useState("");
  const [vehiculoAEliminar, setVehiculoAEliminar] = useState<Vehiculo | null>(null);

  const vehiculosDelSpotQuery = useQuery({
    queryKey: ["vehicles", "by-parqueadero", parqueadero?.id],
    queryFn: () => vehicleService.listar({ parqueaderoId: parqueadero!.id, limit: 200 }),
    enabled: abierto && Boolean(parqueadero),
  });

  const todosVehiculosQuery = useQuery({
    queryKey: ["vehicles", "todos"],
    queryFn: () => vehicleService.listar({ limit: 200 }),
    enabled: abierto,
  });

  const invalidarTodo = () => {
    queryClient.invalidateQueries({ queryKey: ["vehicles"] });
    queryClient.invalidateQueries({ queryKey: ["parking-spots"] });
  };

  const asignarMutacion = useMutation({
    mutationFn: (vars: { vehiculoId: number; parqueaderoId: number | null }) =>
      vehicleService.asignarParqueadero(vars.vehiculoId, vars.parqueaderoId),
    onSuccess: () => {
      invalidarTodo();
      setVehiculoSeleccionado("");
      setErrorAsignar(null);
    },
    onError: (error) => setErrorAsignar(obtenerMensajeError(error)),
  });

  const inhabilitarMutacion = useMutation({
    mutationFn: (vehiculoId: number) => {
      const vehiculo = vehiculosDelSpotQuery.data?.find((v) => v.id === vehiculoId);
      if (!vehiculo) throw new Error("Vehículo no encontrado");
      return vehicleService.actualizar(vehiculoId, {
        placa: vehiculo.placa,
        tipo_vehiculo_id: vehiculo.tipo_vehiculo.id,
        activo: !vehiculo.activo,
      });
    },
    onSuccess: () => invalidarTodo(),
  });

  const eliminarMutacion = useMutation({
    mutationFn: (vehiculoId: number) => vehicleService.eliminar(vehiculoId),
    onSuccess: () => {
      invalidarTodo();
      setVehiculoAEliminar(null);
    },
  });

  if (!parqueadero) return null;

  const bloque = bloques.find((b) => b.id === parqueadero.bloque_id);
  const propietario = parqueadero.propietario_residente_id
    ? residentes.find((r) => r.id === parqueadero.propietario_residente_id)
    : null;

  const residenteDe = (id: number) => residentes.find((r) => r.id === id)?.nombre ?? "—";

  const candidatos = todosVehiculosQuery.data?.filter(
    (v) =>
      v.tipo_vehiculo.codigo === parqueadero.tipo_vehiculo.codigo && v.parqueadero_id !== parqueadero.id,
  );

  const otrosParqueaderosCompatibles = parqueaderos.filter(
    (p) => p.id !== parqueadero.id && p.tipo_vehiculo.codigo === parqueadero.tipo_vehiculo.codigo,
  );

  const lleno = parqueadero.vehiculos_asignados >= parqueadero.capacidad;

  return (
    <>
    <Dialog open={abierto} onOpenChange={(open) => !open && onCerrar()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {bloque?.nombre ?? "—"} · Parqueadero {parqueadero.numero}
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-x-4 gap-y-3 rounded-lg border border-border bg-secondary/30 p-4 text-sm sm:grid-cols-3">
          <div>
            <p className="text-xs text-muted-foreground">Tipo</p>
            <Badge variant={parqueadero.tipo_espacio === "PRIVADO" ? "secondary" : "outline"}>
              {parqueadero.tipo_espacio === "PRIVADO" ? "Privado" : "Comunal"}
            </Badge>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Vehículo</p>
            <p className="font-medium">{parqueadero.tipo_vehiculo.nombre}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Ocupación</p>
            <p className="font-medium">
              {parqueadero.vehiculos_asignados}/{parqueadero.capacidad}
            </p>
          </div>
          <div className="col-span-2 sm:col-span-2">
            <p className="text-xs text-muted-foreground">Propietario</p>
            <p className="flex items-center gap-1.5 font-medium">
              <UserRound className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
              {propietario?.nombre ?? "—"}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Estado</p>
            <Badge variant={parqueadero.activo ? "success" : "outline"}>
              {parqueadero.activo ? "Activo" : "Inactivo"}
            </Badge>
          </div>
        </div>

        <div className="mt-2">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <p className="flex items-center gap-1.5 text-sm font-medium">
              <Car className="h-4 w-4" />
              Vehículos asignados
              <Badge variant="secondary" className="ml-1">
                {vehiculosDelSpotQuery.data?.length ?? 0}
              </Badge>
            </p>
            <div className="flex items-center gap-2">
              <Select
                value={vehiculoSeleccionado}
                onValueChange={setVehiculoSeleccionado}
                disabled={lleno || todosVehiculosQuery.isLoading}
              >
                <SelectTrigger className="w-56">
                  <SelectValue placeholder={lleno ? "Sin cupo disponible" : "Elegir vehículo..."} />
                </SelectTrigger>
                <SelectContent>
                  {candidatos?.map((v) => (
                    <SelectItem key={v.id} value={String(v.id)}>
                      {v.placa} · {residenteDe(v.residente_id)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                size="sm"
                disabled={!vehiculoSeleccionado || lleno}
                loading={asignarMutacion.isPending}
                onClick={() =>
                  asignarMutacion.mutate({
                    vehiculoId: Number(vehiculoSeleccionado),
                    parqueaderoId: parqueadero.id,
                  })
                }
              >
                Asignar
              </Button>
            </div>
          </div>
          {errorAsignar && <p className="mb-2 text-xs text-destructive">{errorAsignar}</p>}

          {vehiculosDelSpotQuery.data?.length === 0 ? (
            <EmptyState icon={Car} title="Sin vehículos asignados" />
          ) : (
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full text-sm">
                <thead className="border-b border-border bg-secondary/50 text-left text-xs uppercase text-muted-foreground">
                  <tr>
                    <th className="px-3 py-2 font-medium">Placa</th>
                    <th className="px-3 py-2 font-medium">Residente</th>
                    <th className="px-3 py-2 font-medium">Estado</th>
                    <th className="px-3 py-2 font-medium text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {vehiculosDelSpotQuery.data?.map((vehiculo) => (
                    <tr key={vehiculo.id}>
                      <td className="px-3 py-2 font-mono font-semibold tracking-wider">{vehiculo.placa}</td>
                      <td className="px-3 py-2 text-muted-foreground">{residenteDe(vehiculo.residente_id)}</td>
                      <td className="px-3 py-2">
                        <Badge variant={vehiculo.activo ? "success" : "outline"}>
                          {vehiculo.activo ? "Activo" : "Inactivo"}
                        </Badge>
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex items-center justify-end gap-1">
                          {otrosParqueaderosCompatibles.length > 0 && (
                            <Select
                              value=""
                              onValueChange={(v) =>
                                asignarMutacion.mutate({ vehiculoId: vehiculo.id, parqueaderoId: Number(v) })
                              }
                            >
                              <SelectTrigger className="h-7 w-32 text-xs">
                                <SelectValue placeholder="Cambiar a..." />
                              </SelectTrigger>
                              <SelectContent>
                                {otrosParqueaderosCompatibles.map((p) => {
                                  const b = bloques.find((bl) => bl.id === p.bloque_id);
                                  return (
                                    <SelectItem key={p.id} value={String(p.id)}>
                                      {b?.nombre ?? "—"} · {p.numero}
                                    </SelectItem>
                                  );
                                })}
                              </SelectContent>
                            </Select>
                          )}
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7"
                            title="Sacar del parqueadero"
                            disabled={asignarMutacion.isPending}
                            onClick={() =>
                              asignarMutacion.mutate({ vehiculoId: vehiculo.id, parqueaderoId: null })
                            }
                          >
                            <LogOut className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7"
                            title={vehiculo.activo ? "Inhabilitar" : "Habilitar"}
                            disabled={inhabilitarMutacion.isPending && inhabilitarMutacion.variables === vehiculo.id}
                            onClick={() => inhabilitarMutacion.mutate(vehiculo.id)}
                          >
                            {inhabilitarMutacion.isPending && inhabilitarMutacion.variables === vehiculo.id ? (
                              <Loader2 className="h-3.5 w-3.5 animate-spin" />
                            ) : (
                              <Power className="h-3.5 w-3.5" />
                            )}
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7 text-destructive hover:text-destructive"
                            title="Eliminar vehículo"
                            disabled={eliminarMutacion.isPending && eliminarMutacion.variables === vehiculo.id}
                            onClick={() => setVehiculoAEliminar(vehiculo)}
                          >
                            {eliminarMutacion.isPending && eliminarMutacion.variables === vehiculo.id ? (
                              <Loader2 className="h-3.5 w-3.5 animate-spin" />
                            ) : (
                              <Trash2 className="h-3.5 w-3.5" />
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
        </div>
      </DialogContent>
    </Dialog>

    <ConfirmDialog
      abierto={Boolean(vehiculoAEliminar)}
      onCerrar={() => setVehiculoAEliminar(null)}
      onConfirmar={() => vehiculoAEliminar && eliminarMutacion.mutate(vehiculoAEliminar.id)}
      titulo="Eliminar vehículo"
      descripcion={`¿Eliminar el vehículo ${vehiculoAEliminar?.placa}? Esta acción no se puede deshacer.`}
      cargando={eliminarMutacion.isPending}
    />
    </>
  );
}