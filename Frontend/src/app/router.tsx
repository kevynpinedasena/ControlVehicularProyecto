import { Navigate, createBrowserRouter } from "react-router-dom";

import { LoginPage } from "@/features/auth/login-page";
import { ProtectedRoute } from "@/features/auth/protected-route";
import { BulkImportPage } from "@/features/import/bulk-import-page";
import { LocationsPage } from "@/features/locations/locations-page";
import { ParkingPage } from "@/features/parking/parking-page";
import { PlatformLoginPage } from "@/features/platform/platform-login-page";
import { BusinessUnitsPage } from "@/features/platform/business-units-page";
import { PlateSearchPage } from "@/features/plate-search/plate-search-page";
import { ResidentsPage } from "@/features/residents/residents-page";
import { SelectBusinessUnitPage } from "@/features/tenant/select-business-unit-page";
import { TenantLayout } from "@/features/tenant/tenant-layout";
import { TenantProtectedRoute } from "@/features/tenant/tenant-protected-route";
import { UsersPage } from "@/features/users/users-page";
import { VehiclesPage } from "@/features/vehicles/vehicles-page";
import { AdminLayout } from "@/layouts/admin-layout";
import { PlatformLayout } from "@/layouts/platform-layout";
import { VigilanteLayout } from "@/layouts/vigilante-layout";
import { DashboardPage } from "@/pages/dashboard-page";

export const router = createBrowserRouter([
  { path: "/", element: <SelectBusinessUnitPage /> },
  { path: "/plataforma/login", element: <PlatformLoginPage /> },
  {
    path: "/plataforma",
    element: <ProtectedRoute rolesPermitidos={["ADMIN_PLATAFORMA"]} redirigirLoginA="/plataforma/login" redirigirSinPermisoA="/" />,
    children: [
      {
        element: <PlatformLayout />,
        children: [{ path: "business-units", element: <BusinessUnitsPage /> }],
      },
    ],
  },
  {
    path: "/:slug",
    element: <TenantLayout />,
    children: [
      { index: true, element: <Navigate to="login" replace /> },
      { path: "login", element: <LoginPage /> },
      {
        element: <TenantProtectedRoute rolesPermitidos={["SUPER_ADMIN", "VIGILANTE"]} />,
        children: [
          {
            element: <VigilanteLayout />,
            children: [
              { path: "consulta-placa", element: <PlateSearchPage /> },
              { path: "residents", element: <ResidentsPage /> },
            ],
          },
        ],
      },
      {
        element: <TenantProtectedRoute rolesPermitidos={["SUPER_ADMIN"]} />,
        children: [
          {
            path: "admin",
            element: <AdminLayout />,
            children: [
              { path: "dashboard", element: <DashboardPage /> },
              { path: "residents", element: <ResidentsPage /> },
              { path: "vehicles", element: <VehiclesPage /> },
              { path: "locations", element: <LocationsPage /> },
              { path: "parking", element: <ParkingPage /> },
              { path: "users", element: <UsersPage /> },
              { path: "import", element: <BulkImportPage /> },
            ],
          },
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);
