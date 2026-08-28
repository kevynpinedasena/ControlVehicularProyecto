import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { obtenerMensajeError } from "@/services/api-client";
import { userService } from "@/services/user-service";

const esquemaUsuario = z.object({
  nombre: z.string().min(2, "El nombre es obligatorio"),
  correo: z.string().email("Ingresa un correo válido"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
  rol: z.enum(["SUPER_ADMIN", "VIGILANTE"]),
});

type FormularioUsuario = z.infer<typeof esquemaUsuario>;

export function UserFormDialog({ abierto, onCerrar }: { abierto: boolean; onCerrar: () => void }) {
  const queryClient = useQueryClient();
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormularioUsuario>({
    resolver: zodResolver(esquemaUsuario),
    defaultValues: { rol: "VIGILANTE" },
  });

  useEffect(() => {
    if (abierto) {
      reset({ nombre: "", correo: "", password: "", rol: "VIGILANTE" });
      setErrorGeneral(null);
    }
  }, [abierto, reset]);

  const mutacion = useMutation({
    mutationFn: (datos: FormularioUsuario) => userService.crear(datos),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      onCerrar();
    },
    onError: (error) => setErrorGeneral(obtenerMensajeError(error)),
  });

  return (
    <Dialog open={abierto} onOpenChange={(open) => !open && onCerrar()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Nuevo usuario</DialogTitle>
        </DialogHeader>

        <form className="space-y-4" onSubmit={handleSubmit((d) => mutacion.mutate(d))}>
          {errorGeneral && (
            <Alert variant="destructive">
              <AlertDescription>{errorGeneral}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="nombre">Nombre</Label>
            <Input id="nombre" {...register("nombre")} />
            {errors.nombre && <p className="text-xs text-destructive">{errors.nombre.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="correo">Correo</Label>
            <Input id="correo" type="email" {...register("correo")} />
            {errors.correo && <p className="text-xs text-destructive">{errors.correo.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="password">Contraseña temporal</Label>
            <PasswordInput id="password" {...register("password")} />
            {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label>Rol</Label>
            <Select value={watch("rol")} onValueChange={(v) => setValue("rol", v as FormularioUsuario["rol"])}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="VIGILANTE">Vigilante</SelectItem>
                <SelectItem value="SUPER_ADMIN">Super administrador</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onCerrar}>
              Cancelar
            </Button>
            <Button type="submit" loading={isSubmitting || mutacion.isPending}>
              Crear usuario
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
