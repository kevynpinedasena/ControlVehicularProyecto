// Curvas y duraciones compartidas. Desaceleración tipo "expo out": llega con decisión, sin rebote.
export const EASE_SALIDA = [0.16, 1, 0.3, 1] as const;

/** Cambio de vista dentro de un layout: breve, para no hacer esperar. */
export const TRANSICION_PAGINA = { duration: 0.18, ease: EASE_SALIDA } as const;

/** Indicador activo del menú que se desliza entre secciones. */
export const TRANSICION_INDICADOR = { duration: 0.28, ease: EASE_SALIDA } as const;

/** Veredicto de la consulta de placa: se despliega desde el campo de búsqueda. */
export const TRANSICION_VEREDICTO = { duration: 0.32, ease: EASE_SALIDA } as const;
