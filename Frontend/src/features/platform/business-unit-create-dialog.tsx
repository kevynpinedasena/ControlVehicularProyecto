import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Upload } from "lucide-react";
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
import { PasswordInput } from "@/components/ui/password-input";
import { businessUnitService } from "@/services/business-unit-service";
import { obtenerMensajeError } from "@/services/api-client";

const esquema = z.object({
  nombre: z.string().min(2, "El nombre es obligatorio"),
  slug: z.string().min(2, "El código es obligatorio"),
  color_primario: z.string().min(4),
  color_secundario: z.string().min(4),
  admin_nombre: z.string().min(2, "El nombre es obligatorio"),
  admin_correo: z.string().email("Ingresa un correo válido"),
  admin_password: z.string().min(8, "Mínimo 8 caracteres"),
});

type Formulario = z.infer<typeof esquema>;

export function BusinessUnitCreateDialog({ abierto, onCerrar }: { abierto: boolean; onCerrar: () => void }) {
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
  } = useForm<Formulario>({
    resolver: zodResolver(esquema),
    defaultValues: { color_primario: "#2563eb", color_secundario: "#1e293b" },
  });

  useEffect(() => {
    if (abierto) {
      reset({ color_primario: "#2563eb", color_secundario: "#1e293b" });
      setLogo(null);
      setErrorGeneral(null);
    }
  }, [abierto, reset]);

  const mutacion = useMutation({
    mutationFn: (datos: Formulario) => businessUnitService.crear({ ...datos, logo }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["business-units"] });
      onCerrar();
    },
    onError: (error) => setErrorGeneral(obtenerMensajeError(error)),
  });

  return (
    <Dialog open={abierto} onOpenChange={(open) => !open && onCerrar()}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Nueva unidad de negocio</DialogTitle>
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
              <Input id="nombre" placeholder="Conjunto Los Pinos" {...register("nombre")} />
              {errors.nombre && <p className="text-xs text-destructive">{errors.nombre.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="slug">Código (URL)</Label>
              <Input id="slug" placeholder="los-pinos" {...register("slug")} />
              {errors.slug && <p className="text-xs text-destructive">{errors.slug.message}</p>}
            </div>
          </div>

          <div className="space-y-1.5">
            <Label>Logo (opcional)</Label>
            <label className="flex cursor-pointer items-center gap-2 rounded-md border border-dashed border-input px-3 py-2 text-sm text-muted-foreground hover:bg-accent">
              <Upload className="h-4 w-4" />
              {logo ? logo.name : "Seleccionar imagen"}
              <input
                type="file"
                accept="image/png,image/jpeg,image/svg+xml,image/webp"
                className="hidden"
                onChange={(e) => setLogo(e.target.files?.[0] ?? null)}
              />
            </label>
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

          <div className="border-t border-border pt-4">
            <p className="mb-3 text-sm font-medium">Super administrador de este conjunto</p>
            <div className="space-y-3">
              <div className="space-y-1.5">
                <Label htmlFor="admin_nombre">Nombre</Label>
                <Input id="admin_nombre" {...register("admin_nombre")} />
                {errors.admin_nombre && (
                  <p className="text-xs text-destructive">{errors.admin_nombre.message}</p>
                )}
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="admin_correo">Correo</Label>
                <Input id="admin_correo" type="email" {...register("admin_correo")} />
                {errors.admin_correo && (
                  <p className="text-xs text-destructive">{errors.admin_correo.message}</p>
                )}
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="admin_password">Contraseña temporal</Label>
                <PasswordInput id="admin_password" {...register("admin_password")} />
                {errors.admin_password && (
                  <p className="text-xs text-destructive">{errors.admin_password.message}</p>
                )}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onCerrar}>
              Cancelar
            </Button>
            <Button type="submit" loading={isSubmitting || mutacion.isPending}>
              Crear unidad de negocio
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
