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
import { parkingSpotService } from "@/services/parking-service";
import { residentService } from "@/services/resident-service";
import type { Bloque, Parqueadero } from "@/types";

const esquemaParqueadero = z
  .object({
    bloque_id: z.string().min(1, "Selecciona un bloque"),
    numero: z.string().min(1, "Ingresa el número").max(10, "El número es demasiado largo"),
    tipo_espacio: z.enum(["COMUNAL", "PRIVADO"]),
    tipo_vehiculo_id: z.string().min(1, "Selecciona un tipo de vehículo"),
    capacidad: z.coerce.number().int().min(1, "Debe ser al menos 1").max(100, "Máximo 100"),
    propietario_residente_id: z.string().optional(),
  })
  .refine((datos) => datos.tipo_espacio !== "PRIVADO" || Boolean(datos.propietario_residente_id), {
    message: "Selecciona el residente propietario",
    path: ["propietario_residente_id"],
  });

type FormularioParqueadero = z.infer<typeof esquemaParqueadero>;

interface ParkingSpotFormDialogProps {
  abierto: boolean;
  onCerrar: () => void;
  parqueadero?: Parqueadero | null;
  bloques: Bloque[];
}

export function ParkingSpotFormDialog({
  abierto,
  onCerrar,
  parqueadero,
  bloques,
}: ParkingSpotFormDialogProps) {
  const queryClient = useQueryClient();
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);
  const esEdicion = Boolean(parqueadero);

  const tiposVehiculoQuery = useQuery({
    queryKey: ["vehicle-types"],
    queryFn: vehicleTypeService.listar,
    enabled: abierto,
  });

  const residentesQuery = useQuery({
    queryKey: ["residents", "todos"],
    queryFn: () => residentService.listar({ limit: 200 }),
    enabled: abierto,
  });

  const propietarios = residentesQuery.data?.filter((r) => r.tipo_residente.codigo === "PROPIETARIO");

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormularioParqueadero>({
    resolver: zodResolver(esquemaParqueadero),
    defaultValues: { bloque_id: "", tipo_espacio: "COMUNAL", tipo_vehiculo_id: "", capacidad: 1 },
  });

  const tipoEspacio = watch("tipo_espacio");

  useEffect(() => {
    if (!abierto) return;
    if (parqueadero) {
      reset({
        bloque_id: String(parqueadero.bloque_id),
        numero: parqueadero.numero,
        tipo_espacio: parqueadero.tipo_espacio,
        tipo_vehiculo_id: String(parqueadero.tipo_vehiculo.id),
        capacidad: parqueadero.capacidad,
        propietario_residente_id: parqueadero.propietario_residente_id
          ? String(parqueadero.propietario_residente_id)
          : "",
      });
    } else {
      reset({
        bloque_id: "",
        numero: "",
        tipo_espacio: "COMUNAL",
        tipo_vehiculo_id: "",
        capacidad: 1,
        propietario_residente_id: "",
      });
    }
    setErrorGeneral(null);
  }, [abierto, parqueadero, reset]);

  const mutacion = useMutation({
    mutationFn: async (datos: FormularioParqueadero) => {
      const payload = {
        bloque_id: Number(datos.bloque_id),
        numero: datos.numero.trim(),
        tipo_espacio: datos.tipo_espacio,
        tipo_vehiculo_id: Number(datos.tipo_vehiculo_id),
        capacidad: Number(datos.capacidad),
        propietario_residente_id:
          datos.tipo_espacio === "PRIVADO" ? Number(datos.propietario_residente_id) : null,
      };
      if (parqueadero) {
        return parkingSpotService.actualizar(parqueadero.id, { ...payload, activo: parqueadero.activo });
      }
      return parkingSpotService.crear(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["parking-spots"] });
      onCerrar();
    },
    onError: (error) => setErrorGeneral(obtenerMensajeError(error)),
  });

  return (
    <Dialog open={abierto} onOpenChange={(open) => !open && onCerrar()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{esEdicion ? "Editar parqueadero" : "Nuevo parqueadero"}</DialogTitle>
        </DialogHeader>

        {bloques.length === 0 ? (
          <div className="space-y-4">
            <Alert>
              <AlertDescription>
                Primero debes crear al menos un bloque (por ejemplo "Subterráneo" o "Arriba") en la
                sección Bloques, a la izquierda. Luego podrás registrar los parqueaderos dentro de él.
              </AlertDescription>
            </Alert>
            <DialogFooter>
              <Button type="button" onClick={onCerrar}>
                Entendido
              </Button>
            </DialogFooter>
          </div>
        ) : (
        <form className="space-y-4" onSubmit={handleSubmit((d) => mutacion.mutate(d))}>
          {errorGeneral && (
            <Alert variant="destructive">
              <AlertDescription>{errorGeneral}</AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Bloque</Label>
              <Select value={watch("bloque_id")} onValueChange={(v) => setValue("bloque_id", v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un bloque" />
                </SelectTrigger>
                <SelectContent>
                  {bloques.map((bloque) => (
                    <SelectItem key={bloque.id} value={String(bloque.id)}>
                      {bloque.nombre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.bloque_id && <p className="text-xs text-destructive">{errors.bloque_id.message}</p>}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="numero">Número</Label>
              <Input id="numero" {...register("numero")} />
              {errors.numero && <p className="text-xs text-destructive">{errors.numero.message}</p>}
            </div>
          </div>

          <div className="space-y-1.5">
            <Label>Tipo de espacio</Label>
            <Select
              value={watch("tipo_espacio")}
              onValueChange={(v) => setValue("tipo_espacio", v as "COMUNAL" | "PRIVADO")}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="COMUNAL">Comunal</SelectItem>
                <SelectItem value="PRIVADO">Privado</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-3">
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

            <div className="space-y-1.5">
              <Label htmlFor="capacidad">Capacidad</Label>
              <Input id="capacidad" type="number" min={1} max={100} {...register("capacidad")} />
              {errors.capacidad && <p className="text-xs text-destructive">{errors.capacidad.message}</p>}
            </div>
          </div>

          {tipoEspacio === "PRIVADO" && (
            <div className="space-y-1.5">
              <Label>Propietario</Label>
              <Select
                value={watch("propietario_residente_id")}
                onValueChange={(v) => setValue("propietario_residente_id", v)}
                disabled={residentesQuery.isLoading}
              >
                <SelectTrigger>
                  <SelectValue
                    placeholder={residentesQuery.isLoading ? "Cargando..." : "Selecciona un propietario"}
                  />
                </SelectTrigger>
                <SelectContent>
                  {propietarios?.map((residente) => (
                    <SelectItem key={residente.id} value={String(residente.id)}>
                      {residente.nombre} · {residente.documento}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.propietario_residente_id && (
                <p className="text-xs text-destructive">{errors.propietario_residente_id.message}</p>
              )}
              {propietarios?.length === 0 && (
                <p className="text-xs text-muted-foreground">
                  No hay residentes con tipo Propietario registrados.
                </p>
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
        )}
      </DialogContent>
    </Dialog>
  );
}