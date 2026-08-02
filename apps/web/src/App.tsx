// apps/web/src/App.tsx
import { lazy, Suspense, Component, useEffect, type ReactNode, type ErrorInfo } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { LanguageProvider } from "./components/eco/i18n";
import Layout from "./components/Layout/Layout";
import { AdminShell } from "./features/admin/AdminShell";

const HomePage = lazy(() => import("./pages/HomePage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));
const AlertsPage = lazy(() => import("./pages/AlertsPage"));
const CommunityPage = lazy(() => import("./pages/CommunityPage"));
const EcocoinPage = lazy(() => import("./pages/EcocoinPage"));
const EcoCoinStakingPage = lazy(() => import("./pages/EcoCoinStakingPage"));
const EcoCoinMiningPage = lazy(() => import("./pages/EcoCoinMiningPage"));
const EcoCoinBioeconomyPage = lazy(() => import("./pages/EcoCoinBioeconomyPage"));
const EcoCoinChallengesPage = lazy(() => import("./pages/EcoCoinChallengesPage"));
const EcoCoinClaimPage = lazy(() => import("./pages/EcoCoinClaimPage"));
const EcoCoinClaimsListPage = lazy(() => import("./pages/EcoCoinClaimsListPage"));
const EcoCoinTransparencyPage = lazy(() => import("./pages/EcoCoinTransparencyPage"));
const EcoCoinDashboard = lazy(() => import("./pages/EcoCoinDashboard"));
const GamesPage = lazy(() => import("./pages/GamesPage"));
const LibraryPage = lazy(() => import("./pages/LibraryPage"));
const MrvPage = lazy(() => import("./pages/MrvPage"));
const MrvLevelsPage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvLevelsPage })));
const MrvEvidencePage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvEvidencePage })));
const MrvVerifyPage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvVerifyPage })));
const MrvSatellitesPage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvSatellitesPage })));
const MrvPointsPage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvPointsPage })));
const MrvClaimPage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvClaimPage })));
const MrvMethodologyPage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvMethodologyPage })));
const MrvLedgerPage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvLedgerPage })));
const MrvCalculatorPage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvCalculatorPage })));
const MrvBufferPage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvBufferPage })));
const MrvFarmLinkPage = lazy(() => import("./pages/MrvHubPages").then((m) => ({ default: m.MrvFarmLinkPage })));
const NewsPage = lazy(() => import("./pages/NewsPage"));
const PilotsPage = lazy(() => import("./pages/PilotsPage"));
const PilotNdviPage = lazy(() => import("./pages/PilotNdviPage"));
const RegionalPage = lazy(() => import("./pages/RegionalPage"));
const SatelliteDashboardPage = lazy(() => import("./pages/SatelliteDashboardPage"));
const SatelliteTimeseriesPage = lazy(() => import("./pages/SatelliteTimeseriesPage"));
const SatelliteChangePage = lazy(() => import("./pages/SatelliteChangePage"));
const SatelliteFieldMapPage = lazy(() => import("./pages/SatelliteFieldMapPage"));
const SimulatorsPage = lazy(() => import("./pages/SimulatorsPage"));
const AquaCropRunPage = lazy(() => import("./pages/AquaCropRunPage"));
const RothCRunPage = lazy(() => import("./pages/RothCRunPage"));
const SciencePage = lazy(() => import("./pages/SciencePage"));
const ScienceE2EPage = lazy(() => import("./pages/ScienceE2EPage"));
const FreeStackPage = lazy(() => import("./pages/FreeStackPage"));
const HydromaHubPage = lazy(() => import("./pages/HydromaHubPage"));
const DaneshYarPage = lazy(() => import("./pages/DaneshYarPage"));
const TasmimYarPage = lazy(() => import("./pages/TasmimYarPage"));
const BioFertilizerPage = lazy(() => import("./pages/BioFertilizerPage"));
const WatershedPage = lazy(() => import("./pages/WatershedPage"));
const RangelandPage = lazy(() => import("./pages/RangelandPage"));
const EconomicsPage = lazy(() => import("./pages/EconomicsPage"));
const SiteMapPage = lazy(() => import("./pages/SiteMapPage"));
const HubPage = lazy(() => import("./pages/hub/HubPage"));
const TourismPage = lazy(() => import("./pages/TourismPage"));
const UsersPage = lazy(() => import("./pages/UsersPage"));
const AccountingPage = lazy(() => import("./pages/AccountingPage"));
const AccountPage = lazy(() => import("./pages/AccountPage"));
const InvoicesPage = lazy(() => import("./pages/InvoicesPage"));
const JournalEntriesPage = lazy(() => import("./pages/JournalEntriesPage"));
const PaymentsPage = lazy(() => import("./pages/PaymentsPage"));
const PaymentSuccessPage = lazy(() => import("./pages/PaymentSuccessPage"));
const PaymentCancelPage = lazy(() => import("./pages/PaymentCancelPage"));
const EducationPage = lazy(() => import("./pages/EducationPage"));
const EducationMethodPage = lazy(() => import("./pages/EducationMethodPage"));
const AnalyticsPage = lazy(() => import("./pages/AnalyticsPage"));
const ReportsPage = lazy(() => import("./pages/ReportsPage"));
const RisksPage = lazy(() => import("./pages/RisksPage"));
const PoliciesPage = lazy(() => import("./pages/PoliciesPage"));
const SimulatorDetailPage = lazy(() => import("./pages/SimulatorDetailPage"));
const MySimulationsPage = lazy(() => import("./pages/MySimulationsPage"));
const ComparisonDashboard = lazy(() => import("./pages/ComparisonDashboard"));
const LoginPage = lazy(() => import("./pages/LoginPage"));
const RegisterPage = lazy(() => import("./pages/RegisterPage"));
const ForgotPasswordPage = lazy(() => import("./pages/ForgotPasswordPage"));
const VerifyOtpPage = lazy(() => import("./pages/VerifyOtpPage"));
const FarmsPage = lazy(() => import("./pages/FarmsPage"));
const FarmNewPage = lazy(() => import("./pages/FarmNewPage"));
const FarmDetailPage = lazy(() => import("./pages/FarmDetailPage"));
const FarmWizardPage = lazy(() => import("./pages/FarmWizardPage"));
const FarmRegisterPage = lazy(() => import("./pages/FarmRegisterPage"));
const FarmFieldsPage = lazy(() => import("./pages/FarmSubPages").then((m) => ({ default: m.FarmFieldsPage })));
const FarmLivestockPage = lazy(() => import("./pages/FarmSubPages").then((m) => ({ default: m.FarmLivestockPage })));
const FarmCropsPage = lazy(() => import("./pages/FarmSubPages").then((m) => ({ default: m.FarmCropsPage })));
const FarmTasksPage = lazy(() => import("./pages/FarmSubPages").then((m) => ({ default: m.FarmTasksPage })));
const FarmInputsPage = lazy(() => import("./pages/FarmSubPages").then((m) => ({ default: m.FarmInputsPage })));
const FarmTeamPage = lazy(() => import("./pages/FarmSubPages").then((m) => ({ default: m.FarmTeamPage })));
const FarmSustainabilityPage = lazy(() => import("./pages/FarmSubPages").then((m) => ({ default: m.FarmSustainabilityPage })));
const FarmMonitoringPage = lazy(() => import("./pages/FarmSubPages").then((m) => ({ default: m.FarmMonitoringPage })));
const FarmsMapPage = lazy(() => import("./pages/FarmMapPage"));
const FarmsPolicyPage = lazy(() => import("./pages/FarmSubPages").then((m) => ({ default: m.FarmsPolicyPage })));
const CropsPage = lazy(() => import("./pages/CropsPage"));
const CropDetailPage = lazy(() => import("./pages/CropDetailPage"));
const WaterPage = lazy(() => import("./pages/WaterPage"));
const WaterIrrigationPage = lazy(() => import("./pages/WaterIrrigationPage"));
const PlantingCalendarPage = lazy(() => import("./pages/PlantingCalendarPage"));
const TasksPage = lazy(() => import("./pages/TasksPage"));
const InventoryPage = lazy(() => import("./pages/InventoryPage"));
const CurrencySettingsPage = lazy(() => import("./pages/CurrencySettingsPage"));
const WeatherPage = lazy(() => import("./pages/WeatherPage"));
const MonitoringHubPage = lazy(() => import("./pages/MonitoringHubPage"));
const MonitoringSoilPage = lazy(() => import("./pages/MonitoringSoilPage"));
const MonitoringWeatherPage = lazy(() => import("./pages/MonitoringWeatherPage"));
const MonitoringMapPage = lazy(() => import("./pages/MonitoringMapPage"));
const MonitoringAlertsPage = lazy(() => import("./pages/MonitoringAlertsPage"));
const MonitoringRulesPage = lazy(() => import("./pages/MonitoringRulesPage"));
const AccountSecurityPage = lazy(() => import("./pages/AccountSecurityPage"));
const AccountNotificationsPage = lazy(() => import("./pages/AccountNotificationsPage"));
const AdminOverviewPage = lazy(() => import("./pages/admin/AdminOverviewPage"));
const AdminUsersPage = lazy(() => import("./pages/admin/AdminUsersPage"));
const AdminModulesPage = lazy(() => import("./pages/admin/AdminModulesPage"));
const AdminHealthPage = lazy(() => import("./pages/admin/AdminHealthPage"));
const AdminSettingsPage = lazy(() => import("./pages/admin/AdminSettingsPage"));

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "instant" as ScrollBehavior });
  }, [pathname]);
  return null;
}

