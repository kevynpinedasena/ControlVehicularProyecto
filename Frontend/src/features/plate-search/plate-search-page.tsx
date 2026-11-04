import { useMutation } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { Car, ParkingSquare, Phone, Search, ShieldAlert, ShieldCheck } from "lucide-react";
import { type ReactNode, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { TRANSICION_VEREDICTO } from "@/lib/motion";
import { cn } from "@/lib/utils";
import { obtenerMensajeError } from "@/services/api-client";
import { vehicleService } from "@/services/vehicle-service";
import type { ConsultaPlacaResultado } from "@/types";

export function PlateSearchPage() {
  const [placa, setPlaca] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const mutacion = useMutation({
    meta: { silenciarError: true },
    mutationFn: (valor: string) => vehicleService.consultarPlaca(valor),
  });

  const buscar = () => {
    if (!placa.trim()) return;
    mutacion.mutate(placa.trim());
  };

  // El color del veredicto solo acompaña al campo mientras muestra la placa consultada.
  const veredictoVigente = mutacion.isSuccess && mutacion.variables === placa.trim();
  const veredicto = veredictoVigente ? (mutacion.data.registrado ? "registrado" : "no-registrado") : null;

  const reiniciar = () => {
    mutacion.reset();
    setPlaca("");
    inputRef.current?.focus();
  };

  return (
    <div className="mx-auto w-full max-w-lg pt-4 sm:pt-10">
      <div className="mb-6 text-center">
        <h1 className="text-[1.75rem] font-semibold leading-tight tracking-tight">Consulta de vehículo</h1>
        <p className="mt-1 text-muted-foreground">Ingresa la placa para verificar el registro</p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          buscar();
        }}
      >
        <Input
          ref={inputRef}
          autoFocus
          aria-label="Placa del vehículo"
          autoComplete="off"
          spellCheck={false}
          value={placa}
          onChange={(e) => setPlaca(e.target.value.toUpperCase())}
          placeholder="ABC123"
          maxLength={10}
          className={cn(
            "h-14 text-center font-placa text-3xl font-semibold uppercase tracking-[0.18em] transition-[border-color,box-shadow] duration-300 placeholder:text-muted-foreground/50",
            veredicto === "registrado" && "border-success/60 ring-4 ring-success/15 hover:border-success/60",
            veredicto === "no-registrado" && "border-destructive/60 ring-4 ring-destructive/15 hover:border-destructive/60",
          )}
        />

        <Button
          type="submit"
          loading={mutacion.isPending}
          disabled={!placa.trim()}
          size="lg"
          className="mt-3 w-full"
        >
          {!mutacion.isPending && <Search className="h-4 w-4" />}
          Buscar
        </Button>
      </form>

      <div className="mt-6">
        <AnimatePresence mode="wait">
          {mutacion.isPending && (
            <motion.div
              key="cargando"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1, transition: { delay: 0.12, duration: 0.15 } }}
              exit={{ opacity: 0, transition: { duration: 0.08 } }}
              className="flex justify-center py-10"
            >
              <Spinner className="h-8 w-8" />
            </motion.div>
          )}

          {mutacion.isError && (
            <motion.div
              key="error"
              {...ENTRADA_VEREDICTO}
              role="alert"
              className="rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-center text-sm text-destructive"
            >
              {obtenerMensajeError(mutacion.error, "No se pudo consultar la placa")}
            </motion.div>
          )}

          {mutacion.isSuccess && (
            <ResultadoConsulta key="resultado" resultado={mutacion.data} onReiniciar={reiniciar} />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// El veredicto se despliega hacia abajo desde el campo de búsqueda: la respuesta "sale" de la placa.
const ENTRADA_VEREDICTO = {
  initial: { opacity: 0, clipPath: "inset(0% 0% 100% 0% round 12px)" },
  animate: { opacity: 1, clipPath: "inset(0% 0% 0% 0% round 12px)", transition: TRANSICION_VEREDICTO },
  exit: { opacity: 0, transition: { duration: 0.1 } },
} as const;

function telefonosDe(resultado: ConsultaPlacaResultado) {
  const telefonos = [resultado.telefono_1, resultado.telefono_2].filter(Boolean);
  return telefonos.length > 0 ? telefonos.join(" / ") : "—";
}

function ResultadoConsulta({
  resultado,
  onReiniciar,
}: {
  resultado: ConsultaPlacaResultado;
  onReiniciar: () => void;
}) {
  if (!resultado.registrado) {
    return (
      <motion.div
        role="status"
        {...ENTRADA_VEREDICTO}
        className="rounded-xl border border-destructive/30 bg-destructive/5 p-6 text-center"
      >
        <ShieldAlert className="mx-auto mb-3 h-10 w-10 text-destructive" strokeWidth={1.75} aria-hidden />
        <h2 className="text-lg font-semibold text-destructive">Vehículo no registrado</h2>
        <p className="mt-1 text-sm text-muted-foreground">{resultado.mensaje}</p>
        <Button variant="outline" className="mt-4" onClick={onReiniciar}>
          Nueva consulta
        </Button>
      </motion.div>
    );
  }

  return (
    <motion.div
      role="status"
      {...ENTRADA_VEREDICTO}
      className="rounded-xl border border-success/30 bg-success/5 p-5 sm:p-6"
    >
      <div className="flex flex-col items-center text-center">
        <ShieldCheck className="mb-3 h-10 w-10 text-success" strokeWidth={1.75} aria-hidden />
        <h2 className="text-lg font-semibold text-success">Vehículo registrado</h2>
      </div>

      <dl className="mt-5 rounded-lg border border-border bg-card px-4 py-1">
        <Fila etiqueta="Placa" valor={resultado.placa} destacado />
        <Fila
          etiqueta="Tipo"
          valor={resultado.tipo_vehiculo?.nombre ?? "—"}
          icono={<Car className="h-4 w-4" />}
        />
        <Fila etiqueta="Torre" valor={resultado.torre ?? "—"} />
        <Fila etiqueta="Apartamento" valor={resultado.apartamento ?? "—"} />
        <Fila
          etiqueta="Parqueadero"
          valor={resultado.parqueadero ?? "Sin asignar"}
          icono={<ParkingSquare className="h-4 w-4" />}
        />
        <Fila etiqueta="Residente" valor={resultado.tipo_residente?.nombre ?? "—"} />
        <Fila
          etiqueta="Teléfonos"
          valor={telefonosDe(resultado)}
          icono={<Phone className="h-4 w-4" />}
        />
        <Fila etiqueta="Estado" valor={resultado.estado ?? "—"} />
      </dl>

      <Button variant="outline" className="mt-4 w-full" onClick={onReiniciar}>
        Nueva consulta
      </Button>
    </motion.div>
  );
}

function Fila({
  etiqueta,
  valor,
  destacado,
  icono,
}: {
  etiqueta: string;
  valor: string;
  destacado?: boolean;
  icono?: ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-border py-2.5 last:border-0">
      <dt className="text-sm text-muted-foreground">{etiqueta}</dt>
      <dd
        className={
          destacado
            ? "flex items-center gap-1.5 font-placa text-xl font-semibold tracking-wider"
            : "flex min-w-0 items-center gap-1.5 text-right text-sm font-medium"
        }
      >
        {icono && <span className="shrink-0 text-muted-foreground">{icono}</span>}
        {valor}
      </dd>
    </div>
  );
}
