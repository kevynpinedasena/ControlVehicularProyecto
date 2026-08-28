import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { obtenerMensajeError } from "@/services/api-client";
import { vehicleTypeService } from "@/services/catalog-service";
import { residentService } from "@/services/resident-service";
import { vehicleService } from "@/services/vehicle-service";
import type { Vehiculo } from "@/types";

const esquemaVehiculo = z.object({
  placa: z
    .string()
    .min(5, "La placa debe tener al menos 5 caracteres")
    .max(10, "La placa es demasiado larga"),
  tipo_vehiculo_id: z.string().min(1, "Selecciona un tipo de vehículo"),
  residente_id: z.string().min(1, "Selecciona un residente"),
});

type FormularioVehiculo = z.infer<typeof esquemaVehiculo>;

interface VehicleFormDialogProps {
  abierto: boolean;
  onCerrar: () => void;
  vehiculo?: Vehiculo | null;
}

export function VehicleFormDialog({ abierto, onCerrar, vehiculo }: VehicleFormDialogProps) {
  const queryClient = useQueryClient();
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);
  const esEdicion = Boolean(vehiculo);

  const residentesQuery = useQuery({
    queryKey: ["residents", "todos"],
    queryFn: () => residentService.listar({ limit: 200 }),
    enabled: abierto,
  });

  const tiposVehiculoQuery = useQuery({
    queryKey: ["vehicle-types"],
    queryFn: vehicleTypeService.listar,
    enabled: abierto,
  });

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormularioVehiculo>({
    resolver: zodResolver(esquemaVehiculo),
    defaultValues: { tipo_vehiculo_id: "" },
  });

  useEffect(() => {
    if (!abierto) return;
    if (vehiculo) {
      reset({
        placa: vehiculo.placa,
        tipo_vehiculo_id: String(vehiculo.tipo_vehiculo.id),
        residente_id: String(vehiculo.residente_id),
      });
    } else {
      reset({ placa: "", tipo_vehiculo_id: "", residente_id: "" });
    }
    setErrorGeneral(null);
  }, [abierto, vehiculo, reset]);

  const mutacion = useMutation({
    mutationFn: async (datos: FormularioVehiculo) => {
      if (vehiculo) {
        return vehicleService.actualizar(vehiculo.id, {
          placa: datos.placa,
          tipo_vehiculo_id: Number(datos.tipo_vehiculo_id),
          activo: vehiculo.activo,
        });
      }
      return vehicleService.crear({
        placa: datos.placa,
        tipo_vehiculo_id: Number(datos.tipo_vehiculo_id),
        residente_id: Number(datos.residente_id),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      onCerrar();
    },
    onError: (error) => setErrorGeneral(obtenerMensajeError(error)),
  });

  return (
    <Dialog open={abierto} onOpenChange={(open) => !open && onCerrar()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{esEdicion ? "Editar vehículo" : "Registrar vehículo"}</DialogTitle>
        </DialogHeader>

        <form className="space-y-4" onSubmit={handleSubmit((d) => mutacion.mutate(d))}>
          {errorGeneral && (
            <Alert variant="destructive">
              <AlertDescription>{errorGeneral}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="placa">Placa</Label>
            <Input
              id="placa"
              className="uppercase"
              {...register("placa", {
                onChange: (e) => (e.target.value = e.target.value.toUpperCase()),
              })}
            />
            {errors.placa && <p className="text-xs text-destructive">{errors.placa.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label>Tipo de vehículo</Label>
            <Select
              value={watch("tipo_vehiculo_id")}
              onValueChange={(v) => setValue("tipo_vehiculo_id", v)}
              disabled={tiposVehiculoQuery.isLoading}
            >
              <SelectTrigger>
                <SelectValue
                  placeholder={tiposVehiculoQuery.isLoading ? "Cargando..." : "Selecciona un tipo"}
                />
              </SelectTrigger>
              <SelectContent>
                {tiposVehiculoQuery.data?.map((tipo) => (
                  <SelectItem key={tipo.id} value={String(tipo.id)}>
                    {tipo.nombre}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.tipo_vehiculo_id && (
              <p className="text-xs text-destructive">{errors.tipo_vehiculo_id.message}</p>
            )}
          </div>

          {!esEdicion && (
            <div className="space-y-1.5">
              <Label>Residente</Label>
              <Select
                value={watch("residente_id")}
                onValueChange={(v) => setValue("residente_id", v)}
                disabled={residentesQuery.isLoading}
              >
                <SelectTrigger>
                  <SelectValue
                    placeholder={residentesQuery.isLoading ? "Cargando..." : "Selecciona un residente"}
                  />
                </SelectTrigger>
                <SelectContent>
                  {residentesQuery.data?.map((residente) => (
                    <SelectItem key={residente.id} value={String(residente.id)}>
                      {residente.nombre} · {residente.documento}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.residente_id && (
                <p className="text-xs text-destructive">{errors.residente_id.message}</p>
              )}
            </div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onCerrar}>
              Cancelar
            </Button>
            <Button type="submit" loading={isSubmitting || mutacion.isPending}>
              Guardar
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
