import { useIsMutating } from "@tanstack/react-query";

import { Spinner } from "@/components/ui/spinner";
import { useCargaGlobalManual } from "@/lib/carga-global";

/** Se monta una sola vez en la raíz de la app. Mientras haya alguna mutación de React Query
 * en curso (crear/editar/eliminar, iniciar sesión con useMutation, etc.) o una operación
 * marcada manualmente con `conCargaGlobal` (el login, que no pasa por React Query), cubre
 * toda la pantalla con un spinner y bloquea cualquier clic hasta que termine. */
export function GlobalLoadingOverlay() {
  const mutacionesEnCurso = useIsMutating();
  const cargaManual = useCargaGlobalManual();

  if (mutacionesEnCurso === 0 && !cargaManual) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-background/60 backdrop-blur-[1px]"
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <div className="flex flex-col items-center gap-3 rounded-xl border border-border bg-card px-6 py-5 shadow-lg">
        <Spinner className="h-8 w-8" />
        <p className="text-sm font-medium text-muted-foreground">Procesando...</p>
      </div>
    </div>
  );
}
