import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Bike, Building2, Car, UserSquare2, Users } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useNavigate } from "react-router-dom";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { useTenant } from "@/features/tenant/tenant-context";
import { apartmentService, towerService } from "@/services/location-service";
import { residentService } from "@/services/resident-service";
import { vehicleService } from "@/services/vehicle-service";

// Paleta categórica validada (contraste CVD adyacente >= 8 / lectura normal >= 15).
const SERIE_1 = "#2a78d6"; // azul
const SERIE_2 = "#eb6834"; // naranja

export function DashboardPage() {
  const navigate = useNavigate();
  const { slug } = useTenant();

  const residentesQuery = useQuery({
    queryKey: ["residents", "todos"],
    queryFn: () => residentService.listar({ limit: 200 }),
  });
  const vehiculosQuery = useQuery({
    queryKey: ["vehicles", "todos"],
    queryFn: () => vehicleService.listar({ limit: 200 }),
  });
  const torresQuery = useQuery({
    queryKey: ["towers"],
    queryFn: () => towerService.listar({ limit: 500 }),
  });
  const apartamentosQuery = useQuery({
    queryKey: ["apartments", "todos"],
    queryFn: () => apartmentService.listar({ limit: 500 }),
  });

  const cargando =
    residentesQuery.isLoading ||
    vehiculosQuery.isLoading ||
    torresQuery.isLoading ||
    apartamentosQuery.isLoading;

  const residentes = residentesQuery.data ?? [];
  const vehiculos = vehiculosQuery.data ?? [];
  const torres = torresQuery.data ?? [];
  const apartamentos = apartamentosQuery.data ?? [];

  const totalCarros = vehiculos.filter((v) => v.tipo_vehiculo.codigo === "CARRO").length;
  const totalMotos = vehiculos.filter((v) => v.tipo_vehiculo.codigo === "MOTO").length;
  const totalPropietarios = residentes.filter(
    (r) => r.tipo_residente.codigo === "PROPIETARIO",
  ).length;
  const totalArrendatarios = residentes.filter(
    (r) => r.tipo_residente.codigo === "ARRENDATARIO",
  ).length;

  const irA = (ruta: string) => navigate(`/${slug}/admin/${ruta}`);

  const estadisticas = [
    {
      label: "Residentes",
      valor: residentes.length,
      icon: UserSquare2,
      ruta: "residents",
    },
    {
      label: "Vehículos totales",
      valor: vehiculos.length,
      icon: Users,
      ruta: "vehicles",
    },
    { label: "Carros", valor: totalCarros, icon: Car, ruta: "vehicles" },
    { label: "Motos", valor: totalMotos, icon: Bike, ruta: "vehicles" },
  ];

  // Vehículos por torre: apartamento -> torre, residente -> apartamento, vehículo -> residente.
  const torreDeApartamento = new Map(apartamentos.map((a) => [a.id, a.torre_id]));
  const torreDeResidente = new Map(
    residentes.map((r) => [r.id, torreDeApartamento.get(r.apartamento_id)]),
  );
  const conteoPorTorre = new Map<number, number>();
  for (const vehiculo of vehiculos) {
    const torreId = torreDeResidente.get(vehiculo.residente_id);
    if (torreId == null) continue;
    conteoPorTorre.set(torreId, (conteoPorTorre.get(torreId) ?? 0) + 1);
  }
  const datosPorTorre = torres
    .map((t) => ({ torre: t.nombre, vehiculos: conteoPorTorre.get(t.id) ?? 0 }))
    .sort((a, b) => b.vehiculos - a.vehiculos);
  const TOP_TORRES = 10;
  const datosPorTorreVisibles = datosPorTorre.slice(0, TOP_TORRES);
  const torresOcultas = datosPorTorre.length - datosPorTorreVisibles.length;

  return (
    <div>
      <h1 className="text-2xl font-bold tracking-tight">Panel general</h1>
      <p className="mt-1 text-muted-foreground">Resumen del conjunto residencial</p>

      {cargando ? (
        <div className="flex justify-center py-16">
          <Spinner className="h-8 w-8" />
        </div>
      ) : (
        <>
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {estadisticas.map((stat, i) => (
              <motion.button
                key={stat.label}
                type="button"
                onClick={() => irA(stat.ruta)}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                whileHover={{ y: -3 }}
                className="text-left"
              >
                <Card className="cursor-pointer transition-shadow hover:shadow-md hover:ring-1 hover:ring-primary/30">
                  <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      {stat.label}
                    </CardTitle>
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                      <stat.icon className="h-4 w-4 text-primary" />
                    </span>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold">{stat.valor}</p>
                  </CardContent>
                </Card>
              </motion.button>
            ))}
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.24 }}>
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Vehículos por tipo</CardTitle>
                </CardHeader>
                <CardContent>
                  <BarraApilada
                    segmentos={[
                      { etiqueta: "Carro", valor: totalCarros, color: SERIE_1 },
                      { etiqueta: "Moto", valor: totalMotos, color: SERIE_2 },
                    ]}
                  />
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Residentes por tipo</CardTitle>
                </CardHeader>
                <CardContent>
                  <BarraApilada
                    segmentos={[
                      { etiqueta: "Propietario", valor: totalPropietarios, color: SERIE_1 },
                      { etiqueta: "Arrendatario", valor: totalArrendatarios, color: SERIE_2 },
                    ]}
                  />
                </CardContent>
              </Card>
            </motion.div>
          </div>

          <motion.div
            className="mt-4"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.36 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Building2 className="h-4 w-4" /> Vehículos por torre
                </CardTitle>
              </CardHeader>
              <CardContent>
                {datosPorTorreVisibles.length === 0 || datosPorTorreVisibles.every((d) => d.vehiculos === 0) ? (
                  <p className="py-10 text-center text-sm text-muted-foreground">
                    Aún no hay vehículos registrados en ninguna torre
                  </p>
                ) : (
                  <>
                    <div className="h-72 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={datosPorTorreVisibles} margin={{ top: 16, right: 8, left: 0, bottom: 0 }}>
                          <CartesianGrid vertical={false} stroke="hsl(var(--border))" />
                          <XAxis
                            dataKey="torre"
                            tickLine={false}
                            axisLine={{ stroke: "hsl(var(--border))" }}
                            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                          />
                          <YAxis
                            allowDecimals={false}
                            tickLine={false}
                            axisLine={false}
                            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                            width={28}
                          />
                          <Tooltip
                            cursor={{ fill: "hsl(var(--secondary))" }}
                            contentStyle={{
                              backgroundColor: "hsl(var(--card))",
                              borderColor: "hsl(var(--border))",
                              borderRadius: 8,
                              fontSize: 13,
                            }}
                            labelStyle={{ color: "hsl(var(--foreground))", fontWeight: 600 }}
                            formatter={(value) => [value, "Vehículos"]}
                          />
                          <Bar dataKey="vehiculos" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} maxBarSize={40}>
                            <LabelList
                              dataKey="vehiculos"
                              position="top"
                              style={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                            />
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                    {torresOcultas > 0 && (
                      <p className="mt-2 text-xs text-muted-foreground">
                        +{torresOcultas} torre(s) más, no mostradas por espacio
                      </p>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </>
      )}
    </div>
  );
}

function BarraApilada({
  segmentos,
}: {
  segmentos: { etiqueta: string; valor: number; color: string }[];
}) {
  const total = segmentos.reduce((acc, s) => acc + s.valor, 0);

  return (
    <div>
      <div className="flex h-6 w-full gap-[2px] overflow-hidden rounded-full bg-secondary/50">
        {total === 0
          ? null
          : segmentos.map((s) => {
              const porcentaje = (s.valor / total) * 100;
              if (porcentaje <= 0) return null;
              return (
                <div
                  key={s.etiqueta}
                  style={{ width: `${porcentaje}%`, backgroundColor: s.color }}
                  title={`${s.etiqueta}: ${s.valor}`}
                />
              );
            })}
      </div>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2">
        {segmentos.map((s) => (
          <div key={s.etiqueta} className="flex items-center gap-1.5 text-sm">
            <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: s.color }} />
            <span className="text-muted-foreground">{s.etiqueta}</span>
            <span className="font-semibold">{s.valor}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
