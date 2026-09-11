import { useSyncExternalStore } from "react";

/** Contador de operaciones en curso que no pasan por React Query (ej. el login, que
 * actualiza tokens y contexto antes de poder redirigir). Se combina con `useIsMutating()`
 * en <GlobalLoadingOverlay> para bloquear la pantalla completa mientras cualquiera de
 * las dos esté en curso. */
let contador = 0;
const listeners = new Set<() => void>();

function notificar() {
  listeners.forEach((listener) => listener());
}

export function iniciarCargaGlobal() {
  contador += 1;
  notificar();
}

export function terminarCargaGlobal() {
  contador = Math.max(0, contador - 1);
  notificar();
}

export async function conCargaGlobal<T>(accion: () => Promise<T>): Promise<T> {
  iniciarCargaGlobal();
  try {
    return await accion();
  } finally {
    terminarCargaGlobal();
  }
}

export function useCargaGlobalManual(): boolean {
  return useSyncExternalStore(
    (listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    () => contador > 0,
  );
}
