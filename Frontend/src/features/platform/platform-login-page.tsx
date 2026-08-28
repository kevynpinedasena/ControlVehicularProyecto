import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { ShieldCheck } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Navigate, useNavigate } from "react-router-dom";
import { z } from "zod";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PasswordInput } from "@/components/ui/password-input";
import { useAuth } from "@/features/auth/auth-context";
import { obtenerMensajeError } from "@/services/api-client";

const esquemaLogin = z.object({
  correo: z.string().min(1, "El correo es obligatorio").email("Ingresa un correo válido"),
  password: z.string().min(1, "La contraseña es obligatoria"),
});

type FormularioLogin = z.infer<typeof esquemaLogin>;

export function PlatformLoginPage() {
  const { iniciarSesion, autenticado } = useAuth();
  const navigate = useNavigate();
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormularioLogin>({ resolver: zodResolver(esquemaLogin) });

  if (autenticado) {
    return <Navigate to="/plataforma/business-units" replace />;
  }

  const onSubmit = async (datos: FormularioLogin) => {
    setErrorGeneral(null);
    try {
      await iniciarSesion({ ...datos, slug_unidad_negocio: null });
      navigate("/plataforma/business-units", { replace: true });
    } catch (error) {
      setErrorGeneral(obtenerMensajeError(error, "No se pudo iniciar sesión"));
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 shadow-lg"
      >
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <div className="rounded-full bg-primary/10 p-3">
            <ShieldCheck className="h-7 w-7 text-primary" />
          </div>
          <h1 className="text-xl font-semibold">Administración de Plataforma</h1>
          <p className="text-sm text-muted-foreground">Acceso exclusivo para administradores</p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          {errorGeneral && (
            <Alert variant="destructive">
              <AlertDescription>{errorGeneral}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="correo">Correo</Label>
            <Input id="correo" type="email" autoComplete="username" {...register("correo")} />
            {errors.correo && <p className="text-xs text-destructive">{errors.correo.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="password">Contraseña</Label>
            <PasswordInput id="password" autoComplete="current-password" {...register("password")} />
            {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
          </div>

          <Button type="submit" className="w-full" size="lg" loading={isSubmitting}>
            Iniciar sesión
          </Button>
        </form>

        <a href="/" className="mt-6 block text-center text-xs text-muted-foreground hover:text-foreground">
          Volver a la selección de conjunto
        </a>
      </motion.div>
    </div>
  );
}
