import { useIsMutating } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2 } from "lucide-react";

import { useCargaGlobalManual } from "@/lib/carga-global";

/** Se monta una sola vez en la raíz de la app. Mientras haya alguna mutación de React Query
 * en curso (crear/editar/eliminar, iniciar sesión con useMutation, etc.) o una operación
 * marcada manualmente con `conCargaGlobal` (el login, que no pasa por React Query), cubre
 * toda la pantalla con un spinner y bloquea cualquier clic hasta que termine. */
export function GlobalLoadingOverlay() {
  const mutacionesEnCurso = useIsMutating();
  const cargaManual = useCargaGlobalManual();
  const visible = mutacionesEnCurso > 0 || cargaManual;

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          key="overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-background/60 backdrop-blur-[2px]"
          role="status"
          aria-live="polite"
          aria-busy="true"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94 }}
            transition={{ type: "spring", stiffness: 320, damping: 24 }}
            className="flex flex-col items-center gap-3 rounded-2xl border border-border bg-card px-7 py-6 shadow-xl"
          >
            {/* Color fijo a propósito (no --primary): algunos conjuntos configuran un color
                primario gris/neutro, lo que dejaría el spinner sin vida en su marca. */}
            <div className="relative flex h-12 w-12 items-center justify-center">
              <motion.span
                className="absolute inset-0 rounded-full bg-[#2563eb]/15"
                animate={{ scale: [1, 1.3, 1], opacity: [0.7, 0.15, 0.7] }}
                transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
              />
              <Loader2 className="h-7 w-7 animate-spin text-[#2563eb]" />
            </div>
            <p className="text-sm font-medium text-foreground">Procesando...</p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
