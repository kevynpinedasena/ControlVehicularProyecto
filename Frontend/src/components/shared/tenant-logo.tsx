import type { LucideIcon } from "lucide-react";
import { useState } from "react";

import { urlLogo } from "@/lib/media";
import { cn } from "@/lib/utils";

interface TenantLogoProps {
  logoUrl: string | null | undefined;
  nombre: string;
  icono: LucideIcon;
  className?: string;
  iconoClassName?: string;
}

export function TenantLogo({ logoUrl, nombre, icono: Icono, className, iconoClassName }: TenantLogoProps) {
  const [fallo, setFallo] = useState(false);
  const url = urlLogo(logoUrl);

  if (!url || fallo) {
    return <Icono className={cn("text-primary", iconoClassName)} />;
  }

  return (
    <img
      src={url}
      alt={nombre}
      className={cn("object-cover", className)}
      onError={() => setFallo(true)}
    />
  );
}
