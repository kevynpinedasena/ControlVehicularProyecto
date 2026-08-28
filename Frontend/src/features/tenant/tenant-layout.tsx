import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { Navigate, Outlet, useParams } from "react-router-dom";

import { Spinner } from "@/components/ui/spinner";
import { TenantContext } from "@/features/tenant/tenant-context";
import { colorDeTexto, hexAHsl } from "@/lib/color";
import { businessUnitService } from "@/services/business-unit-service";

export function TenantLayout() {
  const { slug } = useParams<{ slug: string }>();

  const unidadQuery = useQuery({
    queryKey: ["business-unit-public", slug],
    queryFn: () => businessUnitService.obtenerPublica(slug!),
    enabled: Boolean(slug),
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    const unidad = unidadQuery.data;
    if (!unidad) return;

    // Solo se tiñe el color primario (botones, enlaces, foco). El resto de la UI
    // (fondos, badges neutrales) se mantiene fija para garantizar buen contraste
    // sin importar qué color elija cada unidad de negocio.
    const raiz = document.documentElement;
    const primario = hexAHsl(unidad.color_primario);
    if (primario) {
      raiz.style.setProperty("--primary", primario);
      raiz.style.setProperty("--ring", primario);
      raiz.style.setProperty("--primary-foreground", colorDeTexto(unidad.color_primario));
    }

    return () => {
      raiz.style.removeProperty("--primary");
      raiz.style.removeProperty("--ring");
      raiz.style.removeProperty("--primary-foreground");
    };
  }, [unidadQuery.data]);

  if (unidadQuery.isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (unidadQuery.isError || !unidadQuery.data || !slug) {
    return <Navigate to="/" replace />;
  }

  if (!unidadQuery.data.activo) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-2 px-4 text-center">
        <h1 className="text-xl font-semibold">Unidad deshabilitada</h1>
        <p className="text-muted-foreground">
          "{unidadQuery.data.nombre}" se encuentra deshabilitada temporalmente. Contacta al
          administrador de la plataforma.
        </p>
        <a href="/" className="mt-2 text-sm text-primary underline">
          Volver al inicio
        </a>
      </div>
    );
  }

  return (
    <TenantContext.Provider value={{ unidad: unidadQuery.data, slug }}>
      <Outlet />
    </TenantContext.Provider>
  );
}
