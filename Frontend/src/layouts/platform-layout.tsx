import { LogOut, ShieldCheck } from "lucide-react";
import { Outlet } from "react-router-dom";

import { useAuth } from "@/features/auth/auth-context";

export function PlatformLayout() {
  const { usuario, cerrarSesion } = useAuth();

  return (
    <div className="min-h-screen bg-secondary/40">
      <header className="flex items-center justify-between border-b border-border bg-slate-950 px-6 py-4 text-white">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-white/10 p-2">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-semibold leading-tight">Administración de Plataforma</p>
            <p className="text-xs text-white/60">Unidades de negocio</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <p className="hidden text-sm text-white/70 sm:block">{usuario?.nombre}</p>
          <button
            onClick={cerrarSesion}
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-white/70 transition-colors hover:bg-white/10 hover:text-white"
          >
            <LogOut className="h-4 w-4" />
            Salir
          </button>
        </div>
      </header>
      <main className="p-8">
        <Outlet />
      </main>
    </div>
  );
}
