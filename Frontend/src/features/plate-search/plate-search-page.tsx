import { useMutation } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { Car, ParkingSquare, Phone, Search, ShieldAlert, ShieldCheck } from "lucide-react";
import { type ReactNode, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { obtenerMensajeError } from "@/services/api-client";
import { vehicleService } from "@/services/vehicle-service";
import type { ConsultaPlacaResultado } from "@/types";

export function PlateSearchPage() {
  const [placa, setPlaca] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const mutacion = useMutation({
    mutationFn: (valor: string) => vehicleService.consultarPlaca(valor),
  });

  const buscar = () => {
    if (!placa.trim()) return;
    mutacion.mutate(placa.trim());
  };

  const reiniciar = () => {
    mutacion.reset();
    setPlaca("");
    inputRef.current?.focus();
  };

  return (
    <div className="flex min-h-full items-center justify-center">
    <div className="w-full max-w-lg">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold tracking-tight">Consulta de vehículo</h1>
        <p className="mt-1 text-muted-foreground">Ingresa la placa para verificar el registro</p>
      </div>

      <div className="flex gap-2">
        <Input
          ref={inputRef}
          autoFocus
          value={placa}
          onChange={(e) => setPlaca(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === "Enter" && buscar()}
          placeholder="ABC123"
          maxLength={10}
          className="h-14 text-center text-2xl font-bold uppercase tracking-widest"
        />
      </div>

      <Button
        onClick={buscar}
        loading={mutacion.isPending}
        disabled={!placa.trim()}
        size="lg"
        className="mt-4 w-full gap-2"
      >
        <Search className="h-5 w-5" />
        Buscar
      </Button>

      <div className="mt-6">
        <AnimatePresence mode="wait">
          {mutacion.isPending && (
            <motion.div
              key="cargando"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex justify-center py-10"
            >
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary/20 border-t-primary" />
            </motion.div>
          )}

          {mutacion.isError && (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
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
    </div>
  );
}

function telefonosDe(resultado: ConsultaPlacaResultado) {
  const telefonos = [resultado.telefono_1, resultado.telefono_2].filter(Boolean);
  return telefonos.length > 0 ? telefonos.join(" / ") : "-";
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
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0 }}
        transition={{ type: "spring", stiffness: 300, damping: 20 }}
        className="rounded-2xl border-2 border-destructive/30 bg-destructive/5 p-6 text-center"
      >
        <motion.div
          initial={{ rotate: 0 }}
          animate={{ rotate: [0, -8, 8, -4, 0] }}
          transition={{ duration: 0.4 }}
          className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-destructive/10"
        >
          <ShieldAlert className="h-7 w-7 text-destructive" />
        </motion.div>
        <h2 className="text-lg font-bold text-destructive">VEHÍCULO NO REGISTRADO</h2>
        <p className="mt-1 text-sm text-muted-foreground">{resultado.mensaje}</p>
        <Button variant="outline" className="mt-4" onClick={onReiniciar}>
          Nueva consulta
        </Button>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 22 }}
      className="rounded-2xl border-2 border-success/30 bg-success/5 p-6"
    >
      <div className="flex flex-col items-center text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 400, damping: 15, delay: 0.1 }}
          className="mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-success/10"
        >
          <ShieldCheck className="h-7 w-7 text-success" />
        </motion.div>
        <h2 className="text-lg font-bold text-success">VEHÍCULO REGISTRADO</h2>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="mt-5 space-y-2 rounded-xl bg-card p-4"
      >
        <Fila etiqueta="Placa" valor={resultado.placa} destacado />
        <Fila
          etiqueta="Tipo"
          valor={resultado.tipo_vehiculo?.nombre ?? "-"}
          icono={<Car className="h-4 w-4" />}
        />
        <Fila etiqueta="Torre" valor={resultado.torre ?? "-"} />
        <Fila etiqueta="Apartamento" valor={resultado.apartamento ?? "-"} />
        <Fila
          etiqueta="Parqueadero"
          valor={resultado.parqueadero ?? "Sin asignar"}
          icono={<ParkingSquare className="h-4 w-4" />}
        />
        <Fila etiqueta="Residente" valor={resultado.tipo_residente?.nombre ?? "-"} />
        <Fila
          etiqueta="Teléfonos"
          valor={telefonosDe(resultado)}
          icono={<Phone className="h-4 w-4" />}
        />
        <Fila etiqueta="Estado" valor={resultado.estado ?? "-"} />
      </motion.div>

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
    <div className="flex items-center justify-between border-b border-border py-1.5 last:border-0">
      <span className="text-sm text-muted-foreground">{etiqueta}</span>
      <span
        className={
          destacado
            ? "flex items-center gap-1.5 font-mono text-lg font-bold tracking-wider"
            : "flex items-center gap-1.5 text-sm font-medium"
        }
      >
        {icono}
        {valor}
      </span>
    </div>
  );
}
