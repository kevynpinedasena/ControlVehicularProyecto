/** Resuelve una ruta de logo relativa (ej. "/uploads/logos/x.png") a una URL absoluta del backend.
 * Los logos nuevos llegan como data URI (`data:image/...;base64,...`) y se devuelven tal cual. */
export function urlLogo(logoUrl: string | null | undefined): string | null {
  if (!logoUrl) return null;
  if (/^(https?:|data:)/.test(logoUrl)) return logoUrl;

  const base = (import.meta.env.VITE_API_URL ?? "").replace(/\/api\/v1\/?$/, "");
  return `${base}${logoUrl}`;
}
