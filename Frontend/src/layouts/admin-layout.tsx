import {
  Building2,
  Car,
  LayoutDashboard,
  LogOut,
  ParkingSquare,
  Search,
  Upload,
  Users,
  UserSquare2,
} from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

import { TenantLogo } from "@/components/shared/tenant-logo";
import { textoContrastante } from "@/lib/color";
import { cn } from "@/lib/utils";
import { useAuth } from "@/features/auth/auth-context";
import { useTenant } from "@/features/tenant/tenant-context";

export function AdminLayout() {
  const { usuario, cerrarSesion } = useAuth();
  const { unidad, slug } = useTenant();
  const colorTexto = textoContrastante(unidad.color_secundario);

  const enlaces = [
    { to: `/${slug}/admin/dashboard`, label: "Panel", icon: LayoutDashboard },
    { to: `/${slug}/admin/residents`, label: "Residentes", icon: UserSquare2 },
    { to: `/${slug}/admin/vehicles`, label: "Vehículos", icon: Car },
    { to: `/${slug}/admin/locations`, label: "Torres y apartamentos", icon: Building2 },
    { to: `/${slug}/admin/parking`, label: "Parqueaderos", icon: ParkingSquare },
    { to: `/${slug}/admin/users`, label: "Usuarios", icon: Users },
    { to: `/${slug}/admin/import`, label: "Carga masiva", icon: Upload },
    { to: `/${slug}/consulta-placa`, label: "Consultar placa", icon: Search },
  ];

  return (
    <div className="flex min-h-screen bg-secondary/40">
      <aside
        className="flex w-64 shrink-0 flex-col"
        style={{ backgroundColor: unidad.color_secundario, color: colorTexto }}
      >
        <div className="flex items-center gap-2 px-6 py-5">
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
            <p className="truncate text-xs opacity-70">Control Vehicular</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3">
          {enlaces.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "opacity-80 hover:bg-current/10 hover:opacity-100",
                )
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-current/15 p-3">
          <div className="mb-2 rounded-lg bg-current/10 px-3 py-2">
            <p className="truncate text-sm font-medium">{usuario?.nombre}</p>
            <p className="truncate text-xs opacity-70">{usuario?.correo}</p>
          </div>
          <button
            onClick={cerrarSesion}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium opacity-80 transition-colors hover:bg-current/10 hover:opacity-100"
          >
            <LogOut className="h-4 w-4" />
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto p-8">
        <Outlet />
      </main>
    </div>
  );
}
