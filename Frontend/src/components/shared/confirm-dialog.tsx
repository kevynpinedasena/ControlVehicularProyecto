import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface ConfirmDialogProps {
  abierto: boolean;
  onCerrar: () => void;
  onConfirmar: () => void;
  titulo: string;
  descripcion: string;
  textoConfirmar?: string;
  textoCancelar?: string;
  cargando?: boolean;
  destructivo?: boolean;
}

export function ConfirmDialog({
  abierto,
  onCerrar,
  onConfirmar,
  titulo,
  descripcion,
  textoConfirmar = "Eliminar",
  textoCancelar = "Cancelar",
  cargando = false,
  destructivo = true,
}: ConfirmDialogProps) {
  return (
    <Dialog open={abierto} onOpenChange={(open) => !open && !cargando && onCerrar()}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>{titulo}</DialogTitle>
          <DialogDescription>{descripcion}</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={onCerrar} disabled={cargando}>
            {textoCancelar}
          </Button>
          <Button
            type="button"
            variant={destructivo ? "destructive" : "default"}
            loading={cargando}
            onClick={onConfirmar}
          >
            {textoConfirmar}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}