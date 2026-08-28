import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Building2, Check, Home, Loader2, Pencil, Plus, Trash2, X } from "lucide-react";
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
import { apartmentService, towerService } from "@/services/location-service";
import type { Apartamento, Torre } from "@/types";

export function LocationsPage() {
  const queryClient = useQueryClient();

  const torresQuery = useQuery({ queryKey: ["towers"], queryFn: () => towerService.listar({ limit: 500 }) });
  const apartamentosQuery = useQuery({
    queryKey: ["apartments", "todos"],
    queryFn: () => apartmentService.listar({ limit: 500 }),
  });

  const [paginaTorres, setPaginaTorres] = useState(1);
  const [tamanoPaginaTorres, setTamanoPaginaTorres] = useState(50);
  const [paginaApartamentos, setPaginaApartamentos] = useState(1);
  const [tamanoPaginaApartamentos, setTamanoPaginaApartamentos] = useState(50);

  const [nombreTorre, setNombreTorre] = useState("");
  const [codigoTorre, setCodigoTorre] = useState("");
  const [errorTorre, setErrorTorre] = useState<string | null>(null);
  const [torreEditando, setTorreEditando] = useState<Torre | null>(null);

  const [torreApartamento, setTorreApartamento] = useState("");
  const [numeroApartamento, setNumeroApartamento] = useState("");
  const [errorApartamento, setErrorApartamento] = useState<string | null>(null);
  const [apartamentoEditando, setApartamentoEditando] = useState<Apartamento | null>(null);

  const [torreAEliminar, setTorreAEliminar] = useState<Torre | null>(null);
  const [apartamentoAEliminar, setApartamentoAEliminar] = useState<Apartamento | null>(null);

  const limpiarFormTorre = () => {
    setTorreEditando(null);
    setNombreTorre("");
    setCodigoTorre("");
    setErrorTorre(null);
  };

  const limpiarFormApartamento = () => {
    setApartamentoEditando(null);
    setNumeroApartamento("");
    setErrorApartamento(null);
  };

  const editarTorre = (torre: Torre) => {
    setTorreEditando(torre);
    setNombreTorre(torre.nombre);
    setCodigoTorre(torre.codigo);
    setErrorTorre(null);
  };

  const editarApartamento = (apto: Apartamento) => {
    setApartamentoEditando(apto);
    setTorreApartamento(String(apto.torre_id));
    setNumeroApartamento(apto.numero);
    setErrorApartamento(null);
  };

  const crearTorre = useMutation({
    mutationFn: towerService.crear,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["towers"] });
      limpiarFormTorre();
    },
    onError: (error) => setErrorTorre(obtenerMensajeError(error)),
  });

  const actualizarTorre = useMutation({
    mutationFn: (vars: { id: number; nombre: string; codigo: string }) =>
      towerService.actualizar(vars.id, { nombre: vars.nombre, codigo: vars.codigo }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["towers"] });
      limpiarFormTorre();
    },
    onError: (error) => setErrorTorre(obtenerMensajeError(error)),
  });

  const eliminarTorre = useMutation({
    mutationFn: towerService.eliminar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["towers"] });
      setTorreAEliminar(null);
    },
  });

  const crearApartamento = useMutation({
    mutationFn: apartmentService.crear,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apartments"] });
      limpiarFormApartamento();
    },
    onError: (error) => setErrorApartamento(obtenerMensajeError(error)),
  });

  const actualizarApartamento = useMutation({
    mutationFn: (vars: { id: number; torre_id: number; numero: string; activo: boolean }) =>
      apartmentService.actualizar(vars.id, {
        torre_id: vars.torre_id,
        numero: vars.numero,
        activo: vars.activo,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apartments"] });
      limpiarFormApartamento();
    },
    onError: (error) => setErrorApartamento(obtenerMensajeError(error)),
  });

  const eliminarApartamento = useMutation({
    mutationFn: apartmentService.eliminar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apartments"] });
      setApartamentoAEliminar(null);
    },
  });

  const apartamentosFiltrados = apartamentosQuery.data?.filter(
    (a) => !torreApartamento || String(a.torre_id) === torreApartamento,
  );

  const torresVisibles = torresQuery.data?.slice(
    (paginaTorres - 1) * tamanoPaginaTorres,
    paginaTorres * tamanoPaginaTorres,
  );
  const apartamentosVisibles = apartamentosFiltrados?.slice(
    (paginaApartamentos - 1) * tamanoPaginaApartamentos,
    paginaApartamentos * tamanoPaginaApartamentos,
  );

  return (
    <div>
      <h1 className="text-2xl font-bold tracking-tight">Torres y apartamentos</h1>
      <p className="mt-1 text-muted-foreground">Estructura física del conjunto residencial</p>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-4 w-4" /> Torres
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form
              className="mb-2 flex gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                if (!nombreTorre.trim() || !codigoTorre.trim()) return;
                if (torreEditando) {
                  actualizarTorre.mutate({
                    id: torreEditando.id,
                    nombre: nombreTorre.trim(),
                    codigo: codigoTorre.trim(),
                  });
                } else {
                  crearTorre.mutate({ nombre: nombreTorre.trim(), codigo: codigoTorre.trim() });
                }
              }}
            >
              <Input placeholder="Nombre (ej. Torre 3)" value={nombreTorre} onChange={(e) => setNombreTorre(e.target.value)} />
              <Input placeholder="Código" className="w-28" value={codigoTorre} onChange={(e) => setCodigoTorre(e.target.value)} />
              <Button
                type="submit"
                size="icon"
                loading={crearTorre.isPending || actualizarTorre.isPending}
              >
                {torreEditando ? <Check className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              </Button>
              {torreEditando && (
                <Button type="button" variant="outline" size="icon" onClick={limpiarFormTorre}>
                  <X className="h-4 w-4" />
                </Button>
              )}
            </form>
            {torreEditando && (
              <p className="mb-2 text-xs text-muted-foreground">Editando "{torreEditando.nombre}"</p>
            )}
            {errorTorre && <p className="mb-3 text-xs text-destructive">{errorTorre}</p>}

            {torresQuery.isLoading ? (
              <Spinner />
            ) : torresQuery.data?.length === 0 ? (
              <EmptyState icon={Building2} title="Sin torres registradas" />
            ) : (
              <>
              <ul className="space-y-1.5">
                {torresVisibles?.map((torre) => (
                  <li
                    key={torre.id}
                    className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm"
                  >
                    <span className="font-medium">{torre.nombre}</span>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{torre.codigo}</Badge>
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => editarTorre(torre)}>
                        <Pencil className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-destructive hover:text-destructive"
                        disabled={eliminarTorre.isPending && eliminarTorre.variables === torre.id}
                        onClick={() => setTorreAEliminar(torre)}
                      >
                        {eliminarTorre.isPending && eliminarTorre.variables === torre.id ? (
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                          <Trash2 className="h-3.5 w-3.5" />
                        )}
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
              {torresQuery.data && torresQuery.data.length > 0 && (
                <Pagination
                  pagina={paginaTorres}
                  onCambiarPagina={setPaginaTorres}
                  tamanoPagina={tamanoPaginaTorres}
                  onCambiarTamanoPagina={setTamanoPaginaTorres}
                  cantidadEnPagina={torresVisibles?.length ?? 0}
                />
              )}
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Home className="h-4 w-4" /> Apartamentos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form
              className="mb-2 flex gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                if (!torreApartamento || !numeroApartamento.trim()) return;
                if (apartamentoEditando) {
                  actualizarApartamento.mutate({
                    id: apartamentoEditando.id,
                    torre_id: Number(torreApartamento),
                    numero: numeroApartamento.trim(),
                    activo: apartamentoEditando.activo,
                  });
                } else {
                  crearApartamento.mutate({
                    torre_id: Number(torreApartamento),
                    numero: numeroApartamento.trim(),
                  });
                }
              }}
            >
              <Select
                value={torreApartamento}
                onValueChange={(v) => {
                  setTorreApartamento(v);
                  setPaginaApartamentos(1);
                }}
                disabled={torresQuery.isLoading}
              >
                <SelectTrigger className="w-40">
                  <SelectValue placeholder={torresQuery.isLoading ? "Cargando..." : "Torre"} />
                </SelectTrigger>
                <SelectContent>
                  {torresQuery.data?.map((torre) => (
                    <SelectItem key={torre.id} value={String(torre.id)}>
                      {torre.nombre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input placeholder="Número" value={numeroApartamento} onChange={(e) => setNumeroApartamento(e.target.value)} />
              <Button
                type="submit"
                size="icon"
                loading={crearApartamento.isPending || actualizarApartamento.isPending}
              >
                {apartamentoEditando ? <Check className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              </Button>
              {apartamentoEditando && (
                <Button type="button" variant="outline" size="icon" onClick={limpiarFormApartamento}>
                  <X className="h-4 w-4" />
                </Button>
              )}
            </form>
            <p className="mb-2 text-xs text-muted-foreground">
              {apartamentoEditando
                ? `Editando apartamento ${apartamentoEditando.numero}`
                : torreApartamento
                  ? "Mostrando solo los apartamentos de la torre seleccionada"
                  : "Selecciona una torre para filtrar la lista"}
            </p>
            {errorApartamento && <p className="mb-3 text-xs text-destructive">{errorApartamento}</p>}

            {apartamentosQuery.isLoading ? (
              <Spinner />
            ) : apartamentosFiltrados?.length === 0 ? (
              <EmptyState icon={Home} title="Sin apartamentos registrados" />
            ) : (
              <>
              <ul className="max-h-80 space-y-1.5 overflow-y-auto">
                {apartamentosVisibles?.map((apto) => {
                  const torre = torresQuery.data?.find((t) => t.id === apto.torre_id);
                  return (
                    <li
                      key={apto.id}
                      className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm"
                    >
                      <span className="font-medium">
                        {torre?.nombre ?? "—"} · Apto {apto.numero}
                      </span>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => editarApartamento(apto)}
                        >
                          <Pencil className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-destructive hover:text-destructive"
                          disabled={eliminarApartamento.isPending && eliminarApartamento.variables === apto.id}
                          onClick={() => setApartamentoAEliminar(apto)}
                        >
                          {eliminarApartamento.isPending && eliminarApartamento.variables === apto.id ? (
                            <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Trash2 className="h-3.5 w-3.5" />
                          )}
                        </Button>
                      </div>
                    </li>
                  );
                })}
              </ul>
              {apartamentosFiltrados && apartamentosFiltrados.length > 0 && (
                <Pagination
                  pagina={paginaApartamentos}
                  onCambiarPagina={setPaginaApartamentos}
                  tamanoPagina={tamanoPaginaApartamentos}
                  onCambiarTamanoPagina={setTamanoPaginaApartamentos}
                  cantidadEnPagina={apartamentosVisibles?.length ?? 0}
                />
              )}
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <ConfirmDialog
        abierto={Boolean(torreAEliminar)}
        onCerrar={() => setTorreAEliminar(null)}
        onConfirmar={() => torreAEliminar && eliminarTorre.mutate(torreAEliminar.id)}
        titulo="Eliminar torre"
        descripcion={`¿Eliminar ${torreAEliminar?.nombre}? Esta acción no se puede deshacer.`}
        cargando={eliminarTorre.isPending}
      />

      <ConfirmDialog
        abierto={Boolean(apartamentoAEliminar)}
        onCerrar={() => setApartamentoAEliminar(null)}
        onConfirmar={() => apartamentoAEliminar && eliminarApartamento.mutate(apartamentoAEliminar.id)}
        titulo="Eliminar apartamento"
        descripcion={`¿Eliminar el apartamento ${apartamentoAEliminar?.numero}? Esta acción no se puede deshacer.`}
        cargando={eliminarApartamento.isPending}
      />
    </div>
  );
}
