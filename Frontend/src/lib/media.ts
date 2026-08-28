/** Resuelve una ruta de logo relativa (ej. "/uploads/logos/x.png") a una URL absoluta del backend. */
export function urlLogo(logoUrl: string | null | undefined): string | null {
  if (!logoUrl) return null;
  if (/^https?:\/\//.test(logoUrl)) return logoUrl;

  const base = (import.meta.env.VITE_API_URL ?? "").replace(/\/api\/v1\/?$/, "");
  return `${base}${logoUrl}`;
}
