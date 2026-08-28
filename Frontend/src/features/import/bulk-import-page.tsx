import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Download, FileSpreadsheet, ListChecks, Upload } from "lucide-react";
import { useState } from "react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { obtenerMensajeError } from "@/services/api-client";
import { importService } from "@/services/import-service";
import type { ReporteImportacion } from "@/types";

export function BulkImportPage() {
  const queryClient = useQueryClient();
  const [archivo, setArchivo] = useState<File | null>(null);
  const [descargando, setDescargando] = useState(false);
  const [reporte, setReporte] = useState<ReporteImportacion | null>(null);
  const [error, setError] = useState<string | null>(null);

  const descargarPlantilla = async () => {
    setDescargando(true);
    try {
      const blob = await importService.descargarPlantilla();
      const url = URL.createObjectURL(blob);
      const enlace = document.createElement("a");
      enlace.href = url;
      enlace.download = "plantilla-carga-masiva.xlsx";
      document.body.appendChild(enlace);
      enlace.click();
      enlace.remove();
      URL.revokeObjectURL(url);
    } finally {
      setDescargando(false);
    }
  };

  const subirMutacion = useMutation({
    mutationFn: (a: File) => importService.subirArchivo(a),
    onSuccess: (datos) => {
      setReporte(datos);
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["towers"] });
      queryClient.invalidateQueries({ queryKey: ["apartments"] });
      queryClient.invalidateQueries({ queryKey: ["residents"] });
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      queryClient.invalidateQueries({ queryKey: ["parking-blocks"] });
      queryClient.invalidateQueries({ queryKey: ["parking-spots"] });
    },
    onError: (err) => {
      setError(obtenerMensajeError(err));
      setReporte(null);
    },
  });

  return (
    <div>
      <h1 className="text-2xl font-bold tracking-tight">Carga masiva</h1>
      <p className="mt-1 text-muted-foreground">
        Registra torres, apartamentos, residentes, vehículos, bloques y parqueaderos desde un
        archivo Excel. Si el código, documento o placa ya existe, se actualiza; si no existe, se
        crea.
      </p>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Download className="h-4 w-4" /> 1. Descarga la plantilla
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Incluye una hoja por cada tipo de dato (Torres, Apartamentos, Residentes, Bloques,
              Parqueaderos y Vehículos) con un ejemplo de referencia. La hoja de Vehículos tiene
              columnas opcionales <code className="rounded bg-secondary px-1">bloque_codigo</code>{" "}
              y <code className="rounded bg-secondary px-1">parqueadero_numero</code> para asignar
              el vehículo a un parqueadero directamente en la carga. Llena las filas siguientes con
              tus datos reales, sin borrar los encabezados.
            </p>
            <Button variant="outline" onClick={descargarPlantilla} loading={descargando} className="gap-2">
              <FileSpreadsheet className="h-4 w-4" />
              Descargar plantilla de ejemplo
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-4 w-4" /> 2. Sube tu archivo lleno
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <label className="flex cursor-pointer items-center gap-2 rounded-md border border-dashed border-input px-3 py-2 text-sm text-muted-foreground hover:bg-accent">
              <Upload className="h-4 w-4" />
              {archivo ? archivo.name : "Seleccionar archivo .xlsx"}
              <input
                type="file"
                accept=".xlsx"
                className="hidden"
                onChange={(e) => {
                  setArchivo(e.target.files?.[0] ?? null);
                  setReporte(null);
                  setError(null);
                }}
              />
            </label>
            <Button
              onClick={() => archivo && subirMutacion.mutate(archivo)}
              disabled={!archivo}
              loading={subirMutacion.isPending}
              className="w-full"
            >
              Procesar carga masiva
            </Button>
          </CardContent>
        </Card>
      </div>

      {error && (
        <Alert variant="destructive" className="mt-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {reporte && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-success" /> Resultado de la carga
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
              <ResumenTarjeta etiqueta="Torres creadas" valor={reporte.torres_creadas} />
              <ResumenTarjeta etiqueta="Apartamentos creados" valor={reporte.apartamentos_creados} />
              <ResumenTarjeta etiqueta="Residentes creados" valor={reporte.residentes_creados} />
              <ResumenTarjeta etiqueta="Bloques creados" valor={reporte.bloques_creados} />
              <ResumenTarjeta etiqueta="Parqueaderos creados" valor={reporte.parqueaderos_creados} />
              <ResumenTarjeta etiqueta="Vehículos creados" valor={reporte.vehiculos_creados} />
            </div>

            {(reporte.torres_actualizadas > 0 ||
              reporte.apartamentos_actualizados > 0 ||
              reporte.residentes_actualizados > 0 ||
              reporte.bloques_actualizados > 0 ||
              reporte.parqueaderos_actualizados > 0 ||
              reporte.vehiculos_actualizados > 0) && (
              <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
                <ResumenTarjeta etiqueta="Torres actualizadas" valor={reporte.torres_actualizadas} />
                <ResumenTarjeta
                  etiqueta="Apartamentos actualizados"
                  valor={reporte.apartamentos_actualizados}
                />
                <ResumenTarjeta
                  etiqueta="Residentes actualizados"
                  valor={reporte.residentes_actualizados}
                />
                <ResumenTarjeta etiqueta="Bloques actualizados" valor={reporte.bloques_actualizados} />
                <ResumenTarjeta
                  etiqueta="Parqueaderos actualizados"
                  valor={reporte.parqueaderos_actualizados}
                />
                <ResumenTarjeta etiqueta="Vehículos actualizados" valor={reporte.vehiculos_actualizados} />
              </div>
            )}

            {reporte.detalles.length > 0 && (
              <div className="mt-6">
                <p className="mb-2 flex items-center gap-2 text-sm font-medium">
                  <ListChecks className="h-4 w-4" />
                  Detalle de lo procesado ({reporte.detalles.length} fila(s))
                </p>
                <div className="max-h-72 overflow-y-auto rounded-lg border border-border">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 border-b border-border bg-secondary/50 text-left text-xs uppercase text-muted-foreground">
                      <tr>
                        <th className="px-3 py-2 font-medium">Hoja</th>
                        <th className="px-3 py-2 font-medium">Fila</th>
                        <th className="px-3 py-2 font-medium">Acción</th>
                        <th className="px-3 py-2 font-medium">Registro</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {reporte.detalles.map((d, i) => (
                        <tr key={i}>
                          <td className="px-3 py-2">
                            <Badge variant="outline">{d.hoja}</Badge>
                          </td>
                          <td className="px-3 py-2 text-muted-foreground">{d.fila}</td>
                          <td className="px-3 py-2">
                            <Badge variant={d.accion === "creado" ? "success" : "secondary"}>
                              {d.accion === "creado" ? "Creado" : "Actualizado"}
                            </Badge>
                          </td>
                          <td className="px-3 py-2">{d.descripcion}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {reporte.errores.length > 0 && (
              <div className="mt-6">
                <p className="mb-2 flex items-center gap-2 text-sm font-medium text-destructive">
                  <AlertTriangle className="h-4 w-4" />
                  {reporte.errores.length} fila(s) con error — el resto de la carga sí se aplicó
                </p>
                <div className="max-h-72 overflow-y-auto rounded-lg border border-border">
                  <table className="w-full text-sm">
                    <thead className="border-b border-border bg-secondary/50 text-left text-xs uppercase text-muted-foreground">
                      <tr>
                        <th className="px-3 py-2 font-medium">Hoja</th>
                        <th className="px-3 py-2 font-medium">Fila</th>
                        <th className="px-3 py-2 font-medium">Error</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {reporte.errores.map((e, i) => (
                        <tr key={i}>
                          <td className="px-3 py-2">
                            <Badge variant="outline">{e.hoja}</Badge>
                          </td>
                          <td className="px-3 py-2 text-muted-foreground">{e.fila}</td>
                          <td className="px-3 py-2 text-destructive">{e.mensaje}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function ResumenTarjeta({ etiqueta, valor }: { etiqueta: string; valor: number }) {
  return (
    <div className="rounded-lg border border-border p-3">
      <p className="text-xs text-muted-foreground">{etiqueta}</p>
      <p className="text-2xl font-bold">{valor}</p>
    </div>
  );
}
