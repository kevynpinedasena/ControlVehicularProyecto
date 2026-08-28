import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { Building2 } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Navigate, useNavigate } from "react-router-dom";
import { z } from "zod";

import { TenantLogo } from "@/components/shared/tenant-logo";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PasswordInput } from "@/components/ui/password-input";
import { useAuth } from "@/features/auth/auth-context";
import { useTenant } from "@/features/tenant/tenant-context";
import { obtenerMensajeError } from "@/services/api-client";

const esquemaLogin = z.object({
  correo: z.string().min(1, "El correo es obligatorio").email("Ingresa un correo válido"),
  password: z.string().min(1, "La contraseña es obligatoria"),
});

type FormularioLogin = z.infer<typeof esquemaLogin>;

export function LoginPage() {
  const { iniciarSesion, autenticado, usuario } = useAuth();
  const { unidad, slug } = useTenant();
  const navigate = useNavigate();
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormularioLogin>({ resolver: zodResolver(esquemaLogin) });

  if (autenticado && usuario) {
    const destino = usuario.rol === "SUPER_ADMIN" ? `/${slug}/admin/dashboard` : `/${slug}/consulta-placa`;
    return <Navigate to={destino} replace />;
  }

  const onSubmit = async (datos: FormularioLogin) => {
    setErrorGeneral(null);
    try {
      const usuario = await iniciarSesion({ ...datos, slug_unidad_negocio: slug });
      navigate(
        usuario.rol === "SUPER_ADMIN" ? `/${slug}/admin/dashboard` : `/${slug}/consulta-placa`,
        { replace: true },
      );
    } catch (error) {
      setErrorGeneral(obtenerMensajeError(error, "No se pudo iniciar sesión"));
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-secondary/50 px-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 shadow-lg"
      >
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
            <TenantLogo
              logoUrl={unidad.logo_url}
              nombre={unidad.nombre}
              icono={Building2}
              className="h-14 w-14 rounded-full"
              iconoClassName="h-7 w-7"
            />
          </div>
          <h1 className="max-w-full truncate text-xl font-semibold">{unidad.nombre}</h1>
          <p className="text-sm text-muted-foreground">Control Vehicular</p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          {errorGeneral && (
            <Alert variant="destructive">
              <AlertDescription>{errorGeneral}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="correo">Correo</Label>
            <Input
              id="correo"
              type="email"
              autoComplete="username"
              placeholder="usuario@conjunto.com"
              {...register("correo")}
            />
            {errors.correo && <p className="text-xs text-destructive">{errors.correo.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="password">Contraseña</Label>
            <PasswordInput
              id="password"
              autoComplete="current-password"
              placeholder="••••••••"
              {...register("password")}
            />
            {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
          </div>

          <Button type="submit" className="w-full" size="lg" loading={isSubmitting}>
            Iniciar sesión
          </Button>
        </form>

        <a href="/" className="mt-6 block text-center text-xs text-muted-foreground hover:text-foreground">
          No es tu conjunto? Cambiar
        </a>
      </motion.div>
    </div>
  );
}