function PageLoader() {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-stone-200 border-t-emerald-600" />
    </div>
  );
}

interface EBProps {
  children: ReactNode;
}
interface EBState {
  hasError: boolean;
  message: string;
}

class ErrorBoundary extends Component<EBProps, EBState> {
  constructor(props: EBProps) {
    super(props);
    this.state = { hasError: false, message: "" };
  }
  static getDerivedStateFromError(error: Error): EBState {
    return { hasError: true, message: error?.message || String(error) };
  }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("[App ErrorBoundary]", error, info?.componentStack);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 p-8 text-center">
          <p className="font-display text-2xl text-stone-800">Something went wrong</p>
          <p className="max-w-lg text-sm text-stone-600">{this.state.message}</p>
          <div className="flex gap-3">
            <button type="button" onClick={() => this.setState({ hasError: false, message: "" })} className="rounded-xl border border-stone-300 px-6 py-2.5 text-sm font-bold">Try again</button>
            <button type="button" onClick={() => window.location.assign("/sitemap")} className="rounded-xl bg-emerald-600 px-6 py-2.5 text-sm font-bold text-white">Site map</button>
            <button type="button" onClick={() => window.location.reload()} className="rounded-xl bg-stone-800 px-6 py-2.5 text-sm font-bold text-white">Reload</button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  return (
    <LanguageProvider>
      <ScrollToTop />
      <ErrorBoundary>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            <Route path="forgot-password" element={<ForgotPasswordPage />} />
            <Route path="verify-otp" element={<VerifyOtpPage />} />
            <Route path="admin" element={<AdminShell />}>
              <Route index element={<AdminOverviewPage />} />
              <Route path="users" element={<AdminUsersPage />} />
              <Route path="modules" element={<AdminModulesPage />} />
              <Route path="health" element={<AdminHealthPage />} />
              <Route path="settings" element={<AdminSettingsPage />} />
            </Route>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="sitemap" element={<SiteMapPage />} />
              <Route path="free-stack" element={<FreeStackPage />} />
              <Route path="hydroma" element={<HydromaHubPage />} />
              <Route path="danesh-yar" element={<DaneshYarPage />} />
              <Route path="tasmim-yar" element={<TasmimYarPage />} />
              <Route path="bio-fertilizer" element={<BioFertilizerPage />} />
              <Route path="watershed" element={<WatershedPage />} />
              <Route path="rangeland" element={<RangelandPage />} />
              <Route path="economics" element={<EconomicsPage />} />
              <Route path="hub/:slug" element={<HubPage />} />
              <Route path="farms" element={<FarmsPage />} />
              <Route path="farms/new" element={<FarmNewPage />} />
              <Route path="farms/wizard" element={<FarmWizardPage />} />
              <Route path="farms/register" element={<FarmRegisterPage />} />
              <Route path="farms/map" element={<FarmsMapPage />} />
              <Route path="farms/policy" element={<FarmsPolicyPage />} />
              <Route path="farms/:id/fields" element={<FarmFieldsPage />} />
              <Route path="farms/:id/livestock" element={<FarmLivestockPage />} />
              <Route path="farms/:id/crops" element={<FarmCropsPage />} />
              <Route path="farms/:id/tasks" element={<FarmTasksPage />} />
              <Route path="farms/:id/inputs" element={<FarmInputsPage />} />
              <Route path="farms/:id/team" element={<FarmTeamPage />} />
              <Route path="farms/:id/sustainability" element={<FarmSustainabilityPage />} />
              <Route path="farms/:id/monitoring" element={<FarmMonitoringPage />} />
              <Route path="farms/:id" element={<FarmDetailPage />} />
              <Route path="crops" element={<CropsPage />} />
              <Route path="crops/:id" element={<CropDetailPage />} />
              <Route path="water" element={<WaterPage />} />
              <Route path="water/irrigation" element={<WaterIrrigationPage />} />
              <Route path="planting" element={<PlantingCalendarPage />} />
              <Route path="tasks" element={<TasksPage />} />
              <Route path="inventory" element={<InventoryPage />} />
              <Route path="currency" element={<CurrencySettingsPage />} />
              <Route path="weather" element={<WeatherPage />} />
              <Route path="monitoring" element={<MonitoringHubPage />} />
              <Route path="monitoring/soil" element={<MonitoringSoilPage />} />
              <Route path="monitoring/weather" element={<MonitoringWeatherPage />} />
              <Route path="monitoring/map" element={<MonitoringMapPage />} />
              <Route path="monitoring/alerts" element={<MonitoringAlertsPage />} />
              <Route path="monitoring/rules" element={<MonitoringRulesPage />} />
              <Route path="account" element={<AccountPage />} />
              <Route path="account/security" element={<AccountSecurityPage />} />
              <Route path="account/notifications" element={<AccountNotificationsPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="alerts" element={<AlertsPage />} />
              <Route path="community" element={<CommunityPage />} />
              <Route path="ecocoin" element={<EcocoinPage />} />
              <Route path="ecocoin/dashboard" element={<EcoCoinDashboard />} />
              <Route path="ecocoin/staking" element={<EcoCoinStakingPage />} />
              <Route path="ecocoin/mining" element={<EcoCoinMiningPage />} />
              <Route path="ecocoin/bioeconomy" element={<EcoCoinBioeconomyPage />} />
              <Route path="ecocoin/challenges" element={<EcoCoinChallengesPage />} />
              <Route path="ecocoin/claim" element={<EcoCoinClaimPage />} />
              <Route path="ecocoin/claims" element={<EcoCoinClaimsListPage />} />
              <Route path="ecocoin/transparency" element={<EcoCoinTransparencyPage />} />
              <Route path="games" element={<GamesPage />} />
              <Route path="library" element={<LibraryPage />} />
              <Route path="mrv" element={<MrvPage />} />
              <Route path="mrv/levels" element={<MrvLevelsPage />} />
              <Route path="mrv/evidence" element={<MrvEvidencePage />} />
              <Route path="mrv/verify" element={<MrvVerifyPage />} />
              <Route path="mrv/satellites" element={<MrvSatellitesPage />} />
              <Route path="mrv/points" element={<MrvPointsPage />} />
              <Route path="mrv/claim" element={<MrvClaimPage />} />
              <Route path="mrv/methodology" element={<MrvMethodologyPage />} />
              <Route path="mrv/ledger" element={<MrvLedgerPage />} />
              <Route path="mrv/calculator" element={<MrvCalculatorPage />} />
              <Route path="mrv/buffer" element={<MrvBufferPage />} />
              <Route path="mrv/farm-link" element={<MrvFarmLinkPage />} />
              <Route path="news" element={<NewsPage />} />
              <Route path="pilots" element={<PilotsPage />} />
              <Route path="pilots/ndvi" element={<PilotNdviPage />} />
              <Route path="regional" element={<RegionalPage />} />
              <Route path="satellite" element={<SatelliteDashboardPage />} />
              <Route path="satellite/timeseries" element={<SatelliteTimeseriesPage />} />
              <Route path="satellite/change" element={<SatelliteChangePage />} />
              <Route path="satellite/fields" element={<SatelliteFieldMapPage />} />
              <Route path="simulators" element={<SimulatorsPage />} />
              <Route path="simulators/aquacrop" element={<AquaCropRunPage />} />
              <Route path="simulators/rothc" element={<RothCRunPage />} />
              <Route path="science" element={<SciencePage />} />
              <Route path="science/e2e" element={<ScienceE2EPage />} />
              <Route path="simulators/:id" element={<SimulatorDetailPage />} />
              <Route path="my-simulations" element={<MySimulationsPage />} />
              <Route path="comparison" element={<ComparisonDashboard />} />
              <Route path="tourism" element={<TourismPage />} />
              <Route path="users" element={<UsersPage />} />
              <Route path="accounting" element={<AccountingPage />} />
              <Route path="invoices" element={<InvoicesPage />} />
              <Route path="journal" element={<JournalEntriesPage />} />
              <Route path="payments" element={<PaymentsPage />} />
              <Route path="payments/success" element={<PaymentSuccessPage />} />
              <Route path="payments/cancel" element={<PaymentCancelPage />} />
              <Route path="education" element={<EducationPage />} />
              <Route path="education/methods" element={<EducationMethodPage />} />
              <Route path="education/methods/:slug" element={<EducationMethodPage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="risks" element={<RisksPage />} />
              <Route path="policies" element={<PoliciesPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </LanguageProvider>
  );
}
