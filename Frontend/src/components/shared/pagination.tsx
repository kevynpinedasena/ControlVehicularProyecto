import { ChevronLeft, ChevronRight } from "lucide-react";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";

export const TAMANOS_PAGINA = [50, 100, 150] as const;

interface PaginationProps {
  pagina: number;
  onCambiarPagina: (pagina: number) => void;
  tamanoPagina: number;
  onCambiarTamanoPagina: (tamano: number) => void;
  cantidadEnPagina: number;
}

export function Pagination({
  pagina,
  onCambiarPagina,
  tamanoPagina,
  onCambiarTamanoPagina,
  cantidadEnPagina,
}: PaginationProps) {
  const hayPaginaAnterior = pagina > 1;
  const hayPaginaSiguiente = cantidadEnPagina === tamanoPagina;
  const desde = cantidadEnPagina === 0 ? 0 : (pagina - 1) * tamanoPagina + 1;
  const hasta = (pagina - 1) * tamanoPagina + cantidadEnPagina;

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border/70 px-4 py-2.5 text-xs text-muted-foreground">
      <div className="flex items-center gap-1.5">
        <span>Filas por página</span>
        <Select
          value={String(tamanoPagina)}
          onValueChange={(v) => {
            onCambiarTamanoPagina(Number(v));
            onCambiarPagina(1);
          }}
        >
          <SelectTrigger className="h-6 w-[60px] gap-1 border-0 bg-transparent px-1.5 text-xs font-medium text-foreground shadow-none hover:bg-secondary focus:ring-1 focus:ring-ring">
            <SelectValue />
          </SelectTrigger>
          <SelectContent align="start">
            {TAMANOS_PAGINA.map((tamano) => (
              <SelectItem key={tamano} value={String(tamano)} className="text-xs">
                {tamano}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center gap-4">
        <span>{cantidadEnPagina === 0 ? "Sin resultados" : `${desde}–${hasta}`}</span>
        <div className="flex items-center gap-0.5">
          <PaginationIcon
            direccion="anterior"
            disabled={!hayPaginaAnterior}
            onClick={() => onCambiarPagina(pagina - 1)}
          />
          <span className="min-w-[1.25rem] text-center font-medium text-foreground">{pagina}</span>
          <PaginationIcon
            direccion="siguiente"
            disabled={!hayPaginaSiguiente}
            onClick={() => onCambiarPagina(pagina + 1)}
          />
        </div>
      </div>
    </div>
  );
}

function PaginationIcon({
  direccion,
  disabled,
  onClick,
}: {
  direccion: "anterior" | "siguiente";
  disabled: boolean;
  onClick: () => void;
}) {
  const Icono = direccion === "anterior" ? ChevronLeft : ChevronRight;
  return (
    <button
      type="button"
      aria-label={`Página ${direccion}`}
      disabled={disabled}
      onClick={onClick}
      className={cn(
        "flex h-6 w-6 items-center justify-center rounded-md transition-colors",
        disabled
          ? "cursor-not-allowed opacity-30"
          : "text-foreground hover:bg-secondary active:bg-secondary/80",
      )}
    >
      <Icono className="h-3.5 w-3.5" />
    </button>
  );
}
