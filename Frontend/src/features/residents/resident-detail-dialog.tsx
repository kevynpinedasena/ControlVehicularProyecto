import { Car, ParkingSquare, Phone } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { EmptyState } from "@/components/shared/empty-state";
import type { Residente } from "@/types";

export function ResidentDetailDialog({
  abierto,
  onCerrar,
  residente,
  ubicacion,
  parqueaderoDe,
}: {
  abierto: boolean;
  onCerrar: () => void;
  residente: Residente | null;
  ubicacion: string;
  parqueaderoDe: (parqueaderoId: number | null) => string;
}) {
  if (!residente) return null;

  const telefonos = [residente.telefono_1, residente.telefono_2].filter(Boolean);

  return (
    <Dialog open={abierto} onOpenChange={(open) => !open && onCerrar()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{residente.nombre}</DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-x-4 gap-y-3 rounded-lg border border-border bg-secondary/30 p-4 text-sm">
          <div>
            <p className="text-xs text-muted-foreground">Documento</p>
            <p className="font-medium">{residente.documento}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Tipo</p>
            <p className="font-medium">{residente.tipo_residente.nombre}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Ubicación</p>
            <p className="font-medium">{ubicacion}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Estado</p>
            <Badge variant={residente.activo ? "success" : "outline"}>
              {residente.activo ? "Activo" : "Inactivo"}
            </Badge>
          </div>
          <div className="col-span-2">
            <p className="text-xs text-muted-foreground">Teléfonos</p>
            <p className="flex items-center gap-1.5 font-medium">
              <Phone className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
              {telefonos.length > 0 ? telefonos.join(" / ") : "—"}
            </p>
          </div>
        </div>

        <div className="mt-2">
          <p className="mb-2 flex items-center gap-1.5 text-sm font-medium">
            <Car className="h-4 w-4" />
            Vehículos a cargo
            <Badge variant="secondary" className="ml-1">
              {residente.vehiculos.length}
            </Badge>
          </p>

          {residente.vehiculos.length === 0 ? (
            <EmptyState icon={Car} title="Sin vehículos registrados" />
          ) : (
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full text-sm">
                <thead className="border-b border-border bg-secondary/50 text-left text-xs uppercase text-muted-foreground">
                  <tr>
                    <th className="px-3 py-2 font-medium">Placa</th>
                    <th className="px-3 py-2 font-medium">Tipo</th>
                    <th className="px-3 py-2 font-medium">Parqueadero</th>
                    <th className="px-3 py-2 font-medium">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {residente.vehiculos.map((vehiculo) => (
                    <tr key={vehiculo.id}>
                      <td className="px-3 py-2 font-mono font-semibold tracking-wider">
                        {vehiculo.placa}
                      </td>
                      <td className="px-3 py-2">{vehiculo.tipo_vehiculo.nombre}</td>
                      <td className="px-3 py-2 text-muted-foreground">
                        <span className="flex items-center gap-1.5">
                          <ParkingSquare className="h-3.5 w-3.5 shrink-0" />
                          {parqueaderoDe(vehiculo.parqueadero_id)}
                        </span>
                      </td>
                      <td className="px-3 py-2">
                        <Badge variant={vehiculo.activo ? "success" : "outline"}>
                          {vehiculo.activo ? "Activo" : "Inactivo"}
                        </Badge>
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
  );
}
