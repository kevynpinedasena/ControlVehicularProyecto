import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Building2,
  Check,
  Eye,
  Loader2,
  ParkingSquare,
  Pencil,
  Plus,
  Trash2,
  X,
} from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { EmptyState } from "@/components/shared/empty-state";
import { Input } from "@/components/ui/input";
import { Pagination } from "@/components/shared/pagination";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { obtenerMensajeError } from "@/services/api-client";
import { blockService, parkingSpotService } from "@/services/parking-service";
import { residentService } from "@/services/resident-service";
import { ParkingSpotDetailDialog } from "@/features/parking/parking-spot-detail-dialog";
import { ParkingSpotFormDialog } from "@/features/parking/parking-spot-form-dialog";
import type { Bloque, Parqueadero } from "@/types";

export function ParkingPage() {
  const queryClient = useQueryClient();

  const bloquesQuery = useQuery({ queryKey: ["parking-blocks"], queryFn: blockService.listar });
  const parqueaderosQuery = useQuery({
    queryKey: ["parking-spots"],
    queryFn: () => parkingSpotService.listar(),
  });
  const residentesQuery = useQuery({
    queryKey: ["residents", "todos"],
    queryFn: () => residentService.listar({ limit: 200 }),
  });

  const [paginaBloques, setPaginaBloques] = useState(1);
  const [tamanoPaginaBloques, setTamanoPaginaBloques] = useState(50);
  const [pagina, setPagina] = useState(1);
  const [tamanoPagina, setTamanoPagina] = useState(50);
  const [filtroBloque, setFiltroBloque] = useState("todos");

  const [nombreBloque, setNombreBloque] = useState("");
  const [codigoBloque, setCodigoBloque] = useState("");
  const [errorBloque, setErrorBloque] = useState<string | null>(null);
  const [bloqueEditando, setBloqueEditando] = useState<Bloque | null>(null);

  const [dialogoFormAbierto, setDialogoFormAbierto] = useState(false);
  const [parqueaderoEditando, setParqueaderoEditando] = useState<Parqueadero | null>(null);
  const [parqueaderoDetalle, setParqueaderoDetalle] = useState<Parqueadero | null>(null);
  const [bloqueAEliminar, setBloqueAEliminar] = useState<Bloque | null>(null);
  const [parqueaderoAEliminar, setParqueaderoAEliminar] = useState<Parqueadero | null>(null);

  const limpiarFormBloque = () => {
    setBloqueEditando(null);
    setNombreBloque("");
    setCodigoBloque("");
    setErrorBloque(null);
  };

  const editarBloque = (bloque: Bloque) => {
    setBloqueEditando(bloque);
    setNombreBloque(bloque.nombre);
    setCodigoBloque(bloque.codigo);
    setErrorBloque(null);
  };

  const crearBloque = useMutation({
    mutationFn: blockService.crear,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["parking-blocks"] });
      limpiarFormBloque();
    },
    onError: (error) => setErrorBloque(obtenerMensajeError(error)),
  });

  const actualizarBloque = useMutation({
    mutationFn: (vars: { id: number; nombre: string; codigo: string }) =>
      blockService.actualizar(vars.id, { nombre: vars.nombre, codigo: vars.codigo }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["parking-blocks"] });
      limpiarFormBloque();
    },
    onError: (error) => setErrorBloque(obtenerMensajeError(error)),
  });

  const eliminarBloque = useMutation({
    mutationFn: blockService.eliminar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["parking-blocks"] });
      setBloqueAEliminar(null);
    },
  });

  const eliminarParqueadero = useMutation({
    mutationFn: parkingSpotService.eliminar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["parking-spots"] });
      setParqueaderoAEliminar(null);
    },
  });

  const bloquesVisibles = bloquesQuery.data?.slice(
    (paginaBloques - 1) * tamanoPaginaBloques,
    paginaBloques * tamanoPaginaBloques,
  );

  const bloqueDe = (id: number) => bloquesQuery.data?.find((b) => b.id === id);
  const residenteDe = (id: number) => residentesQuery.data?.find((r) => r.id === id)?.nombre ?? "—";

  const parqueaderosFiltrados = parqueaderosQuery.data?.filter(
    (p) => filtroBloque === "todos" || String(p.bloque_id) === filtroBloque,
  );
  const parqueaderosVisibles = parqueaderosFiltrados?.slice(
    (pagina - 1) * tamanoPagina,
    pagina * tamanoPagina,
  );

  const abrirCrear = () => {
    setParqueaderoEditando(null);
    setDialogoFormAbierto(true);
  };

  const abrirEditar = (parqueadero: Parqueadero) => {
    setParqueaderoEditando(parqueadero);
    setDialogoFormAbierto(true);
  };

  const cargando = bloquesQuery.isLoading || parqueaderosQuery.isLoading || residentesQuery.isLoading;

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Parqueaderos</h1>
          <p className="mt-1 text-muted-foreground">Bloques, espacios y vehículos asignados</p>
        </div>
        <Button onClick={abrirCrear} className="gap-2">
          <Plus className="h-4 w-4" />
          Nuevo parqueadero
        </Button>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <Card className="min-w-0 lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-4 w-4" /> Bloques
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form
              className="mb-2 space-y-2"
              onSubmit={(e) => {
                e.preventDefault();
                const faltantes = [!nombreBloque.trim() && "Nombre", !codigoBloque.trim() && "Código"].filter(Boolean);
                if (faltantes.length > 0) {
                  setErrorBloque(`Completa los campos obligatorios: ${faltantes.join(", ")}`);
                  return;
                }
                setErrorBloque(null);
                if (bloqueEditando) {
                  actualizarBloque.mutate({
                    id: bloqueEditando.id,
                    nombre: nombreBloque.trim(),
                    codigo: codigoBloque.trim(),
                  });
                } else {
                  crearBloque.mutate({ nombre: nombreBloque.trim(), codigo: codigoBloque.trim() });
                }
              }}
            >
              <Input
                placeholder="Nombre (ej. Subterráneo)"
                value={nombreBloque}
                onChange={(e) => setNombreBloque(e.target.value)}
              />
              <div className="flex gap-2">
                <Input
                  placeholder="Código"
                  value={codigoBloque}
                  onChange={(e) => setCodigoBloque(e.target.value)}
                />
                <Button
                  type="submit"
                  size="icon"
                  className="shrink-0"
                  loading={crearBloque.isPending || actualizarBloque.isPending}
                >
                  {bloqueEditando ? <Check className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                </Button>
                {bloqueEditando && (
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="shrink-0"
                    onClick={limpiarFormBloque}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </form>
            {bloqueEditando && (
              <p className="mb-2 text-xs text-muted-foreground">Editando "{bloqueEditando.nombre}"</p>
            )}
            {errorBloque && <p className="mb-3 text-xs text-destructive">{errorBloque}</p>}

            {bloquesQuery.isLoading ? (
              <Spinner />
            ) : bloquesQuery.data?.length === 0 ? (
              <EmptyState icon={Building2} title="Sin bloques registrados" />
            ) : (
              <>
                <ul className="space-y-1.5">
                  {bloquesVisibles?.map((bloque) => (
                    <li
                      key={bloque.id}
                      className="flex items-center justify-between gap-2 rounded-lg border border-border px-3 py-2 text-sm"
                    >
                      <div className="flex min-w-0 items-center gap-2">
                        <span className="truncate font-medium" title={bloque.nombre}>
                          {bloque.nombre}
                        </span>
                        <Badge variant="outline" className="shrink-0">
                          {bloque.codigo}
                        </Badge>
                      </div>
                      <div className="flex shrink-0 items-center gap-1">
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => editarBloque(bloque)}>
                          <Pencil className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-destructive hover:text-destructive"
                          disabled={eliminarBloque.isPending && eliminarBloque.variables === bloque.id}
                          onClick={() => setBloqueAEliminar(bloque)}
                        >
                          {eliminarBloque.isPending && eliminarBloque.variables === bloque.id ? (
                            <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Trash2 className="h-3.5 w-3.5" />
                          )}
                        </Button>
                      </div>
                    </li>
                  ))}
                </ul>
                {bloquesQuery.data && bloquesQuery.data.length > 0 && (
                  <Pagination
                    pagina={paginaBloques}
                    onCambiarPagina={setPaginaBloques}
                    tamanoPagina={tamanoPaginaBloques}
                    onCambiarTamanoPagina={setTamanoPaginaBloques}
                    cantidadEnPagina={bloquesVisibles?.length ?? 0}
                  />
                )}
              </>
            )}
          </CardContent>
        </Card>

        <Card className="min-w-0 lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between gap-3 space-y-0">
            <CardTitle className="flex items-center gap-2">
              <ParkingSquare className="h-4 w-4" /> Espacios
            </CardTitle>
            <Select
              value={filtroBloque}
              onValueChange={(v) => {
                setFiltroBloque(v);
                setPagina(1);
              }}
            >
              <SelectTrigger className="w-44">
                <SelectValue placeholder="Todos los bloques" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos los bloques</SelectItem>
                {bloquesQuery.data?.map((bloque) => (
                  <SelectItem key={bloque.id} value={String(bloque.id)}>
                    {bloque.nombre}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardHeader>
          <CardContent className="p-0">
            {cargando ? (
              <div className="flex justify-center py-16">
                <Spinner className="h-8 w-8" />
              </div>
            ) : parqueaderosFiltrados?.length === 0 ? (
              <EmptyState
                icon={ParkingSquare}
                title="No hay parqueaderos"
                description={
                  bloquesQuery.data?.length ? "Crea el primer parqueadero" : "Primero crea un bloque"
                }
              />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b border-border bg-secondary/50 text-left text-xs uppercase text-muted-foreground">
                    <tr>
                      <th className="px-4 py-3 font-medium">Bloque</th>
                      <th className="px-4 py-3 font-medium">Número</th>
                      <th className="px-4 py-3 font-medium">Tipo</th>
                      <th className="px-4 py-3 font-medium">Vehículo</th>
                      <th className="px-4 py-3 font-medium">Ocupación</th>
                      <th className="px-4 py-3 font-medium">Dueño</th>
                      <th className="px-4 py-3 font-medium">Estado</th>
                      <th className="px-4 py-3 font-medium text-right">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {parqueaderosVisibles?.map((parqueadero) => (
                      <tr key={parqueadero.id} className="transition-colors hover:bg-secondary/30">
                        <td className="px-4 py-3">{bloqueDe(parqueadero.bloque_id)?.nombre ?? "—"}</td>
                        <td className="px-4 py-3 font-semibold">{parqueadero.numero}</td>
                        <td className="px-4 py-3">
                          <Badge variant={parqueadero.tipo_espacio === "PRIVADO" ? "secondary" : "outline"}>
                            {parqueadero.tipo_espacio === "PRIVADO" ? "Privado" : "Comunal"}
                          </Badge>
                        </td>
                        <td className="px-4 py-3">{parqueadero.tipo_vehiculo.nombre}</td>
                        <td className="px-4 py-3">
                          {parqueadero.vehiculos_asignados}/{parqueadero.capacidad}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {parqueadero.propietario_residente_id
                            ? residenteDe(parqueadero.propietario_residente_id)
                            : "—"}
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={parqueadero.activo ? "success" : "outline"}>
                            {parqueadero.activo ? "Activo" : "Inactivo"}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex justify-end gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setParqueaderoDetalle(parqueadero)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => abrirEditar(parqueadero)}>
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-destructive hover:text-destructive"
                              disabled={
                                eliminarParqueadero.isPending &&
                                eliminarParqueadero.variables === parqueadero.id
                              }
                              onClick={() => setParqueaderoAEliminar(parqueadero)}
                            >
                              {eliminarParqueadero.isPending &&
                              eliminarParqueadero.variables === parqueadero.id ? (
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
            {parqueaderosFiltrados && parqueaderosFiltrados.length > 0 && (
              <Pagination
                pagina={pagina}
                onCambiarPagina={setPagina}
                tamanoPagina={tamanoPagina}
                onCambiarTamanoPagina={setTamanoPagina}
                cantidadEnPagina={parqueaderosVisibles?.length ?? 0}
              />
            )}
          </CardContent>
        </Card>
      </div>

      <ParkingSpotFormDialog
        abierto={dialogoFormAbierto}
        onCerrar={() => setDialogoFormAbierto(false)}
        parqueadero={parqueaderoEditando}
        bloques={bloquesQuery.data ?? []}
      />

      <ParkingSpotDetailDialog
        abierto={Boolean(parqueaderoDetalle)}
        onCerrar={() => setParqueaderoDetalle(null)}
        parqueadero={
          parqueaderoDetalle
            ? (parqueaderosQuery.data?.find((p) => p.id === parqueaderoDetalle.id) ?? parqueaderoDetalle)
            : null
        }
        bloques={bloquesQuery.data ?? []}
        parqueaderos={parqueaderosQuery.data ?? []}
        residentes={residentesQuery.data ?? []}
      />

      <ConfirmDialog
        abierto={Boolean(bloqueAEliminar)}
        onCerrar={() => setBloqueAEliminar(null)}
        onConfirmar={() => bloqueAEliminar && eliminarBloque.mutate(bloqueAEliminar.id)}
        titulo="Eliminar bloque"
        descripcion={`¿Eliminar el bloque ${bloqueAEliminar?.nombre}? Esta acción no se puede deshacer.`}
        cargando={eliminarBloque.isPending}
      />

      <ConfirmDialog
        abierto={Boolean(parqueaderoAEliminar)}
        onCerrar={() => setParqueaderoAEliminar(null)}
        onConfirmar={() => parqueaderoAEliminar && eliminarParqueadero.mutate(parqueaderoAEliminar.id)}
        titulo="Eliminar parqueadero"
        descripcion={`¿Eliminar el parqueadero ${parqueaderoAEliminar?.numero}? Esta acción no se puede deshacer.`}
        cargando={eliminarParqueadero.isPending}
      />
    </div>
  );
}