import { useMutation, useQuery } from "@tanstack/react-query";
import { Check, Copy, Dices, KeyRound, Users as UsersIcon } from "lucide-react";
import { useState } from "react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { EmptyState } from "@/components/shared/empty-state";
import { PasswordInput } from "@/components/ui/password-input";
import { Spinner } from "@/components/ui/spinner";
import { obtenerMensajeError } from "@/services/api-client";
import {
  businessUnitService,
  type RestablecerPasswordResultado,
} from "@/services/business-unit-service";
import type { UnidadNegocio } from "@/types";

const LONGITUD_MINIMA_PASSWORD = 8;

const ETIQUETAS_ROL = { ADMIN_PLATAFORMA: "Admin plataforma", SUPER_ADMIN: "Super administrador", VIGILANTE: "Vigilante" } as const;

export function BusinessUnitUsersDialog({
  abierto,
  onCerrar,
  unidad,
}: {
  abierto: boolean;
  onCerrar: () => void;
  unidad: UnidadNegocio | null;
}) {
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<RestablecerPasswordResultado | null>(null);
  const [copiado, setCopiado] = useState(false);
  const [usuarioPersonalizando, setUsuarioPersonalizando] = useState<number | null>(null);
  const [passwordPersonalizada, setPasswordPersonalizada] = useState("");

  const usuariosQuery = useQuery({
    queryKey: ["business-unit-users", unidad?.id],
    queryFn: () => businessUnitService.listarUsuarios(unidad!.id),
    enabled: abierto && Boolean(unidad),
  });

  const restablecerMutacion = useMutation({
    mutationFn: ({ usuarioId, nuevaPassword }: { usuarioId: number; nuevaPassword?: string }) =>
      businessUnitService.restablecerPassword(unidad!.id, usuarioId, nuevaPassword),
    onSuccess: (datos) => {
      setResultado(datos);
      setError(null);
      setCopiado(false);
      setUsuarioPersonalizando(null);
      setPasswordPersonalizada("");
    },
    onError: (err) => setError(obtenerMensajeError(err)),
  });

  const cerrar = () => {
    setResultado(null);
    setError(null);
    setUsuarioPersonalizando(null);
    setPasswordPersonalizada("");
    onCerrar();
  };

  const abrirPersonalizacion = (usuarioId: number) => {
    setUsuarioPersonalizando(usuarioId);
    setPasswordPersonalizada("");
    setError(null);
  };

  const confirmarPersonalizada = (usuarioId: number) => {
    if (passwordPersonalizada.length < LONGITUD_MINIMA_PASSWORD) {
      setError(`La contraseña debe tener al menos ${LONGITUD_MINIMA_PASSWORD} caracteres`);
      return;
    }
    restablecerMutacion.mutate({ usuarioId, nuevaPassword: passwordPersonalizada });
  };

  const copiarPassword = async () => {
    if (!resultado) return;
    try {
      await navigator.clipboard.writeText(resultado.nueva_password);
      setCopiado(true);
    } catch {
      // el navegador puede bloquear el portapapeles; el usuario igual puede seleccionar el texto
    }
  };

  if (!unidad) return null;

  return (
    <Dialog open={abierto} onOpenChange={(open) => !open && cerrar()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Usuarios de {unidad.nombre}</DialogTitle>
        </DialogHeader>

        {resultado && (
          <Alert className="mb-4 border-success/40 bg-success/10">
            <AlertDescription>
              <p className="mb-2 font-medium text-foreground">
                Nueva contraseña para <span className="font-mono">{resultado.correo}</span>
              </p>
              <p className="mb-2 text-xs text-muted-foreground">
                Cópiala y compártela ahora — no se volverá a mostrar.
              </p>
              <div className="flex items-center gap-2">
                <code className="flex-1 rounded-md border border-border bg-card px-3 py-2 font-mono text-sm">
                  {resultado.nueva_password}
                </code>
                <Button type="button" variant="outline" size="icon" onClick={copiarPassword}>
                  {copiado ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {usuariosQuery.isLoading ? (
          <div className="flex justify-center py-10">
            <Spinner className="h-8 w-8" />
          </div>
        ) : usuariosQuery.data?.length === 0 ? (
          <EmptyState icon={UsersIcon} title="Sin usuarios registrados" />
        ) : (
          <ul className="max-h-80 space-y-1.5 overflow-y-auto">
            {usuariosQuery.data?.map((usuario) => {
              const enviandoAleatoria =
                restablecerMutacion.isPending &&
                restablecerMutacion.variables?.usuarioId === usuario.id &&
                !restablecerMutacion.variables?.nuevaPassword;
              const enviandoPersonalizada =
                restablecerMutacion.isPending &&
                restablecerMutacion.variables?.usuarioId === usuario.id &&
                Boolean(restablecerMutacion.variables?.nuevaPassword);

              return (
                <li key={usuario.id} className="rounded-lg border border-border px-3 py-2 text-sm">
                  <div className="flex items-center justify-between">
                    <div className="min-w-0">
                      <p className="truncate font-medium">{usuario.nombre}</p>
                      <p className="truncate text-xs text-muted-foreground">{usuario.correo}</p>
                    </div>
                    <div className="flex shrink-0 items-center gap-2">
                      <Badge variant="outline">{ETIQUETAS_ROL[usuario.rol]}</Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        className="gap-1.5"
                        loading={enviandoAleatoria}
                        onClick={() => restablecerMutacion.mutate({ usuarioId: usuario.id })}
                      >
                        <Dices className="h-3.5 w-3.5" />
                        Aleatoria
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="gap-1.5"
                        onClick={() =>
                          usuarioPersonalizando === usuario.id
                            ? setUsuarioPersonalizando(null)
                            : abrirPersonalizacion(usuario.id)
                        }
                      >
                        <KeyRound className="h-3.5 w-3.5" />
                        Definir
                      </Button>
                    </div>
                  </div>

                  {usuarioPersonalizando === usuario.id && (
                    <div className="mt-2.5 flex items-center gap-2 border-t border-border pt-2.5">
                      <PasswordInput
                        autoFocus
                        placeholder={`Mínimo ${LONGITUD_MINIMA_PASSWORD} caracteres`}
                        value={passwordPersonalizada}
                        onChange={(e) => setPasswordPersonalizada(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && confirmarPersonalizada(usuario.id)}
                        className="h-9"
                      />
                      <Button
                        size="sm"
                        loading={enviandoPersonalizada}
                        onClick={() => confirmarPersonalizada(usuario.id)}
                      >
                        Confirmar
                      </Button>
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </DialogContent>
    </Dialog>
  );
}
