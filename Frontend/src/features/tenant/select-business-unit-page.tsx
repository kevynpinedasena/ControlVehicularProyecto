import { motion } from "framer-motion";
import { Building2, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { obtenerMensajeError } from "@/services/api-client";
import { businessUnitService } from "@/services/business-unit-service";

export function SelectBusinessUnitPage() {
  const navigate = useNavigate();
  const [codigo, setCodigo] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const continuar = async () => {
    const slug = codigo.trim().toLowerCase();
    if (!slug) return;

    setCargando(true);
    setError(null);
    try {
      await businessUnitService.obtenerPublica(slug);
      navigate(`/${slug}/login`);
    } catch (err) {
      setError(obtenerMensajeError(err, "No encontramos un conjunto con ese código"));
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-secondary/50 px-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-sm rounded-xl border border-border bg-card p-6 shadow-[0_8px_24px_-12px_rgb(15_23_42/0.18)] sm:p-8"
      >
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <div className="rounded-full bg-primary/10 p-3">
            <Building2 className="h-7 w-7 text-primary" />
          </div>
          <h1 className="text-xl font-semibold">Control Vehicular</h1>
          <p className="text-sm text-muted-foreground">Ingresa el código de tu conjunto</p>
        </div>

        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            continuar();
          }}
        >
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="codigo">Código del conjunto</Label>
            <Input
              id="codigo"
              autoFocus
              autoComplete="off"
              autoCapitalize="none"
              spellCheck={false}
              placeholder="mi-conjunto"
              value={codigo}
              onChange={(e) => setCodigo(e.target.value)}
            />
          </div>

          <Button type="submit" className="w-full" size="lg" loading={cargando} disabled={!codigo.trim()}>
            Continuar
          </Button>
        </form>

        <Link
          to="/plataforma/login"
          className="mt-6 flex items-center justify-center gap-1.5 text-xs text-muted-foreground hover:text-foreground"
        >
          <ShieldCheck className="h-3.5 w-3.5" />
          Acceso de administrador de plataforma
        </Link>
      </motion.div>
    </div>
  );
}
