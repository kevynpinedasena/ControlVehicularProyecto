import { ArrowLeft, Car, LogOut, Search, UserSquare2 } from "lucide-react";
import { motion } from "framer-motion";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";

import { TenantLogo } from "@/components/shared/tenant-logo";
import { TRANSICION_INDICADOR, TRANSICION_PAGINA } from "@/lib/motion";
import { textoContrastante } from "@/lib/color";
import { cn } from "@/lib/utils";
import { useAuth } from "@/features/auth/auth-context";
import { useTenant } from "@/features/tenant/tenant-context";

export function VigilanteLayout() {
  const { usuario, cerrarSesion } = useAuth();
  const { unidad, slug } = useTenant();
  const colorTexto = textoContrastante(unidad.color_secundario);
  const { pathname } = useLocation();

  const enlaces = [
    { to: `/${slug}/consulta-placa`, label: "Consultar placa", icon: Search },
    { to: `/${slug}/residents`, label: "Residentes", icon: UserSquare2 },
  ];

  return (
    <div className="flex min-h-screen flex-col bg-secondary/40">
      <header
        className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3 px-4 py-3 lg:px-8"
        style={{ backgroundColor: unidad.color_secundario, color: colorTexto }}
      >
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-current/10">
            <TenantLogo
              logoUrl={unidad.logo_url}
              nombre={unidad.nombre}
              icono={Car}
              className="h-9 w-9 rounded-lg"
              iconoClassName="h-5 w-5"
            />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold leading-tight">{unidad.nombre}</p>
            <p className="text-xs opacity-70">Puesto de vigilancia</p>
          </div>
        </div>

        <nav className="flex items-center gap-1">
          {enlaces.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  "relative flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-[background-color,opacity,color] duration-150",
                  isActive ? "text-primary-foreground" : "opacity-80 hover:bg-current/10 hover:opacity-100",
                )
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.span
                      layoutId="indicador-menu-vigilante"
                      transition={TRANSICION_INDICADOR}
                      className="absolute inset-0 rounded-lg bg-primary"
                    />
                  )}
                  <Icon className="relative h-4 w-4" />
                  <span className="relative">{label}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="flex shrink-0 items-center gap-3">
          {usuario?.rol === "SUPER_ADMIN" && (
            <Link
              to={`/${slug}/admin/dashboard`}
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium opacity-80 transition-colors hover:bg-current/10 hover:opacity-100"
            >
              <ArrowLeft className="h-4 w-4" />
              Volver al panel
            </Link>
          )}
          <p className="hidden text-sm opacity-70 sm:block">{usuario?.nombre}</p>
          <button
            type="button"
            onClick={cerrarSesion}
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium opacity-80 transition-colors hover:bg-current/10 hover:opacity-100"
          >
            <LogOut className="h-4 w-4" />
            Salir
          </button>
        </div>
      </header>
      <main className="flex-1 overflow-y-auto p-4 lg:p-8">
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={TRANSICION_PAGINA}
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  );
}
