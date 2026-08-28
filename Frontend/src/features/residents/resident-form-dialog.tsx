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
import { residentTypeService } from "@/services/catalog-service";
import { apartmentService, towerService } from "@/services/location-service";
import { residentService } from "@/services/resident-service";
import type { Residente } from "@/types";

const SUFIJOS_TIPO_RESIDENTE: Record<string, string> = {
  PROPIETARIO: " (máx. 2 vehículos)",
  ARRENDATARIO: " (máx. 1 vehículo)",
};

const esquemaResidente = z.object({
  nombre: z.string().min(2, "El nombre es obligatorio"),
  documento: z.string().min(1, "El documento es obligatorio"),
  tipo_residente_id: z.string().min(1, "Selecciona un tipo de residente"),
  torre_id: z.string().min(1, "Selecciona una torre"),
  apartamento_id: z.string().min(1, "Selecciona un apartamento"),
  telefono_1: z.string().optional(),
  telefono_2: z.string().optional(),
});

type FormularioResidente = z.infer<typeof esquemaResidente>;

interface ResidentFormDialogProps {
  abierto: boolean;
  onCerrar: () => void;
  residente?: Residente | null;
}

export function ResidentFormDialog({ abierto, onCerrar, residente }: ResidentFormDialogProps) {
  const queryClient = useQueryClient();
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);
  const esEdicion = Boolean(residente);

  const torresQuery = useQuery({
    queryKey: ["towers"],
    queryFn: () => towerService.listar({ limit: 500 }),
    enabled: abierto,
  });
  const apartamentosQuery = useQuery({
    queryKey: ["apartments", "todos"],
    queryFn: () => apartmentService.listar({ limit: 500 }),
    enabled: abierto,
  });
  const tiposResidenteQuery = useQuery({
    queryKey: ["resident-types"],
    queryFn: residentTypeService.listar,
    enabled: abierto,
  });

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormularioResidente>({
    resolver: zodResolver(esquemaResidente),
    defaultValues: { tipo_residente_id: "" },
  });

  const torreSeleccionada = watch("torre_id");
  const apartamentosDeLaTorre = apartamentosQuery.data?.filter(
    (a) => String(a.torre_id) === torreSeleccionada,
  );

  useEffect(() => {
    if (!abierto) return;
    if (residente && apartamentosQuery.data) {
      const apartamentoActual = apartamentosQuery.data.find((a) => a.id === residente.apartamento_id);
      reset({
        nombre: residente.nombre,
        documento: residente.documento,
        tipo_residente_id: String(residente.tipo_residente.id),
        torre_id: apartamentoActual ? String(apartamentoActual.torre_id) : "",
        apartamento_id: String(residente.apartamento_id),
        telefono_1: residente.telefono_1 ?? "",
        telefono_2: residente.telefono_2 ?? "",
      });
    } else if (!residente) {
      reset({
        nombre: "",
        documento: "",
        tipo_residente_id: "",
        torre_id: "",
        apartamento_id: "",
        telefono_1: "",
        telefono_2: "",
      });
    }
    setErrorGeneral(null);
  }, [abierto, residente, apartamentosQuery.data, reset]);

  const mutacion = useMutation({
    mutationFn: async (datos: FormularioResidente) => {
      const payload = {
        nombre: datos.nombre,
        documento: datos.documento,
        tipo_residente_id: Number(datos.tipo_residente_id),
        apartamento_id: Number(datos.apartamento_id),
        telefono_1: datos.telefono_1?.trim() || null,
        telefono_2: datos.telefono_2?.trim() || null,
      };
      if (residente) {
        return residentService.actualizar(residente.id, { ...payload, activo: residente.activo });
      }
      return residentService.crear(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["residents"] });
      onCerrar();
    },
    onError: (error) => setErrorGeneral(obtenerMensajeError(error)),
  });

  return (
    <Dialog open={abierto} onOpenChange={(open) => !open && onCerrar()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{esEdicion ? "Editar residente" : "Nuevo residente"}</DialogTitle>
        </DialogHeader>

        <form className="space-y-4" onSubmit={handleSubmit((d) => mutacion.mutate(d))}>
          {errorGeneral && (
            <Alert variant="destructive">
              <AlertDescription>{errorGeneral}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="nombre">Nombre completo</Label>
            <Input id="nombre" {...register("nombre")} />
            {errors.nombre && <p className="text-xs text-destructive">{errors.nombre.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="documento">Documento</Label>
            <Input id="documento" {...register("documento")} />
            {errors.documento && <p className="text-xs text-destructive">{errors.documento.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label>Tipo de residente</Label>
            <Select
              value={watch("tipo_residente_id")}
              onValueChange={(v) => setValue("tipo_residente_id", v)}
              disabled={tiposResidenteQuery.isLoading}
            >
              <SelectTrigger>
                <SelectValue
                  placeholder={tiposResidenteQuery.isLoading ? "Cargando..." : "Selecciona un tipo"}
                />
              </SelectTrigger>
              <SelectContent>
                {tiposResidenteQuery.data?.map((tipo) => (
                  <SelectItem key={tipo.id} value={String(tipo.id)}>
                    {tipo.nombre}
                    {SUFIJOS_TIPO_RESIDENTE[tipo.codigo] ?? ""}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.tipo_residente_id && (
              <p className="text-xs text-destructive">{errors.tipo_residente_id.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Torre</Label>
              <Select
                value={torreSeleccionada}
                onValueChange={(v) => {
                  setValue("torre_id", v);
                  setValue("apartamento_id", "");
                }}
                disabled={torresQuery.isLoading}
              >
                <SelectTrigger>
                  <SelectValue placeholder={torresQuery.isLoading ? "Cargando..." : "Selecciona"} />
                </SelectTrigger>
                <SelectContent>
                  {torresQuery.data?.map((torre) => (
                    <SelectItem key={torre.id} value={String(torre.id)}>
                      {torre.nombre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.torre_id && <p className="text-xs text-destructive">{errors.torre_id.message}</p>}
            </div>

            <div className="space-y-1.5">
              <Label>Apartamento</Label>
              <Select
                value={watch("apartamento_id")}
                onValueChange={(v) => setValue("apartamento_id", v)}
                disabled={!torreSeleccionada || apartamentosQuery.isLoading}
              >
                <SelectTrigger>
                  <SelectValue
                    placeholder={apartamentosQuery.isLoading ? "Cargando..." : "Selecciona"}
                  />
                </SelectTrigger>
                <SelectContent>
                  {apartamentosDeLaTorre?.map((apto) => (
                    <SelectItem key={apto.id} value={String(apto.id)}>
                      {apto.numero}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.apartamento_id && (
                <p className="text-xs text-destructive">{errors.apartamento_id.message}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="telefono_1">Teléfono 1</Label>
              <Input id="telefono_1" placeholder="Opcional" {...register("telefono_1")} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="telefono_2">Teléfono 2</Label>
              <Input id="telefono_2" placeholder="Opcional" {...register("telefono_2")} />
            </div>
          </div>

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
