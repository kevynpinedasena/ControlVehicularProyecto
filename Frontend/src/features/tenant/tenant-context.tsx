import { createContext, useContext } from "react";

import type { UnidadNegocioPublica } from "@/types";

export interface TenantContextValue {
  unidad: UnidadNegocioPublica;
  slug: string;
}

export const TenantContext = createContext<TenantContextValue | undefined>(undefined);

export function useTenant(): TenantContextValue {
  const contexto = useContext(TenantContext);
  if (!contexto) throw new Error("useTenant debe usarse dentro de una ruta con TenantLayout");
  return contexto;
}
