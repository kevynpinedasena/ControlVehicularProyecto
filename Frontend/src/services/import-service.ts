import { apiClient } from "@/services/api-client";
import type { ReporteImportacion } from "@/types";

export const importService = {
  descargarPlantilla: async () => {
    const respuesta = await apiClient.get("/import/template", { responseType: "blob" });
    return respuesta.data as Blob;
  },
  subirArchivo: async (archivo: File) => {
    const formData = new FormData();
    formData.append("archivo", archivo);
    const { data } = await apiClient.post<ReporteImportacion>("/import/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },
};
