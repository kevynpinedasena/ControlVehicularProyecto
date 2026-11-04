import { AnimatePresence, motion } from "framer-motion";
import { CircleAlert, CircleCheck, X } from "lucide-react";
import { useSyncExternalStore } from "react";

import { cn } from "@/lib/utils";

type TipoAviso = "exito" | "error";

interface Aviso {
  id: number;
  tipo: TipoAviso;
  mensaje: string;
}

const DURACION_MS: Record<TipoAviso, number> = { exito: 3200, error: 6000 };
const MAXIMO_VISIBLES = 3;

let avisos: Aviso[] = [];
let siguienteId = 1;
const suscriptores = new Set<() => void>();
const temporizadores = new Map<number, ReturnType<typeof setTimeout>>();

function emitir() {
  for (const fn of suscriptores) fn();
}

function cerrar(id: number) {
  clearTimeout(temporizadores.get(id));
  temporizadores.delete(id);
  avisos = avisos.filter((a) => a.id !== id);
  emitir();
}

function agregar(tipo: TipoAviso, mensaje: string) {
  // Evita apilar el mismo mensaje si la acción se repite rápido.
  const repetido = avisos.find((a) => a.tipo === tipo && a.mensaje === mensaje);
  if (repetido) cerrar(repetido.id);

  const id = siguienteId++;
  avisos = [...avisos, { id, tipo, mensaje }].slice(-MAXIMO_VISIBLES);
  temporizadores.set(id, setTimeout(() => cerrar(id), DURACION_MS[tipo]));
  emitir();
}

export const notificar = {
  exito: (mensaje: string) => agregar("exito", mensaje),
  error: (mensaje: string) => agregar("error", mensaje),
};

function suscribir(fn: () => void) {
  suscriptores.add(fn);
  return () => suscriptores.delete(fn);
}

export function Toaster() {
  const lista = useSyncExternalStore(suscribir, () => avisos);

  return (
    <div
      aria-live="polite"
      className="pointer-events-none fixed inset-x-0 bottom-0 z-[60] flex flex-col items-center gap-2 p-4 sm:inset-x-auto sm:right-0 sm:items-end sm:p-6"
    >
      <AnimatePresence initial={false}>
        {lista.map((aviso) => {
          const Icono = aviso.tipo === "exito" ? CircleCheck : CircleAlert;
          return (
            <motion.div
              key={aviso.id}
              layout
              role={aviso.tipo === "error" ? "alert" : "status"}
              initial={{ opacity: 0, y: 12, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1, transition: { duration: 0.24, ease: [0.16, 1, 0.3, 1] } }}
              exit={{ opacity: 0, scale: 0.98, transition: { duration: 0.14, ease: "easeIn" } }}
              className="pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-lg border border-border bg-card py-3 pl-3.5 pr-2 text-sm text-card-foreground shadow-[0_10px_30px_-12px_rgb(15_23_42/0.25)]"
            >
              <Icono
                aria-hidden
                className={cn(
                  "mt-px h-[18px] w-[18px] shrink-0",
                  aviso.tipo === "exito" ? "text-success" : "text-destructive",
                )}
              />
              <p className="min-w-0 flex-1 leading-snug">{aviso.mensaje}</p>
              <button
                type="button"
                aria-label="Cerrar aviso"
                onClick={() => cerrar(aviso.id)}
                className="-my-0.5 shrink-0 rounded-md p-1 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
