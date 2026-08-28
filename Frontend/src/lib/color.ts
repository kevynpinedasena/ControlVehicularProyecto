/** Convierte un color hexadecimal (#rrggbb) al formato "H S% L%" usado por las variables CSS. */
export function hexAHsl(hex: string): string | null {
  const limpio = hex.trim().replace("#", "");
  if (!/^[0-9a-fA-F]{6}$/.test(limpio)) return null;

  const r = parseInt(limpio.slice(0, 2), 16) / 255;
  const g = parseInt(limpio.slice(2, 4), 16) / 255;
  const b = parseInt(limpio.slice(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;
  let h = 0;
  let s = 0;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) * 60;
        break;
      case g:
        h = ((b - r) / d + 2) * 60;
        break;
      default:
        h = ((r - g) / d + 4) * 60;
    }
  }

  return `${h.toFixed(1)} ${(s * 100).toFixed(1)}% ${(l * 100).toFixed(1)}%`;
}

/** Elige texto blanco o negro según el brillo percibido del color, para buen contraste
 * (formato "H S% L%", para usar en variables CSS). */
export function colorDeTexto(hex: string): string {
  const limpio = hex.trim().replace("#", "");
  if (!/^[0-9a-fA-F]{6}$/.test(limpio)) return "0 0% 100%";
  const r = parseInt(limpio.slice(0, 2), 16);
  const g = parseInt(limpio.slice(2, 4), 16);
  const b = parseInt(limpio.slice(4, 6), 16);
  const brillo = (r * 299 + g * 587 + b * 114) / 1000;
  return brillo > 150 ? "222 47% 11%" : "0 0% 100%";
}

/** Igual que colorDeTexto, pero como color hexadecimal listo para usar en un `style` inline. */
export function textoContrastante(hex: string): string {
  const limpio = hex.trim().replace("#", "");
  if (!/^[0-9a-fA-F]{6}$/.test(limpio)) return "#ffffff";
  const r = parseInt(limpio.slice(0, 2), 16);
  const g = parseInt(limpio.slice(2, 4), 16);
  const b = parseInt(limpio.slice(4, 6), 16);
  const brillo = (r * 299 + g * 587 + b * 114) / 1000;
  return brillo > 150 ? "#0f172a" : "#ffffff";
}
