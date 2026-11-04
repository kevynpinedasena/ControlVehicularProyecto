import { MutationCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "framer-motion";
import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";

import { router } from "@/app/router";
import { Toaster, notificar } from "@/components/ui/toaster";
import { AuthProvider } from "@/features/auth/auth-context";
import { obtenerMensajeError } from "@/services/api-client";

import "@fontsource-variable/instrument-sans/wght.css";
import "@fontsource-variable/bricolage-grotesque/index.css";
import "@fontsource/barlow-semi-condensed/600.css";

import "@/index.css";

declare module "@tanstack/react-query" {
  interface Register {
    mutationMeta: {
      /** Mensaje que se muestra como aviso cuando la mutación termina bien. */
      exito?: string;
      /** La pantalla ya muestra el error por su cuenta; no duplicarlo en un aviso. */
      silenciarError?: boolean;
    };
  }
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
  mutationCache: new MutationCache({
    onSuccess: (_datos, _variables, _contexto, mutacion) => {
      if (mutacion.meta?.exito) notificar.exito(mutacion.meta.exito);
    },
    onError: (error, _variables, _contexto, mutacion) => {
      // Solo avisa si la pantalla no maneja el error (evita fallos silenciosos sin duplicar mensajes).
      if (mutacion.options.onError || mutacion.meta?.silenciarError) return;
      notificar.error(obtenerMensajeError(error, "No se pudo completar la acción"));
    },
  }),
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <MotionConfig reducedMotion="user">
        <AuthProvider>
          <RouterProvider router={router} />
        </AuthProvider>
        <Toaster />
      </MotionConfig>
    </QueryClientProvider>
  </React.StrictMode>,
);
