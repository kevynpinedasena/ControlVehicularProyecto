import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Building2, Upload } from "lucide-react";
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
import { TenantLogo } from "@/components/shared/tenant-logo";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { obtenerMensajeError } from "@/services/api-client";
import { businessUnitService } from "@/services/business-unit-service";
import type { UnidadNegocio } from "@/types";

const esquema = z.object({
  nombre: z.string().min(2, "El nombre es obligatorio"),
  slug: z.string().min(2, "El código es obligatorio"),
  color_primario: z.string().min(4),
  color_secundario: z.string().min(4),
  activo: z.boolean(),
});

type Formulario = z.infer<typeof esquema>;

interface BusinessUnitEditDialogProps {
  abierto: boolean;
  onCerrar: () => void;
  unidad: UnidadNegocio | null;
}

export function BusinessUnitEditDialog({ abierto, onCerrar, unidad }: BusinessUnitEditDialogProps) {
  const queryClient = useQueryClient();
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);
  const [logo, setLogo] = useState<File | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<Formulario>({ resolver: zodResolver(esquema) });

  useEffect(() => {
    if (abierto && unidad) {
      reset({
        nombre: unidad.nombre,
        slug: unidad.slug,
        color_primario: unidad.color_primario,
        color_secundario: unidad.color_secundario,
        activo: unidad.activo,
      });
      setLogo(null);
      setErrorGeneral(null);
    }
  }, [abierto, unidad, reset]);

  const mutacion = useMutation({
    mutationFn: async (datos: Formulario) => {
      if (!unidad) return;
      if (logo) {
        await businessUnitService.subirLogo(unidad.id, logo);
      }
      return businessUnitService.actualizar(unidad.id, datos);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["business-units"] });
      onCerrar();
    },
    onError: (error) => setErrorGeneral(obtenerMensajeError(error)),
  });

  if (!unidad) return null;

  return (
    <Dialog open={abierto} onOpenChange={(open) => !open && onCerrar()}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Editar unidad de negocio</DialogTitle>
        </DialogHeader>

        <form className="space-y-4" onSubmit={handleSubmit((d) => mutacion.mutate(d))}>
          {errorGeneral && (
            <Alert variant="destructive">
              <AlertDescription>{errorGeneral}</AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="nombre">Nombre del conjunto</Label>
              <Input id="nombre" {...register("nombre")} />
              {errors.nombre && <p className="text-xs text-destructive">{errors.nombre.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="slug">Código (URL)</Label>
              <Input id="slug" {...register("slug")} />
              {errors.slug && <p className="text-xs text-destructive">{errors.slug.message}</p>}
            </div>
          </div>

          <div className="space-y-1.5">
            <Label>Logo</Label>
            <div className="flex items-center gap-3">
              {unidad.logo_url && !logo && (
                <TenantLogo
                  logoUrl={unidad.logo_url}
                  nombre={unidad.nombre}
                  icono={Building2}
                  className="h-10 w-10 rounded"
                  iconoClassName="h-8 w-8 text-muted-foreground"
                />
              )}
              <label className="flex flex-1 cursor-pointer items-center gap-2 rounded-md border border-dashed border-input px-3 py-2 text-sm text-muted-foreground hover:bg-accent">
                <Upload className="h-4 w-4" />
                {logo ? logo.name : "Reemplazar imagen"}
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/svg+xml,image/webp"
                  className="hidden"
                  onChange={(e) => setLogo(e.target.files?.[0] ?? null)}
                />
              </label>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="color_primario">Color primario (botones y acentos)</Label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  className="h-10 w-10 shrink-0 rounded border border-input"
                  value={watch("color_primario") || "#2563eb"}
                  onChange={(e) => setValue("color_primario", e.target.value, { shouldValidate: true })}
                />
                <Input
                  id="color_primario"
                  value={watch("color_primario") ?? ""}
                  onChange={(e) => setValue("color_primario", e.target.value, { shouldValidate: true })}
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="color_secundario">Color secundario (fondo del menú)</Label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  className="h-10 w-10 shrink-0 rounded border border-input"
                  value={watch("color_secundario") || "#1e293b"}
                  onChange={(e) => setValue("color_secundario", e.target.value, { shouldValidate: true })}
                />
                <Input
                  id="color_secundario"
                  value={watch("color_secundario") ?? ""}
                  onChange={(e) => setValue("color_secundario", e.target.value, { shouldValidate: true })}
                />
              </div>
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" className="h-4 w-4" {...register("activo")} />
            Unidad activa
          </label>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onCerrar}>
              Cancelar
            </Button>
            <Button type="submit" loading={isSubmitting || mutacion.isPending}>
              Guardar cambios
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
